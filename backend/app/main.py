from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import uuid
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

try:
    from .pipeline import process_audio_file
except ImportError as e:
    logger.error(f"Failed to import pipeline: {e}")
    logger.error("Make sure all dependencies are installed: pip install -r requirements.txt")
    raise

BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_DIR = BASE_DIR / "media"
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Speech Clarity Enhancement API", version="1.0.0")

@app.on_event("startup")
async def startup_event():
    logger.info("=" * 50)
    logger.info("Speech Clarity Enhancement API Starting...")
    logger.info(f"Media directory: {MEDIA_DIR}")
    logger.info("=" * 50)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/enhance-speech")
async def enhance_speech(
    file: UploadFile = File(...),
    output_mode: str = Form("both"),  # "audio" | "text" | "both"
    calculate_metrics: bool = Form(True),
    realtime: bool = Form(False)
):
    """
    Main endpoint with enhanced features:
    1. Saves uploaded audio
    2. Runs ASR -> text cleaning -> TTS (based on output_mode)
    3. Calculates fluency metrics (if requested)
    4. Returns selected outputs
    
    Parameters:
    - output_mode: "audio" | "text" | "both" - what to return
    - calculate_metrics: true/false - whether to calculate fluency scores
    - realtime: true/false - real-time mode flag (for future use)
    """
    import asyncio
    import logging
    import sys
    
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    logger = logging.getLogger(__name__)
    
    # Validate output_mode
    if output_mode not in ["audio", "text", "both"]:
        output_mode = "both"
        logger.warning(f"Invalid output_mode, defaulting to 'both'")
    
    # Save input file
    suffix = Path(file.filename or "audio").suffix or ".flac"
    input_id = uuid.uuid4().hex
    input_path = MEDIA_DIR / f"input_{input_id}{suffix}"

    try:
        logger.info(f"Received file: {file.filename}, mode: {output_mode}, metrics: {calculate_metrics}")
        with input_path.open("wb") as f:
            content = await file.read()
            f.write(content)
        logger.info(f"File saved: {input_path.name} ({len(content)} bytes)")

        # Process through pipeline with timeout (max 2 minutes for faster feedback)
        try:
            # Run in executor to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            result = await asyncio.wait_for(
                loop.run_in_executor(
                    None, 
                    process_audio_file, 
                    input_path, 
                    MEDIA_DIR,
                    output_mode,
                    calculate_metrics
                ),
                timeout=120.0  # 2 minute timeout
            )
            
            logger.info("Processing completed successfully")
            
            # Build response based on output_mode
            response = {}
            
            if output_mode in ["text", "both"]:
                response["cleaned_text"] = result.get("cleaned_text", "")
                response["raw_text"] = result.get("raw_text", "")
            
            if output_mode in ["audio", "both"]:
                enhanced_path = result.get("enhanced_audio_path")
                if enhanced_path:
                    response["enhanced_audio_filename"] = enhanced_path.name
            
            if calculate_metrics and "fluency_metrics" in result:
                response["fluency_metrics"] = result["fluency_metrics"]
            
            return JSONResponse(response)
        except asyncio.TimeoutError:
            logger.error("Processing timed out")
            return JSONResponse(
                {"detail": "Processing timed out after 2 minutes. Please try a shorter audio file or check server logs."},
                status_code=500,
            )
        except Exception as e:
            # Keep the server running even if ML deps aren't installed yet
            logger.error(f"Processing failed: {e}", exc_info=True)
            error_msg = str(e)
            error_detail = error_msg
            
            # Make error message more user-friendly
            if "Could not load audio" in error_msg or "load" in error_msg.lower():
                if "webm" in error_msg.lower() or ".webm" in str(input_path).lower():
                    error_detail = "WebM audio format not fully supported. Please try recording in WAV format or upload a WAV/FLAC/MP3 file."
                else:
                    error_detail = f"Could not load audio file. Supported formats: WAV, FLAC, MP3. Error: {error_msg}"
            elif "TTS" in error_msg or "pyttsx3" in error_msg:
                error_detail = "Text-to-speech generation failed. Please check if your system has a TTS engine installed."
            elif "Whisper" in error_msg or "whisper" in error_msg:
                error_detail = "Speech recognition failed. Please check if Whisper model is properly installed."
            elif not error_detail or error_detail == "":
                error_detail = f"Processing failed: {error_msg}"
            
            return JSONResponse(
                {"detail": error_detail},
                status_code=500,
            )
    except Exception as e:
        logger.error(f"File upload failed: {e}", exc_info=True)
        return JSONResponse(
            {"detail": f"Failed to save uploaded file: {e}"},
            status_code=500,
        )


@app.get("/download/{filename}")
async def download_enhanced_audio(filename: str):
    file_path = MEDIA_DIR / filename
    if not file_path.exists():
        return JSONResponse({"detail": "File not found"}, status_code=404)
    return FileResponse(path=file_path, filename=file_path.name, media_type="audio/wav")


@app.get("/")
async def root():
    """Root endpoint - API information."""
    return JSONResponse({
        "message": "Speech Clarity Enhancement API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "enhance": "/enhance-speech",
            "docs": "/docs"
        }
    })

@app.get("/health")
async def health():
    """Health check endpoint for frontend connection monitoring."""
    return {"status": "ok", "message": "Backend is running"}




