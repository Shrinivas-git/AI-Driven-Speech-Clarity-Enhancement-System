<<<<<<< HEAD
"""
Speech Clarity Enhancement API - Production Version

This is the main FastAPI application with:
- Authentication and authorization
- Usage limits and subscription management
- Database integration
- User management
- Admin panel
- Preserved AI functionality
"""

from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, status, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
=======
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
>>>>>>> 015c03c9e65da3a9fde160ed1e1b7b748a0ed461
from pathlib import Path
import uuid
import sys
import logging
<<<<<<< HEAD
import time
from datetime import datetime
from typing import Optional
=======
>>>>>>> 015c03c9e65da3a9fde160ed1e1b7b748a0ed461

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

<<<<<<< HEAD
# Import database and models
from .database import get_database, init_database, check_database_connection
from .models import User, AudioHistory, FluencyScore, OutputMode, UserRole
from .auth import get_current_active_user, require_admin
from .usage_limits import get_usage_tracker, UsageLimitError
from .schemas import (
    AudioProcessResponse, UsageInfo, FluencyComparison, 
    FluencyMetrics, ErrorResponse
)

# Import existing pipeline
=======
>>>>>>> 015c03c9e65da3a9fde160ed1e1b7b748a0ed461
try:
    from .pipeline import process_audio_file
except ImportError as e:
    logger.error(f"Failed to import pipeline: {e}")
    logger.error("Make sure all dependencies are installed: pip install -r requirements.txt")
    raise

<<<<<<< HEAD
# Import API routers
from .routers import auth, users, admin, dashboard, history

=======
>>>>>>> 015c03c9e65da3a9fde160ed1e1b7b748a0ed461
BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_DIR = BASE_DIR / "media"
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

<<<<<<< HEAD
# Create FastAPI app
app = FastAPI(
    title="Speech Clarity Enhancement API - Production",
    version="2.0.0",
    description="AI-powered speech clarity enhancement with authentication and subscription management"
)

# Security
security = HTTPBearer()

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("=" * 60)
    logger.info("Speech Clarity Enhancement API - Production Starting...")
    logger.info(f"Media directory: {MEDIA_DIR}")
    
    # Check database connection
    if check_database_connection():
        logger.info("Database connection successful")
        try:
            init_database()
            logger.info("Database tables initialized")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
    else:
        logger.error("Database connection failed - some features may not work")
    
    logger.info("=" * 60)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Restrict origins in production
=======
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
>>>>>>> 015c03c9e65da3a9fde160ed1e1b7b748a0ed461
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

<<<<<<< HEAD
# Include API routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(history.router, prefix="/history", tags=["History"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])


# ===================================================
# MAIN AUDIO PROCESSING ENDPOINT (PROTECTED)
# ===================================================

@app.post("/enhance-speech", response_model=AudioProcessResponse)
=======

@app.post("/enhance-speech")
>>>>>>> 015c03c9e65da3a9fde160ed1e1b7b748a0ed461
async def enhance_speech(
    file: UploadFile = File(...),
    output_mode: str = Form("both"),  # "audio" | "text" | "both"
    calculate_metrics: bool = Form(True),
<<<<<<< HEAD
    grammar_correction: bool = Form(True),  # NEW: Grammar correction toggle
    realtime: bool = Form(False),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """
    Main audio processing endpoint with authentication and usage limits.
    
    Features:
    1. User authentication required
    2. Usage limit enforcement (10 free uses for normal users)
    3. Saves uploaded audio with user tracking
    4. Runs ASR -> text cleaning -> TTS pipeline
    5. Calculates fluency metrics (if requested)
    6. Stores processing history in database
    7. Returns selected outputs based on output_mode
    
    Parameters:
    - file: Audio file (FLAC, WAV, MP3, WebM)
    - output_mode: "audio" | "text" | "both" - what to return
    - calculate_metrics: true/false - whether to calculate fluency scores
    - grammar_correction: true/false - whether to apply grammar correction
    - realtime: true/false - real-time mode flag
    
    Returns:
    - AudioProcessResponse with results and usage information
    """
    import asyncio
    
    start_time = time.time()
=======
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
>>>>>>> 015c03c9e65da3a9fde160ed1e1b7b748a0ed461
    
    # Validate output_mode
    if output_mode not in ["audio", "text", "both"]:
        output_mode = "both"
        logger.warning(f"Invalid output_mode, defaulting to 'both'")
    
<<<<<<< HEAD
    # Check usage limits
    usage_tracker = get_usage_tracker(db)
    try:
        can_process, message, usage_info = usage_tracker.can_process_audio(current_user.user_id)
        if not can_process:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "error": "Usage limit exceeded",
                    "message": message,
                    "usage_info": usage_info,
                    "upgrade_required": True
                }
            )
    except UsageLimitError as e:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "error": "Usage limit exceeded",
                "message": str(e),
                "upgrade_required": True
            }
        )
    
    # Save input file with user tracking
    suffix = Path(file.filename or "audio").suffix or ".flac"
    input_id = uuid.uuid4().hex
    input_path = MEDIA_DIR / f"input_{input_id}{suffix}"
    
    # Calculate file size
    content = await file.read()
    file_size_mb = len(content) / (1024 * 1024)
    
    # Check file size limit (50MB max)
    if file_size_mb > 50:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds 50MB limit"
        )

    try:
        logger.info(f"User {current_user.user_id} ({current_user.email}) processing: {file.filename}")
        logger.info(f"Mode: {output_mode}, Metrics: {calculate_metrics}, Size: {file_size_mb:.2f}MB")
        
        # Save file
        with input_path.open("wb") as f:
            f.write(content)
        logger.info(f"File saved: {input_path.name}")

        # Consume usage credit
        try:
            updated_usage = usage_tracker.consume_usage(current_user.user_id)
        except UsageLimitError as e:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=str(e)
            )

        # Process through AI pipeline
        try:
