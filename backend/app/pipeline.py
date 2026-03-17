"""
End-to-end ASR -> Text Cleaning -> TTS pipeline.

Important:
- Whisper is used for ASR (requires torch).
- For TTS we use a lightweight, offline engine (pyttsx3) instead of Coqui TTS
  to avoid heavy audio codec dependencies on Windows, while keeping the same
  ASR → cleaner → TTS architecture for your MCA project.
"""

from pathlib import Path
from typing import Tuple, Any

from .audio_utils import load_and_preprocess, TARGET_SR
from .text_cleaner import clean_stuttered_text

# Lazy singletons so models/engines are loaded only once
_whisper_model: Any | None = None
_tts_engine: Any | None = None
_enhancer_model: Any | None = None
_enhancer_device: Any | None = None


def _missing_dep(msg: str) -> RuntimeError:
    return RuntimeError(
        msg
        + " Install backend ML dependencies (torch, openai-whisper, pyttsx3) "
        + "and retry."
    )


def get_whisper_model() -> Any:
    """
    Load Whisper ASR model once and reuse it.
    """
    global _whisper_model
    if _whisper_model is None:
        try:
            import whisper  # type: ignore
        except Exception as e:
            raise _missing_dep(f"Whisper dependency not available: {e}")
<<<<<<< HEAD
        # Use 'small' for better accuracy while still being reasonably fast
        # 'base' is faster but less accurate; 'small' provides better transcription quality
        # For even better accuracy, use 'medium' but it's much slower on CPU
        _whisper_model = whisper.load_model("small")
=======
        # Use 'base' for faster processing; 'medium' is more accurate but much slower on CPU
        # For production, consider 'small' as a balance, or use GPU for 'medium'
        _whisper_model = whisper.load_model("base")
>>>>>>> 015c03c9e65da3a9fde160ed1e1b7b748a0ed461
    return _whisper_model


def get_enhancer_model() -> tuple[Any | None, Any | None]:
    """
    Load the learned stutter-to-clear enhancer model if available.

    If the model file is missing or cannot be loaded, this gracefully
    returns (None, None) and the pipeline falls back to the raw audio.
    """
    global _enhancer_model, _enhancer_device
    import logging
    import sys
    
    logger = logging.getLogger(__name__)

    if _enhancer_model is not None and _enhancer_device is not None:
        return _enhancer_model, _enhancer_device

    # Model definition + checkpoint live in backend/train_enhancer.py
    model_path = Path(__file__).resolve().parent.parent / "models" / "stutter_enhancer.pt"
    if not model_path.exists():
        # No trained model yet - skip enhancement silently
        logger.info("No enhancer model found, skipping audio enhancement")
        return None, None

    try:
        import torch  # type: ignore
        from ..train_enhancer import Conv1dAutoEncoder  # type: ignore
    except Exception as e:
        logger.warning(f"Could not import enhancer model: {e}. Skipping enhancement.")
        return None, None

    try:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = Conv1dAutoEncoder().to(device)

        checkpoint = torch.load(model_path, map_location=device)
        state_dict = checkpoint.get("model_state", checkpoint)
        model.load_state_dict(state_dict)
        model.eval()

        _enhancer_model = model
        _enhancer_device = device
        logger.info(f"Enhancer model loaded successfully on {device}")
        return _enhancer_model, _enhancer_device
    except Exception as e:
        logger.warning(f"Failed to load enhancer model: {e}. Skipping enhancement.")
        return None, None


def get_tts_engine() -> Any:
    """
    Create a NEW TTS engine instance for each request.
    pyttsx3 can get stuck if reused, so we create fresh instances.
    """
    try:
        import pyttsx3  # type: ignore
    except Exception as e:
        raise _missing_dep(f"pyttsx3 dependency not available: {e}")

    # Create a fresh engine for each request to avoid stuck state
    engine = pyttsx3.init()
    # Tune for clarity (you can adjust these in your experiments)
    engine.setProperty("rate", 180)   # speaking speed
    engine.setProperty("volume", 1.0)  # max volume
    return engine


