"""
Audio processing history API routes.

This module provides endpoints for:
- Processing history with pagination
- Individual file details
- History search and filtering
- File downloads
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from datetime import datetime, timedelta
from typing import Optional, List
import logging

from ..database import get_database
from ..models import User, AudioHistory, FluencyScore, OutputMode
from ..auth import get_current_active_user
from ..schemas import AudioHistoryResponse, AudioHistoryList

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=AudioHistoryList)
async def get_processing_history(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    output_mode: Optional[OutputMode] = Query(None, description="Filter by output mode"),
    days: Optional[int] = Query(None, ge=1, le=365, description="Filter by days ago"),
    search: Optional[str] = Query(None, min_length=1, max_length=100, description="Search in filenames and transcripts"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """
    Get paginated processing history for the current user.
    For admin users, returns all users' history with user information.
    
    Supports filtering by:
    - Output mode (audio, text, both)
    - Time period (last N days)
    - Search in filenames and transcripts
    """
    try:
        # Build base query
        # Admin users can see all history, regular users only see their own
        if current_user.role == 'admin':
            query = db.query(AudioHistory)
        else:
            query = db.query(AudioHistory).filter(
                AudioHistory.user_id == current_user.user_id
            )
        
        # Apply filters
        if output_mode:
            query = query.filter(AudioHistory.output_mode == output_mode)
        
        if days:
            start_date = datetime.utcnow() - timedelta(days=days)
            query = query.filter(AudioHistory.created_at >= start_date)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    AudioHistory.original_filename.ilike(search_term),
                    AudioHistory.transcript_raw.ilike(search_term),
                    AudioHistory.transcript_cleaned.ilike(search_term)
                )
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * per_page
        items = query.order_by(desc(AudioHistory.created_at)).offset(offset).limit(per_page).all()
        
        # Enrich with fluency scores and user info (for admin)
        history_items = []
        for item in items:
            fluency_score = db.query(FluencyScore).filter(
                FluencyScore.audio_id == item.audio_id
            ).first()
            
            fluency_data = None
            if fluency_score:
                fluency_data = {
                    "before_score": float(fluency_score.before_score),
                    "after_score": float(fluency_score.after_score),
                    "improvement": float(fluency_score.improvement_score or 0),
                    "repetitions_before": fluency_score.repetition_count_before,
                    "repetitions_after": fluency_score.repetition_count_after,
                    "fillers_before": fluency_score.filler_count_before,
                    "fillers_after": fluency_score.filler_count_after,
                    "pauses_before": fluency_score.pause_count_before,
                    "pauses_after": fluency_score.pause_count_after
                }
            
            # Get user info for admin
            user_info = None
            if current_user.role == 'admin':
                user = db.query(User).filter(User.user_id == item.user_id).first()
                if user:
                    user_info = {
                        "user_id": user.user_id,
                        "name": user.name,
                        "email": user.email
                    }
            
            # Create response dict manually to avoid ORM relationship issues
            history_response = AudioHistoryResponse(
                audio_id=item.audio_id,
                original_filename=item.original_filename,
                original_audio_path=item.original_audio_path,
                enhanced_audio_path=item.enhanced_audio_path,
                transcript_raw=item.transcript_raw,
                transcript_cleaned=item.transcript_cleaned,
                output_mode=item.output_mode.value,
                processing_duration=item.processing_duration,
                file_size_mb=item.file_size_mb,
                created_at=item.created_at,
                fluency_scores=fluency_data,
                user_info=user_info
            )
            history_items.append(history_response)
        
        # Calculate pagination info
        has_next = (page * per_page) < total
        has_prev = page > 1
        
        return AudioHistoryList(
            items=history_items,
            total=total,
            page=page,
            per_page=per_page,
            has_next=has_next,
            has_prev=has_prev
        )
        
    except Exception as e:
        logger.error(f"History retrieval failed for user {current_user.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load processing history"
        )

@router.get("/{audio_id}", response_model=AudioHistoryResponse)
async def get_audio_details(
    audio_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """
    Get detailed information about a specific processed audio file.
    
    Users can only access their own files.
    """
    try:
        # Get audio record
        audio_record = db.query(AudioHistory).filter(
            and_(
                AudioHistory.audio_id == audio_id,
                AudioHistory.user_id == current_user.user_id
            )
        ).first()
        
        if not audio_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audio record not found"
            )
        
        # Get fluency scores
        fluency_score = db.query(FluencyScore).filter(
            FluencyScore.audio_id == audio_id
        ).first()
        
        fluency_data = None
        if fluency_score:
            fluency_data = {
                "before_score": float(fluency_score.before_score),
                "after_score": float(fluency_score.after_score),
                "improvement": float(fluency_score.improvement_score or 0),
                "repetitions_before": fluency_score.repetition_count_before,
                "repetitions_after": fluency_score.repetition_count_after,
                "fillers_before": fluency_score.filler_count_before,
                "fillers_after": fluency_score.filler_count_after,
                "pauses_before": fluency_score.pause_count_before,
                "pauses_after": fluency_score.pause_count_after,
                "total_words_before": fluency_score.total_words_before,
                "total_words_after": fluency_score.total_words_after
            }
        
        response = AudioHistoryResponse(
            audio_id=audio_record.audio_id,
            original_filename=audio_record.original_filename,
            original_audio_path=audio_record.original_audio_path,
            enhanced_audio_path=audio_record.enhanced_audio_path,
            transcript_raw=audio_record.transcript_raw,
            transcript_cleaned=audio_record.transcript_cleaned,
            output_mode=audio_record.output_mode.value,
            processing_duration=audio_record.processing_duration,
            file_size_mb=audio_record.file_size_mb,
            created_at=audio_record.created_at,
            fluency_scores=fluency_data
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Audio details retrieval failed for audio {audio_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load audio details"
        )

@router.delete("/{audio_id}")
async def delete_audio_record(
    audio_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """
    Delete a processed audio record and its associated files.
    
    Users can only delete their own records.
    """
    try:
        # Get audio record
        audio_record = db.query(AudioHistory).filter(
            and_(
                AudioHistory.audio_id == audio_id,
                AudioHistory.user_id == current_user.user_id
            )
        ).first()
        
        if not audio_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audio record not found"
            )
        
        # Delete associated fluency scores first (due to foreign key constraint)
        db.query(FluencyScore).filter(FluencyScore.audio_id == audio_id).delete()
        
        # Delete the audio record
        db.delete(audio_record)
        db.commit()
        
        # TODO: In production, also delete the actual audio files from disk
        # This would require careful handling to avoid deleting files that might be in use
        
        logger.info(f"Audio record {audio_id} deleted by user {current_user.user_id}")
        
        return {"message": "Audio record deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Audio deletion failed for audio {audio_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete audio record"
        )

@router.get("/stats/summary")
async def get_history_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """
    Get summary statistics for user's processing history.
    """
    try:
        from sqlalchemy import func
        
        # Basic counts
        total_files = db.query(func.count(AudioHistory.audio_id)).filter(
            AudioHistory.user_id == current_user.user_id
        ).scalar() or 0
        
        # Files by output mode
        mode_stats = db.query(
            AudioHistory.output_mode,
            func.count(AudioHistory.audio_id).label('count')
        ).filter(
            AudioHistory.user_id == current_user.user_id
        ).group_by(AudioHistory.output_mode).all()
        
        # Total processing time
        total_time = db.query(func.sum(AudioHistory.processing_duration)).filter(
            AudioHistory.user_id == current_user.user_id
        ).scalar() or 0
        
        # Average file size
        avg_size = db.query(func.avg(AudioHistory.file_size_mb)).filter(
            AudioHistory.user_id == current_user.user_id
        ).scalar() or 0
        
        # Files processed this month
        start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        files_this_month = db.query(func.count(AudioHistory.audio_id)).filter(
            AudioHistory.user_id == current_user.user_id,
            AudioHistory.created_at >= start_of_month
        ).scalar() or 0
        
        # Average improvement score
        avg_improvement = db.query(func.avg(FluencyScore.improvement_score)).join(
            AudioHistory, AudioHistory.audio_id == FluencyScore.audio_id
        ).filter(
            AudioHistory.user_id == current_user.user_id
        ).scalar() or 0
        
        return {
            "total_files": total_files,
            "files_this_month": files_this_month,
            "total_processing_time": float(total_time),
            "average_file_size_mb": float(avg_size),
            "average_improvement_score": float(avg_improvement),
            "files_by_mode": [
                {
                    "mode": stat.output_mode.value,
                    "count": stat.count
                }
                for stat in mode_stats
            ]
        }
        
    except Exception as e:
        logger.error(f"History summary failed for user {current_user.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load history summary"
        )

@router.post("/bulk-delete")
async def bulk_delete_records(
    audio_ids: List[int],
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """
    Delete multiple audio records at once.
    
    Users can only delete their own records.
    """
    if not audio_ids or len(audio_ids) > 50:  # Limit bulk operations
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid audio_ids list. Must contain 1-50 IDs."
        )
    
    try:
        # Verify all records belong to the user
        user_records = db.query(AudioHistory).filter(
            and_(
                AudioHistory.audio_id.in_(audio_ids),
                AudioHistory.user_id == current_user.user_id
            )
        ).all()
        
        if len(user_records) != len(audio_ids):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Some records not found or don't belong to you"
            )
        
        # Delete fluency scores first
        db.query(FluencyScore).filter(FluencyScore.audio_id.in_(audio_ids)).delete(synchronize_session=False)
        
        # Delete audio records
        deleted_count = db.query(AudioHistory).filter(
            and_(
                AudioHistory.audio_id.in_(audio_ids),
                AudioHistory.user_id == current_user.user_id
            )
        ).delete(synchronize_session=False)
        
        db.commit()
        
        logger.info(f"Bulk deleted {deleted_count} records for user {current_user.user_id}")
        
        return {
            "message": f"Successfully deleted {deleted_count} records",
            "deleted_count": deleted_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Bulk delete failed for user {current_user.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete records"
        )