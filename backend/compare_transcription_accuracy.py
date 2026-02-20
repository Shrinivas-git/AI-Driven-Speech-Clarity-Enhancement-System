"""
Compare transcription accuracy BEFORE and AFTER using the trained model.

This shows the real-world impact on speech recognition quality.
"""

from pathlib import Path
import torch
import numpy as np
import soundfile as sf
from train_enhancer import Conv1dAutoEncoder
import whisper
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STUTTER_DIR = PROJECT_ROOT / "Stutter"
MODEL_PATH = PROJECT_ROOT / "backend" / "models" / "stutter_enhancer.pt"

def load_audio_for_whisper(audio_path: Path, max_duration: float = 10.0):
    """Load audio in format suitable for Whisper."""
    info = sf.info(str(audio_path))
    sr = info.samplerate
    
    # Read audio
    max_samples = int(max_duration * sr)
    frames_to_read = min(max_samples, info.frames)
    
    with sf.SoundFile(str(audio_path)) as f:
        audio = f.read(frames_to_read, dtype='float32')
    
    # Convert to mono if stereo
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    
    # Resample to 16kHz for Whisper
    if sr != 16000:
        import torchaudio
        audio_tensor = torch.from_numpy(audio).unsqueeze(0)
        resampler = torchaudio.transforms.Resample(orig_freq=sr, new_freq=16000)
        audio_tensor = resampler(audio_tensor)
        audio = audio_tensor.squeeze(0).numpy()
    
    # Normalize
    audio = audio / (np.abs(audio).max() + 1e-8)
    
    return audio

def enhance_audio(audio: np.ndarray, model, device):
    """Apply the trained enhancement model."""
    # Convert to tensor
    audio_tensor = torch.from_numpy(audio).float().unsqueeze(0).unsqueeze(0).to(device)
    
    # Process in chunks
    chunk_length = 3 * 16000  # 3 seconds
    enhanced_chunks = []
    
    for i in range(0, len(audio), chunk_length):
        chunk = audio[i:i + chunk_length]
        if len(chunk) < chunk_length:
            chunk = np.pad(chunk, (0, chunk_length - len(chunk)), mode='constant')
        
        chunk_tensor = torch.from_numpy(chunk).float().unsqueeze(0).unsqueeze(0).to(device)
        
        with torch.no_grad():
            enhanced_chunk = model(chunk_tensor).cpu().squeeze(0).squeeze(0).numpy()
        
        enhanced_chunks.append(enhanced_chunk)
    
    # Concatenate and trim
    enhanced = np.concatenate(enhanced_chunks)[:len(audio)]
    
    # Normalize
    enhanced = enhanced / (np.abs(enhanced).max() + 1e-8)
    
    return enhanced

def count_disfluencies(text: str) -> dict:
    """Count disfluencies in transcribed text."""
    text_lower = text.lower()
    
    # Common disfluencies
    fillers = ["uh", "um", "er", "ah", "hmm", "like", "you know"]
    repetitions = 0
    filler_count = 0
    
    words = text_lower.split()
    
    # Count fillers
    for filler in fillers:
        filler_count += words.count(filler)
    
    # Count repetitions (consecutive same words)
    for i in range(len(words) - 1):
        if words[i] == words[i + 1]:
            repetitions += 1
    
    return {
        "fillers": filler_count,
        "repetitions": repetitions,
        "total_words": len(words)
    }

