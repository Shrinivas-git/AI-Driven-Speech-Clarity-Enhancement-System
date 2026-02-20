"""
Admin panel API routes.

This module provides endpoints for:
- User management (view, edit, delete users)
- System statistics and monitoring
- Usage limit management
- Subscription management
- System settings
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from datetime import datetime, timedelta, date
from typing import Optional, List
import logging

from ..database import get_database
from ..models import (
    User, AudioHistory, FluencyScore, UsageLog, Subscription, 
    UserSession, SystemSetting, UserRole, PlanType
)
from ..auth import require_admin
from ..usage_limits import get_usage_tracker, get_subscription_manager
from ..schemas import (
    AdminUserResponse, AdminUsersList, SystemStatistics,
    AdminUserUpdate, SystemSettingResponse, SystemSettingUpdate,
    SuccessResponse, UserResponse
)

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/users", response_model=AdminUsersList)
async def get_all_users(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    role: Optional[UserRole] = Query(None, description="Filter by user role"),
    search: Optional[str] = Query(None, min_length=1, max_length=100, description="Search by name or email"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_database)
):
    """
    Get paginated list of all users with admin information.
    
    Only accessible by admin users.
    """
    try:
        # Build base query
        query = db.query(User)
        
        # Apply filters
        if role:
            query = query.filter(User.role == role)
        
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                User.name.ilike(search_term) | User.email.ilike(search_term)
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * per_page
        users = query.order_by(desc(User.created_at)).offset(offset).limit(per_page).all()
        
        # Enrich with additional data
        admin_users = []
        usage_tracker = get_usage_tracker(db)
        
        for user in users:
            # Get usage info
            usage_log = usage_tracker.get_user_usage(user.user_id)
            is_premium = usage_tracker.is_premium_user(user.user_id)
            
            usage_info = {
                "total_uses": usage_log.total_uses if usage_log else 0,
                "remaining_uses": usage_log.remaining_uses if usage_log else 10,
                "is_premium": is_premium,
                "last_used_at": usage_log.last_used_at if usage_log else None,
                "user_role": user.role.value
            }
            
            # Get subscription info
            subscription = usage_tracker.get_active_subscription(user.user_id)
            subscription_info = None
            if subscription:
                subscription_info = {
                    "subscription_id": subscription.subscription_id,
                    "plan_type": subscription.plan_type.value,
                    "start_date": subscription.start_date.isoformat(),
                    "end_date": subscription.end_date.isoformat() if subscription.end_date else None,
                    "is_active": subscription.is_active,
                    "amount": float(subscription.amount)
                }
            
            # Get processing stats
            total_files = db.query(func.count(AudioHistory.audio_id)).filter(
                AudioHistory.user_id == user.user_id
            ).scalar() or 0
            
            # Get last activity
            last_activity = db.query(AudioHistory.created_at).filter(
                AudioHistory.user_id == user.user_id
            ).order_by(desc(AudioHistory.created_at)).first()
            
            admin_user = AdminUserResponse(
                user_id=user.user_id,
                name=user.name,
                email=user.email,
                role=user.role,
                is_active=user.is_active,
                email_verified=user.email_verified,
                created_at=user.created_at,
                last_login=user.last_login,
                usage_info=usage_info,
                subscription_info=subscription_info,
                total_processed_files=total_files,
                last_activity=last_activity[0] if last_activity else None
            )
            admin_users.append(admin_user)
        
        return AdminUsersList(
            items=admin_users,
            total=total,
            page=page,
            per_page=per_page
        )
        
    except Exception as e:
        logger.error(f"Admin user list failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load user list"
        )

@router.get("/users/{user_id}", response_model=AdminUserResponse)
async def get_user_details(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_database)
):
    """
    Get detailed information about a specific user.
    """
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get enriched data (same as in get_all_users)
        usage_tracker = get_usage_tracker(db)
        usage_log = usage_tracker.get_user_usage(user.user_id)
        is_premium = usage_tracker.is_premium_user(user.user_id)
        
        usage_info = {
            "total_uses": usage_log.total_uses if usage_log else 0,
            "remaining_uses": usage_log.remaining_uses if usage_log else 10,
            "is_premium": is_premium,
            "last_used_at": usage_log.last_used_at if usage_log else None,
            "user_role": user.role.value
        }
        
        subscription = usage_tracker.get_active_subscription(user.user_id)
        subscription_info = None
        if subscription:
            subscription_info = {
                "subscription_id": subscription.subscription_id,
                "plan_type": subscription.plan_type.value,
                "start_date": subscription.start_date.isoformat(),
                "end_date": subscription.end_date.isoformat() if subscription.end_date else None,
                "is_active": subscription.is_active,
                "amount": float(subscription.amount)
            }
        
        total_files = db.query(func.count(AudioHistory.audio_id)).filter(
            AudioHistory.user_id == user.user_id
        ).scalar() or 0
        
        last_activity = db.query(AudioHistory.created_at).filter(
            AudioHistory.user_id == user.user_id
        ).order_by(desc(AudioHistory.created_at)).first()
        
        return AdminUserResponse(
            user_id=user.user_id,
            name=user.name,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            email_verified=user.email_verified,
            created_at=user.created_at,
            last_login=user.last_login,
            usage_info=usage_info,
            subscription_info=subscription_info,
            total_processed_files=total_files,
            last_activity=last_activity[0] if last_activity else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin user details failed for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load user details"
        )

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: AdminUserUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_database)
):
    """
    Update user information (admin only).
    
    Admins can update:
    - Name and email
    - Role
    - Active status
    - Reset usage limits
    """
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prevent admin from deactivating themselves
        if user_id == current_user.user_id and user_update.is_active is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot deactivate your own account"
            )
        
        # Update user fields
        if user_update.name:
            user.name = user_update.name
        if user_update.email:
            # Check if email is already taken
            existing = db.query(User).filter(
                User.email == user_update.email,
                User.user_id != user_id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use"
                )
            user.email = user_update.email
            user.email_verified = False
        
        if user_update.role:
            user.role = user_update.role
        
        if user_update.is_active is not None:
            user.is_active = user_update.is_active
        
        # Reset usage if requested
        if user_update.reset_usage:
            usage_tracker = get_usage_tracker(db)
            usage_tracker.reset_user_usage(user_id, user_update.new_usage_limit or 10)
        
        db.commit()
        db.refresh(user)
        
        logger.info(f"User {user_id} updated by admin {current_user.user_id}")
        
        return UserResponse.from_orm(user)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Admin user update failed for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )

@router.delete("/users/{user_id}", response_model=SuccessResponse)
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_database)
):
    """
    Delete a user account (admin only).
    
    This performs a soft delete by deactivating the account.
    """
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prevent admin from deleting themselves
        if user_id == current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )
        
        # Soft delete - deactivate account
        user.is_active = False
        
        # Cancel subscriptions
        subscription_manager = get_subscription_manager(db)
        subscription_manager.cancel_subscription(user_id)
        
        db.commit()
        
        logger.info(f"User {user_id} deleted by admin {current_user.user_id}")
        
        return SuccessResponse(
            message=f"User {user.email} has been deactivated"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Admin user deletion failed for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )

@router.get("/statistics", response_model=SystemStatistics)
async def get_system_statistics(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_database)
):
    """
    Get comprehensive system statistics.
    """
    try:
        usage_tracker = get_usage_tracker(db)
        stats = usage_tracker.get_usage_statistics()
        
        # Additional stats
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_signups = db.query(func.count(User.user_id)).filter(
            User.created_at >= thirty_days_ago
        ).scalar() or 0
        
        # Calculate revenue (simulated)
        active_subscriptions = db.query(Subscription).filter(
            Subscription.is_active == True,
            Subscription.plan_type.in_([PlanType.MONTHLY_PREMIUM, PlanType.YEARLY_PREMIUM])
        ).all()
        
        revenue_this_month = sum(
            float(sub.amount) for sub in active_subscriptions 
            if sub.start_date >= date.today().replace(day=1)
        )
        
        return SystemStatistics(
            total_users=stats.get("total_users", 0),
            premium_users=stats.get("premium_users", 0),
            free_users=stats.get("free_users", 0),
            active_subscriptions=stats.get("active_subscriptions", 0),
            total_usage=stats.get("total_usage", 0),
            average_usage_per_user=stats.get("average_usage_per_user", 0),
            users_at_limit=stats.get("users_at_limit", 0),
            conversion_rate=stats.get("conversion_rate", 0),
            recent_signups=recent_signups,
            revenue_this_month=revenue_this_month
        )
        
    except Exception as e:
        logger.error(f"System statistics failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load system statistics"
        )

@router.get("/settings", response_model=List[SystemSettingResponse])
async def get_system_settings(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_database)
):
    """
    Get all system settings.
    """
    try:
        settings = db.query(SystemSetting).order_by(SystemSetting.setting_key).all()
        return [SystemSettingResponse.from_orm(setting) for setting in settings]
        
    except Exception as e:
        logger.error(f"System settings retrieval failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load system settings"
        )

@router.put("/settings/{setting_key}", response_model=SystemSettingResponse)
async def update_system_setting(
    setting_key: str,
    setting_update: SystemSettingUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_database)
):
    """
    Update a system setting.
    """
    try:
        setting = db.query(SystemSetting).filter(
            SystemSetting.setting_key == setting_key
        ).first()
        
        if not setting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Setting not found"
            )
        
        setting.setting_value = setting_update.setting_value
        setting.updated_by = current_user.user_id
        
        db.commit()
        db.refresh(setting)
        
        logger.info(f"System setting {setting_key} updated by admin {current_user.user_id}")
        
        return SystemSettingResponse.from_orm(setting)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"System setting update failed for {setting_key}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update system setting"
        )

@router.post("/users/{user_id}/upgrade-to-premium", response_model=SuccessResponse)
async def upgrade_user_to_premium(
    user_id: int,
    plan_type: PlanType = PlanType.YEARLY_PREMIUM,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_database)
):
    """
    Upgrade a user to premium (admin only).
    """
    if plan_type == PlanType.FREE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot upgrade to free plan"
        )
    
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Create premium subscription
        subscription_manager = get_subscription_manager(db)
        subscription = subscription_manager.create_subscription(
            user_id=user_id,
            plan_type=plan_type,
            duration_months=12 if plan_type == PlanType.YEARLY_PREMIUM else 1
        )
        
        logger.info(f"User {user_id} upgraded to {plan_type.value} by admin {current_user.user_id}")
        
        return SuccessResponse(
            message=f"User {user.email} upgraded to {plan_type.value}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User upgrade failed for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upgrade user"
        )

@router.post("/users/{user_id}/reset-usage", response_model=SuccessResponse)
async def reset_user_usage_limit(
    user_id: int,
    new_limit: int = Query(10, ge=0, le=1000, description="New usage limit"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_database)
):
    """
    Reset a user's usage limit (admin only).
    """
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        usage_tracker = get_usage_tracker(db)
        success = usage_tracker.reset_user_usage(user_id, new_limit)
        
        if success:
            logger.info(f"Usage reset for user {user_id} to {new_limit} by admin {current_user.user_id}")
            return SuccessResponse(
                message=f"Usage limit reset to {new_limit} for user {user.email}"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to reset usage limit"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Usage reset failed for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset usage limit"
        )