def run_asr_on_waveform(audio_path: Path) -> str:
    """
    1. Load + preprocess the audio (mono, 16kHz, normalized)
    2. Run Whisper ASR
    3. Return raw transcript (which may include repetitions, fillers etc.)
    """
    import logging
    import sys
    import numpy as np
    
    logger = logging.getLogger(__name__)
    
    logger.info("Loading and preprocessing audio...")
    y, sr = load_and_preprocess(audio_path)
    logger.info(f"Audio loaded: {len(y)/sr:.2f} seconds at {sr}Hz")

    # Optional enhancement using learned model (process in chunks for efficiency)
    enhancer, device = get_enhancer_model()
    if enhancer is not None and device is not None:
        try:
            import torch  # type: ignore
            logger.info("Applying audio enhancement...")

            # Process in 3-second chunks to avoid memory issues and speed up processing
            chunk_length = 3 * sr  # 3 seconds at sample rate
            enhanced_chunks = []
            
            for i in range(0, len(y), chunk_length):
                chunk = y[i:i + chunk_length]
                if len(chunk) < chunk_length:
                    # Pad last chunk
                    chunk = np.pad(chunk, (0, chunk_length - len(chunk)), mode='constant')
                
                x = torch.from_numpy(chunk.astype(np.float32)).unsqueeze(0).unsqueeze(0).to(device)
                with torch.no_grad():
                    enhanced_chunk = enhancer(x).cpu().squeeze(0).squeeze(0).numpy()
                enhanced_chunks.append(enhanced_chunk)
            
            # Concatenate chunks and trim to original length
            enhanced = np.concatenate(enhanced_chunks)[:len(y)]
            
            # Simple renormalization
            peak = float(np.max(np.abs(enhanced)) or 1.0)
            y = enhanced / peak
            logger.info("Audio enhancement completed")
        except Exception as e:
            # If anything goes wrong, just fall back to original waveform
            logger.warning(f"Enhancement failed, using original audio: {e}")
            pass
    else:
        logger.info("Skipping enhancement (model not available)")

    logger.info("Loading Whisper model...")
    model = get_whisper_model()
    logger.info("Running Whisper transcription...")

    # Whisper expects 16kHz float32 numpy
    audio = y.astype(np.float32)
    # Use faster decoding options for speed
    result = model.transcribe(
        audio, 
        language="en",
        fp16=False,  # FP16 not supported on CPU anyway
        verbose=False,  # Don't print progress
        condition_on_previous_text=False,  # Faster, slightly less accurate
    )
    
    text = result.get("text", "").strip()
    logger.info(f"Transcription completed: {text[:100]}...")
    return text


def run_tts_on_text(text: str, out_dir: Path, prefix: str = "enhanced") -> Path:
    """
    Generate speech from cleaned text using pyttsx3.
    Creates a fresh engine instance for each request to avoid stuck state.
    """
    import logging
    import sys
    import time
    import threading
    import uuid
    
    logger = logging.getLogger(__name__)
    
    # Handle empty text
    if not text or not text.strip():
        text = "No speech detected."
    
    # Create a fresh TTS engine for each request
    tts = get_tts_engine()
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Use unique filename with timestamp to avoid conflicts
    unique_id = uuid.uuid4().hex[:8]
    out_path = out_dir / f"{prefix}_{unique_id}_{audio_safe_slug(text)[:20]}.wav"
    
    # Use threading with timeout to prevent hanging
    tts_error = [None]
    tts_completed = [False]
    
    def run_tts():
        try:
            logger.info(f"TTS: Saving to {out_path.name}")
            tts.save_to_file(text, str(out_path))
            logger.info("TTS: Starting synthesis...")
            tts.runAndWait()
            logger.info("TTS: Synthesis completed")
            tts_completed[0] = True
        except Exception as e:
            tts_error[0] = e
            logger.error(f"TTS error: {e}", exc_info=True)
        finally:
            # Try to stop the engine to free resources
            try:
                tts.stop()
            except:
                pass
    
    thread = threading.Thread(target=run_tts, daemon=True)
    thread.start()
    thread.join(timeout=60.0)  # 60 second timeout
    
    if thread.is_alive():
        logger.error("TTS timed out after 60 seconds")
        # Try to stop the engine
        try:
            tts.stop()
        except:
            pass
        raise RuntimeError("TTS generation timed out. The text may be too long or TTS engine is stuck.")
    
    if tts_error[0]:
        raise RuntimeError(f"TTS failed: {tts_error[0]}")
    
    if not tts_completed[0]:
        raise RuntimeError("TTS did not complete successfully")
    
    # Wait a bit to ensure file is written
    max_wait = 10
    waited = 0
    while not out_path.exists() and waited < max_wait:
        time.sleep(0.5)
        waited += 0.5
    
    if not out_path.exists():
        raise RuntimeError(f"TTS output file was not created: {out_path}")
    
    logger.info(f"TTS file created: {out_path.name} ({out_path.stat().st_size} bytes)")
    return out_path


