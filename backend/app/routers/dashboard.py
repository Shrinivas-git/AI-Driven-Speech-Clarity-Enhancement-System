"""
User dashboard API routes.

This module provides endpoints for:
- Dashboard overview
- User statistics
- Recent activity
- Usage analytics
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging

from ..database import get_database
from ..models import User, AudioHistory, FluencyScore, UsageLog, Subscription
from ..auth import get_current_active_user
from ..usage_limits import get_usage_tracker
from ..schemas import (
    UserDashboard, UserStatistics, AudioHistoryResponse,
    UserResponse, UsageInfo, SubscriptionResponse
)

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/overview", response_model=UserDashboard)
async def get_dashboard_overview(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """
    Get comprehensive dashboard overview for the current user.
    
    Returns:
    - User information
    - Usage statistics
    - Subscription status
    - Recent activity
    - Performance metrics
    """
    try:
        # Get usage information
        usage_tracker = get_usage_tracker(db)
        usage_log = usage_tracker.get_user_usage(current_user.user_id)
        is_premium = usage_tracker.is_premium_user(current_user.user_id)
        
        usage_info = UsageInfo(
            total_uses=usage_log.total_uses if usage_log else 0,
            remaining_uses=usage_log.remaining_uses if usage_log else 10,
            is_premium=is_premium,
            last_used_at=usage_log.last_used_at if usage_log else None,
            user_role=current_user.role.value
        )
        
        # Get subscription information
        subscription = usage_tracker.get_active_subscription(current_user.user_id)
        subscription_info = SubscriptionResponse.from_orm(subscription) if subscription else None
        
        # Get recent activity (last 10 processed files)
        recent_activity = db.query(AudioHistory).filter(
            AudioHistory.user_id == current_user.user_id
        ).order_by(desc(AudioHistory.created_at)).limit(10).all()
        
        recent_activity_list = []
        for activity in recent_activity:
            # Get fluency scores if available
            fluency_score = db.query(FluencyScore).filter(
                FluencyScore.audio_id == activity.audio_id
            ).first()
            
            fluency_data = None
            if fluency_score:
                fluency_data = {
                    "before_score": float(fluency_score.before_score),
                    "after_score": float(fluency_score.after_score),
                    "improvement": float(fluency_score.improvement_score or 0)
                }
            
            # Create response dict manually to avoid ORM relationship issues
            activity_response = AudioHistoryResponse(
                audio_id=activity.audio_id,
                original_filename=activity.original_filename,
                original_audio_path=activity.original_audio_path,
                enhanced_audio_path=activity.enhanced_audio_path,
                transcript_raw=activity.transcript_raw,
                transcript_cleaned=activity.transcript_cleaned,
                output_mode=activity.output_mode.value,
                processing_duration=activity.processing_duration,
                file_size_mb=activity.file_size_mb,
                created_at=activity.created_at,
                fluency_scores=fluency_data
            )
            recent_activity_list.append(activity_response)
        
        # Get user statistics
        statistics = await get_user_statistics_data(current_user.user_id, db)
        
        return UserDashboard(
            user_info=UserResponse.from_orm(current_user),
            usage_info=usage_info,
            subscription_info=subscription_info,
            recent_activity=recent_activity_list,
            statistics=statistics
        )
        
    except Exception as e:
        logger.error(f"Dashboard overview failed for user {current_user.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load dashboard data"
        )

@router.get("/statistics", response_model=UserStatistics)
async def get_user_statistics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """
    Get detailed user statistics and analytics.
    """
    try:
        stats_data = await get_user_statistics_data(current_user.user_id, db)
        
        return UserStatistics(
            total_processed_files=stats_data["total_processed_files"],
            total_processing_time=stats_data["total_processing_time"],
            average_improvement_score=stats_data["average_improvement_score"],
            most_active_day=stats_data["most_active_day"],
            files_this_month=stats_data["files_this_month"],
            improvement_trend=stats_data["improvement_trend"]
        )
        
    except Exception as e:
        logger.error(f"Statistics retrieval failed for user {current_user.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load statistics"
        )

@router.get("/activity")
async def get_recent_activity(
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """
    Get recent processing activity for the user.
    
    Args:
        limit: Maximum number of activities to return (default: 20, max: 100)
    """
    # Validate limit
    limit = min(max(1, limit), 100)
    
    try:
        activities = db.query(AudioHistory).filter(
            AudioHistory.user_id == current_user.user_id
        ).order_by(desc(AudioHistory.created_at)).limit(limit).all()
        
        activity_list = []
        for activity in activities:
            # Get fluency scores
            fluency_score = db.query(FluencyScore).filter(
                FluencyScore.audio_id == activity.audio_id
            ).first()
            
            fluency_data = None
            if fluency_score:
                fluency_data = {
                    "before_score": float(fluency_score.before_score),
                    "after_score": float(fluency_score.after_score),
                    "improvement": float(fluency_score.improvement_score or 0),
                    "repetitions_reduced": fluency_score.repetition_count_before - fluency_score.repetition_count_after,
                    "fillers_reduced": fluency_score.filler_count_before - fluency_score.filler_count_after
                }
            
            # Create response dict manually to avoid ORM relationship issues
            activity_response = AudioHistoryResponse(
                audio_id=activity.audio_id,
                original_filename=activity.original_filename,
                original_audio_path=activity.original_audio_path,
                enhanced_audio_path=activity.enhanced_audio_path,
                transcript_raw=activity.transcript_raw,
                transcript_cleaned=activity.transcript_cleaned,
                output_mode=activity.output_mode.value,
                processing_duration=activity.processing_duration,
                file_size_mb=activity.file_size_mb,
                created_at=activity.created_at,
                fluency_scores=fluency_data
            )
            activity_list.append(activity_response)
        
        return {
            "activities": activity_list,
            "total_count": len(activity_list),
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Activity retrieval failed for user {current_user.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load activity data"
        )

@router.get("/analytics")
async def get_user_analytics(
    days: int = 30,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """
    Get user analytics for the specified time period.
    
    Args:
        days: Number of days to analyze (default: 30, max: 365)
    """
    # Validate days parameter
    days = min(max(1, days), 365)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    try:
        # Get processing activity over time
        daily_activity = db.query(
            func.date(AudioHistory.created_at).label('date'),
            func.count(AudioHistory.audio_id).label('count'),
            func.avg(AudioHistory.processing_duration).label('avg_duration')
        ).filter(
            AudioHistory.user_id == current_user.user_id,
            AudioHistory.created_at >= start_date
        ).group_by(
            func.date(AudioHistory.created_at)
        ).order_by('date').all()
        
        # Get improvement trends
        improvement_trend = db.query(
            func.date(AudioHistory.created_at).label('date'),
            func.avg(FluencyScore.improvement_score).label('avg_improvement')
        ).join(
            FluencyScore, AudioHistory.audio_id == FluencyScore.audio_id
        ).filter(
            AudioHistory.user_id == current_user.user_id,
            AudioHistory.created_at >= start_date
        ).group_by(
            func.date(AudioHistory.created_at)
        ).order_by('date').all()
        
        # Get output mode preferences
        output_mode_stats = db.query(
            AudioHistory.output_mode,
            func.count(AudioHistory.audio_id).label('count')
        ).filter(
            AudioHistory.user_id == current_user.user_id,
            AudioHistory.created_at >= start_date
        ).group_by(AudioHistory.output_mode).all()
        
        # Format response
        analytics_data = {
            "period_days": days,
            "start_date": start_date.isoformat(),
            "daily_activity": [
                {
                    "date": activity.date.isoformat(),
                    "files_processed": activity.count,
                    "avg_processing_time": float(activity.avg_duration or 0)
                }
                for activity in daily_activity
            ],
            "improvement_trend": [
                {
                    "date": trend.date.isoformat(),
                    "avg_improvement": float(trend.avg_improvement or 0)
                }
                for trend in improvement_trend
            ],
            "output_mode_preferences": [
                {
                    "mode": mode_stat.output_mode.value,
                    "count": mode_stat.count
                }
                for mode_stat in output_mode_stats
            ],
            "summary": {
                "total_files": sum(activity.count for activity in daily_activity),
                "avg_daily_files": sum(activity.count for activity in daily_activity) / max(days, 1),
                "most_productive_day": max(daily_activity, key=lambda x: x.count).date.isoformat() if daily_activity else None,
                "avg_improvement": sum(trend.avg_improvement or 0 for trend in improvement_trend) / max(len(improvement_trend), 1)
            }
        }
        
        return analytics_data
        
    except Exception as e:
        logger.error(f"Analytics retrieval failed for user {current_user.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load analytics data"
        )

async def get_user_statistics_data(user_id: int, db: Session) -> Dict[str, Any]:
    """
    Helper function to get user statistics data.
    """
    # Total processed files
    total_files = db.query(func.count(AudioHistory.audio_id)).filter(
        AudioHistory.user_id == user_id
    ).scalar() or 0
    
    # Total processing time
    total_time = db.query(func.sum(AudioHistory.processing_duration)).filter(
        AudioHistory.user_id == user_id
    ).scalar() or 0
    
    # Average improvement score
    avg_improvement = db.query(func.avg(FluencyScore.improvement_score)).join(
        AudioHistory, AudioHistory.audio_id == FluencyScore.audio_id
    ).filter(
        AudioHistory.user_id == user_id
    ).scalar() or 0
    
    # Most active day of the week
    day_activity = db.query(
        func.dayname(AudioHistory.created_at).label('day'),
        func.count(AudioHistory.audio_id).label('count')
    ).filter(
        AudioHistory.user_id == user_id
    ).group_by('day').order_by(desc('count')).first()
    
    most_active_day = day_activity.day if day_activity else None
    
    # Files this month
    start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    files_this_month = db.query(func.count(AudioHistory.audio_id)).filter(
        AudioHistory.user_id == user_id,
        AudioHistory.created_at >= start_of_month
    ).scalar() or 0
    
    # Improvement trend (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    improvement_trend = db.query(
        func.date(AudioHistory.created_at).label('date'),
        func.avg(FluencyScore.improvement_score).label('improvement')
    ).join(
        FluencyScore, AudioHistory.audio_id == FluencyScore.audio_id
    ).filter(
        AudioHistory.user_id == user_id,
        AudioHistory.created_at >= seven_days_ago
    ).group_by('date').order_by('date').all()
    
    trend_data = [
        {
            "date": trend.date.isoformat(),
            "improvement": float(trend.improvement or 0)
        }
        for trend in improvement_trend
    ]
    
    return {
        "total_processed_files": total_files,
        "total_processing_time": float(total_time),
        "average_improvement_score": float(avg_improvement),
        "most_active_day": most_active_day,
        "files_this_month": files_this_month,
        "improvement_trend": trend_data
    }