=======
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
>>>>>>> 015c03c9e65da3a9fde160ed1e1b7b748a0ed461
            loop = asyncio.get_event_loop()
            result = await asyncio.wait_for(
                loop.run_in_executor(
                    None, 
                    process_audio_file, 
                    input_path, 
                    MEDIA_DIR,
                    output_mode,
<<<<<<< HEAD
                    calculate_metrics,
                    grammar_correction  # Pass grammar correction flag
=======
                    calculate_metrics
>>>>>>> 015c03c9e65da3a9fde160ed1e1b7b748a0ed461
                ),
                timeout=120.0  # 2 minute timeout
            )
            
<<<<<<< HEAD
            processing_duration = time.time() - start_time
            logger.info(f"Processing completed in {processing_duration:.2f}s")
            
            # Create audio history record
            audio_history = AudioHistory(
                user_id=current_user.user_id,
                original_filename=file.filename or "unknown",
                original_audio_path=str(input_path),
                enhanced_audio_path=str(result.get("enhanced_audio_path", "")),
                transcript_raw=result.get("raw_text", ""),
                transcript_cleaned=result.get("cleaned_text", ""),
                output_mode=OutputMode(output_mode),
                processing_duration=round(processing_duration, 2),
                file_size_mb=round(file_size_mb, 2)
            )
            
            db.add(audio_history)
            db.commit()
            db.refresh(audio_history)
            
            # Store fluency metrics if calculated
            fluency_comparison = None
            if calculate_metrics and "fluency_metrics" in result:
                metrics = result["fluency_metrics"]
                
                fluency_score = FluencyScore(
                    audio_id=audio_history.audio_id,
                    before_score=metrics["before"]["fluency_score"],
                    after_score=metrics["after"]["fluency_score"],
                    repetition_count_before=metrics["before"]["repetitions"],
                    repetition_count_after=metrics["after"]["repetitions"],
                    filler_count_before=metrics["before"]["fillers"],
                    filler_count_after=metrics["after"]["fillers"],
                    pause_count_before=metrics["before"]["pauses"],
                    pause_count_after=metrics["after"]["pauses"],
                    total_words_before=metrics["before"]["total_words"],
                    total_words_after=metrics["after"]["total_words"],
                    improvement_score=metrics["improvement"]["score_improvement"]
                )
                
                db.add(fluency_score)
                db.commit()
                
                # Format for response
                fluency_comparison = FluencyComparison(
                    before=FluencyMetrics(**metrics["before"]),
                    after=FluencyMetrics(**metrics["after"]),
                    improvement=metrics["improvement"]
                )
            
            # Build response
            response_data = {
                "audio_id": audio_history.audio_id,
                "message": f"Processing completed successfully. {updated_usage['remaining_uses']} uses remaining." if not updated_usage.get('is_premium') else "Processing completed successfully.",
                "usage_info": UsageInfo(
                    total_uses=updated_usage["total_uses"],
                    remaining_uses=updated_usage["remaining_uses"],
                    is_premium=updated_usage["is_premium"],
                    last_used_at=updated_usage["last_used_at"],
                    user_role=current_user.role.value
                ),
                "processing_duration": processing_duration
            }
            
            # Add content based on output_mode
            if output_mode in ["text", "both"]:
                response_data["cleaned_text"] = result.get("cleaned_text", "")
                response_data["raw_text"] = result.get("raw_text", "")
=======
            logger.info("Processing completed successfully")
            
            # Build response based on output_mode
            response = {}
            
            if output_mode in ["text", "both"]:
                response["cleaned_text"] = result.get("cleaned_text", "")
                response["raw_text"] = result.get("raw_text", "")
>>>>>>> 015c03c9e65da3a9fde160ed1e1b7b748a0ed461
            
            if output_mode in ["audio", "both"]:
                enhanced_path = result.get("enhanced_audio_path")
                if enhanced_path:
<<<<<<< HEAD
                    response_data["enhanced_audio_filename"] = enhanced_path.name
            
            if fluency_comparison:
                response_data["fluency_metrics"] = fluency_comparison
            
            return AudioProcessResponse(**response_data)
            
        except asyncio.TimeoutError:
            logger.error("Processing timed out")
            raise HTTPException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                detail="Processing timed out after 2 minutes. Please try a shorter audio file."
            )
        except Exception as e:
            logger.error(f"Processing failed: {e}", exc_info=True)
            error_msg = str(e)
            
            # User-friendly error messages
            if "Could not load audio" in error_msg or "load" in error_msg.lower():
                if "webm" in error_msg.lower():
                    detail = "WebM audio format not fully supported. Please try WAV, FLAC, or MP3."
                else:
                    detail = f"Could not load audio file. Supported formats: WAV, FLAC, MP3. Error: {error_msg}"
            elif "TTS" in error_msg or "pyttsx3" in error_msg:
                detail = "Text-to-speech generation failed. Please try again or contact support."
            elif "Whisper" in error_msg or "whisper" in error_msg:
                detail = "Speech recognition failed. Please ensure audio quality is good."
            else:
                detail = f"Processing failed: {error_msg}"
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=detail
            )
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"File upload failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process uploaded file: {e}"
=======
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
>>>>>>> 015c03c9e65da3a9fde160ed1e1b7b748a0ed461
        )


@app.get("/download/{filename}")
<<<<<<< HEAD
async def download_enhanced_audio(
    filename: str
):
    """
    Download enhanced audio file (public endpoint for audio playback).
    
    No authentication required to allow browser audio players to work.
    """
    file_path = MEDIA_DIR / filename
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    logger.info(f"Downloading file: {filename}")
    return FileResponse(
        path=file_path, 
        filename=filename, 
        media_type="audio/wav"
    )


# ===================================================
# PUBLIC ENDPOINTS (NO AUTH REQUIRED)
# ===================================================

=======
async def download_enhanced_audio(filename: str):
    file_path = MEDIA_DIR / filename
    if not file_path.exists():
        return JSONResponse({"detail": "File not found"}, status_code=404)
    return FileResponse(path=file_path, filename=file_path.name, media_type="audio/wav")


>>>>>>> 015c03c9e65da3a9fde160ed1e1b7b748a0ed461
@app.get("/")
async def root():
    """Root endpoint - API information."""
    return JSONResponse({
<<<<<<< HEAD
        "message": "Speech Clarity Enhancement API - Production",
        "version": "2.0.0",
        "features": [
            "AI-powered speech enhancement",
            "User authentication and authorization",
            "Usage limits and premium subscriptions",
            "Processing history and analytics",
            "Admin panel and user management"
        ],
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "auth": "/auth",
            "dashboard": "/dashboard"
=======
        "message": "Speech Clarity Enhancement API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "enhance": "/enhance-speech",
            "docs": "/docs"
>>>>>>> 015c03c9e65da3a9fde160ed1e1b7b748a0ed461
        }
    })

@app.get("/health")
async def health():
    """Health check endpoint for frontend connection monitoring."""
<<<<<<< HEAD
    db_status = "connected" if check_database_connection() else "disconnected"
    return {
        "status": "ok", 
        "message": "Backend is running",
        "database": db_status,
        "version": "2.0.0"
    }

@app.get("/pricing")
async def get_pricing():
    """Get pricing information for subscription plans."""
    return JSONResponse({
        "plans": [
            {
                "plan_type": "free",
                "name": "Free Plan",
                "price": 0.00,
                "currency": "USD",
                "duration": "Forever",
                "features": [
                    "10 speech enhancements per account",
                    "Basic fluency metrics",
                    "Standard processing speed",
                    "WAV, FLAC, MP3 support"
                ],
                "limitations": [
                    "Limited to 10 total uses",
                    "No priority support"
                ],
                "is_popular": False
            },
            {
                "plan_type": "monthly_premium",
                "name": "Monthly Premium",
                "price": 9.99,
                "currency": "USD",
                "duration": "Per month",
                "features": [
                    "Unlimited speech enhancements",
                    "Advanced fluency metrics",
                    "Priority processing",
                    "All audio formats supported",
                    "Processing history",
                    "Priority support"
                ],
                "limitations": [],
                "is_popular": True
            },
            {
                "plan_type": "yearly_premium",
                "name": "Yearly Premium",
                "price": 99.99,
                "currency": "USD",
                "duration": "Per year",
                "features": [
                    "Unlimited speech enhancements",
                    "Advanced fluency metrics",
                    "Priority processing",
                    "All audio formats supported",
                    "Processing history",
                    "Priority support",
                    "2 months free (save 17%)"
                ],
                "limitations": [],
                "is_popular": False
            }
        ],
        "note": "This is a simulated payment system for academic purposes only."
    })

# ===================================================
# ERROR HANDLERS
# ===================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": "An unexpected error occurred. Please try again later.",
            "timestamp": datetime.utcnow().isoformat()
        }
    )
=======
    return {"status": "ok", "message": "Backend is running"}
>>>>>>> 015c03c9e65da3a9fde160ed1e1b7b748a0ed461