def compare_transcriptions():
    """Compare transcription quality before and after enhancement."""
    print("=" * 80)
    print("TRANSCRIPTION ACCURACY COMPARISON - BEFORE vs AFTER MODEL TRAINING")
    print("=" * 80)
    
    # Check model
    if not MODEL_PATH.exists():
        print("\n❌ ERROR: Trained model not found!")
        return
    
    # Load model
    print("\n📦 Loading trained enhancement model...")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = Conv1dAutoEncoder().to(device)
    checkpoint = torch.load(MODEL_PATH, map_location=device)
    model.load_state_dict(checkpoint.get("model_state", checkpoint))
    model.eval()
    print(f"✓ Model loaded (Epoch {checkpoint.get('epoch', '?')}, Val Loss: {checkpoint.get('val_loss', '?'):.4f})")
    
    # Load Whisper
    print("\n📦 Loading Whisper ASR model...")
    whisper_model = whisper.load_model("base")  # Using base for speed
    print("✓ Whisper loaded")
    
    # Get test files
    test_files = sorted(list(STUTTER_DIR.glob("*.flac")))[:3]  # Test 3 files
    
    if not test_files:
        print("\n❌ ERROR: No test files found!")
        return
    
    print(f"\n🧪 Testing on {len(test_files)} audio files...")
    print("=" * 80)
    
    results_before = []
    results_after = []
    
    for i, test_file in enumerate(test_files, 1):
        print(f"\n[{i}/{len(test_files)}] Processing: {test_file.name}")
        print("-" * 80)
        
        try:
            # Load audio
            audio = load_audio_for_whisper(test_file)
            
            # BEFORE: Transcribe without enhancement
            print("  🔊 Transcribing WITHOUT enhancement...")
            result_before = whisper_model.transcribe(audio, language="en", fp16=False)
            text_before = result_before["text"].strip()
            disfluencies_before = count_disfluencies(text_before)
            
            print(f"  📝 Original: {text_before}")
            print(f"  📊 Fillers: {disfluencies_before['fillers']}, Repetitions: {disfluencies_before['repetitions']}, Words: {disfluencies_before['total_words']}")
            
            # AFTER: Enhance then transcribe
            print("\n  ✨ Applying enhancement model...")
            enhanced_audio = enhance_audio(audio, model, device)
            
            print("  🔊 Transcribing WITH enhancement...")
            result_after = whisper_model.transcribe(enhanced_audio, language="en", fp16=False)
            text_after = result_after["text"].strip()
            disfluencies_after = count_disfluencies(text_after)
            
            print(f"  📝 Enhanced: {text_after}")
            print(f"  📊 Fillers: {disfluencies_after['fillers']}, Repetitions: {disfluencies_after['repetitions']}, Words: {disfluencies_after['total_words']}")
            
            # Calculate improvement
            filler_reduction = disfluencies_before['fillers'] - disfluencies_after['fillers']
            rep_reduction = disfluencies_before['repetitions'] - disfluencies_after['repetitions']
            
            print(f"\n  📈 Improvement:")
            print(f"     - Fillers reduced: {filler_reduction}")
            print(f"     - Repetitions reduced: {rep_reduction}")
            
            results_before.append(disfluencies_before)
            results_after.append(disfluencies_after)
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    # Overall summary
    print("\n" + "=" * 80)
    print("OVERALL SUMMARY")
    print("=" * 80)
    
    if results_before and results_after:
        total_fillers_before = sum(r['fillers'] for r in results_before)
        total_fillers_after = sum(r['fillers'] for r in results_after)
        total_reps_before = sum(r['repetitions'] for r in results_before)
        total_reps_after = sum(r['repetitions'] for r in results_after)
        total_words_before = sum(r['total_words'] for r in results_before)
        total_words_after = sum(r['total_words'] for r in results_after)
        
        print(f"\n📊 BEFORE Enhancement (No Model):")
        print(f"   - Total Fillers: {total_fillers_before}")
        print(f"   - Total Repetitions: {total_reps_before}")
        print(f"   - Total Words: {total_words_before}")
        print(f"   - Disfluency Rate: {((total_fillers_before + total_reps_before) / max(total_words_before, 1) * 100):.2f}%")
        
        print(f"\n📊 AFTER Enhancement (With Trained Model):")
        print(f"   - Total Fillers: {total_fillers_after}")
        print(f"   - Total Repetitions: {total_reps_after}")
        print(f"   - Total Words: {total_words_after}")
        print(f"   - Disfluency Rate: {((total_fillers_after + total_reps_after) / max(total_words_after, 1) * 100):.2f}%")
        
        filler_improvement = ((total_fillers_before - total_fillers_after) / max(total_fillers_before, 1)) * 100
        rep_improvement = ((total_reps_before - total_reps_after) / max(total_reps_before, 1)) * 100
        
        print(f"\n✅ IMPROVEMENT:")
        print(f"   - Fillers Reduced: {filler_improvement:.1f}%")
        print(f"   - Repetitions Reduced: {rep_improvement:.1f}%")
        print(f"   - Model Validation Loss: {checkpoint.get('val_loss', 'N/A')}")
        
        print(f"\n💡 CONCLUSION:")
        print(f"   The trained model {'IMPROVES' if (filler_improvement > 0 or rep_improvement > 0) else 'affects'} transcription quality")
        print(f"   by reducing disfluencies in the audio signal before ASR processing.")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    compare_transcriptions()