def audio_safe_slug(text: str) -> str:
    """
    Make a filesystem-safe identifier from text (best-effort, short).
    """
    import re

    s = re.sub(r"[^a-zA-Z0-9]+", "_", (text or "speech").strip())
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "speech"


def process_audio_file(input_path: Path, out_dir: Path, 
                       output_mode: str = "both",
<<<<<<< HEAD
                       calculate_metrics: bool = True,
                       grammar_correction: bool = True) -> dict:
=======
                       calculate_metrics: bool = True) -> dict:
>>>>>>> 015c03c9e65da3a9fde160ed1e1b7b748a0ed461
    """
    Full pipeline used by the FastAPI endpoint.
    
    Args:
        input_path: Path to input audio file
        out_dir: Directory to save output files
        output_mode: "audio" | "text" | "both" - what to return
        calculate_metrics: Whether to calculate fluency metrics
<<<<<<< HEAD
        grammar_correction: Whether to apply grammar correction
=======
>>>>>>> 015c03c9e65da3a9fde160ed1e1b7b748a0ed461
    
    Returns:
        Dictionary with:
        - cleaned_text: (optional) Transcript after cleaning
        - enhanced_audio_path: (optional) Path to synthesized audio
        - raw_text: Original transcript from ASR
        - fluency_metrics: (optional) Before/after metrics
    """
    import logging
    import sys
    from .fluency_metrics import calculate_fluency_metrics
    from .audio_utils import load_and_preprocess
    
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    logger = logging.getLogger(__name__)
    
    result = {}
    
    try:
<<<<<<< HEAD
        logger.info(f"Starting processing for {input_path.name} (mode: {output_mode}, grammar: {grammar_correction})")
=======
        logger.info(f"Starting processing for {input_path.name} (mode: {output_mode})")
>>>>>>> 015c03c9e65da3a9fde160ed1e1b7b748a0ed461
        
        # Load raw audio for metrics calculation
        raw_audio, sample_rate = None, None
        if calculate_metrics:
            try:
                raw_audio, sample_rate = load_and_preprocess(input_path)
                logger.info("Raw audio loaded for metrics calculation")
            except Exception as e:
                logger.warning(f"Could not load audio for metrics: {e}")
        
        # 1. ASR
        logger.info("Step 1/3: Running ASR...")
        raw_text = run_asr_on_waveform(input_path)
        logger.info(f"ASR completed. Raw text: {raw_text[:100]}...")
        result["raw_text"] = raw_text

<<<<<<< HEAD
        # 2. Text cleaning (with optional grammar correction)
        logger.info(f"Step 2/3: Cleaning text (grammar correction: {grammar_correction})...")
        cleaned_text = clean_stuttered_text(raw_text, apply_grammar_correction=grammar_correction)
=======
        # 2. Text cleaning
        logger.info("Step 2/3: Cleaning text...")
        cleaned_text = clean_stuttered_text(raw_text)
>>>>>>> 015c03c9e65da3a9fde160ed1e1b7b748a0ed461
        logger.info(f"Text cleaned. Result: {cleaned_text[:100]}...")
        
        # Calculate metrics if requested
        fluency_metrics = None
        if calculate_metrics and raw_audio is not None:
            try:
                logger.info("Calculating fluency metrics...")
                fluency_metrics = calculate_fluency_metrics(
                    raw_text, cleaned_text, raw_audio, sample_rate
                )
                logger.info(f"Metrics calculated - Before: {fluency_metrics['before']['fluency_score']:.1f}%, After: {fluency_metrics['after']['fluency_score']:.1f}%")
                result["fluency_metrics"] = fluency_metrics
            except Exception as e:
                logger.warning(f"Metrics calculation failed: {e}")

        # 3. TTS (only if audio output is requested)
        if output_mode in ["audio", "both"]:
            logger.info("Step 3/3: Generating TTS...")
            enhanced_audio_path = run_tts_on_text(cleaned_text, out_dir=out_dir, prefix="enhanced")
            logger.info(f"TTS completed. Output: {enhanced_audio_path.name}")
            result["enhanced_audio_path"] = enhanced_audio_path
        
        # Add cleaned text if text output is requested
        if output_mode in ["text", "both"]:
            result["cleaned_text"] = cleaned_text

        return result
    except Exception as e:
        logger.error(f"Pipeline error: {e}", exc_info=True)
        raise




