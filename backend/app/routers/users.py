"""
User management API routes.

This module provides endpoints for:
- User profile management
- Subscription management
- Usage information
- Account settings
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date
import logging

from ..database import get_database
from ..models import User, Subscription, PlanType
from ..auth import get_current_active_user
from ..usage_limits import get_usage_tracker, get_subscription_manager
from ..schemas import (
    UserResponse, UserUpdate, UsageInfo, SubscriptionResponse,
    SubscriptionCreate, SuccessResponse, PricingPlan
)

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/profile", response_model=UserResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user's profile information.
    """
    return UserResponse.from_orm(current_user)

@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """
    Update user profile information.
    
    Users can update their name and email.
    """
    try:
        # Check if email is already taken by another user
        if user_update.email and user_update.email != current_user.email:
            existing_user = db.query(User).filter(
                User.email == user_update.email,
                User.user_id != current_user.user_id
            ).first()
            
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use by another account"
                )
        
        # Update fields
        if user_update.name:
            current_user.name = user_update.name
        if user_update.email:
            current_user.email = user_update.email
            current_user.email_verified = False  # Require re-verification
        
        db.commit()
        db.refresh(current_user)
        
        logger.info(f"Profile updated for user {current_user.user_id}")
        
        return UserResponse.from_orm(current_user)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Profile update failed for user {current_user.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed. Please try again."
        )

@router.get("/usage", response_model=UsageInfo)
async def get_user_usage(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """
    Get current user's usage information.
    
    Returns:
    - Total uses
    - Remaining free uses
    - Premium status
    - Last usage timestamp
    """
    usage_tracker = get_usage_tracker(db)
    usage_log = usage_tracker.get_user_usage(current_user.user_id)
    
    if not usage_log:
        # Create usage log if it doesn't exist
        usage_log = usage_tracker._create_usage_log(current_user.user_id)
    
    is_premium = usage_tracker.is_premium_user(current_user.user_id)
    
    return UsageInfo(
        total_uses=usage_log.total_uses,
        remaining_uses=usage_log.remaining_uses,
        is_premium=is_premium,
        last_used_at=usage_log.last_used_at,
        user_role=current_user.role.value
    )

@router.get("/subscription", response_model=SubscriptionResponse)
async def get_user_subscription(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """
    Get current user's active subscription.
    """
    usage_tracker = get_usage_tracker(db)
    subscription = usage_tracker.get_active_subscription(current_user.user_id)
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )
    
    return SubscriptionResponse.from_orm(subscription)

@router.post("/subscription", response_model=SubscriptionResponse)
async def create_subscription(
    subscription_data: SubscriptionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """
    Create a new subscription (simulated payment).
    
    This is a simulated payment system for academic purposes.
    In production, this would integrate with a real payment processor.
    """
    if subscription_data.plan_type == PlanType.FREE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create free subscription. Free plan is automatic."
        )
    
    try:
        subscription_manager = get_subscription_manager(db)
        subscription = subscription_manager.create_subscription(
            user_id=current_user.user_id,
            plan_type=subscription_data.plan_type,
            duration_months=subscription_data.duration_months
        )
        
        logger.info(f"Subscription created for user {current_user.user_id}: {subscription_data.plan_type.value}")
        
        return SubscriptionResponse.from_orm(subscription)
        
    except Exception as e:
        logger.error(f"Subscription creation failed for user {current_user.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Subscription creation failed. Please try again."
        )

@router.delete("/subscription", response_model=SuccessResponse)
async def cancel_subscription(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """
    Cancel current user's subscription.
    
    Reverts user to free plan.
    """
    try:
        subscription_manager = get_subscription_manager(db)
        success = subscription_manager.cancel_subscription(current_user.user_id)
        
        if success:
            logger.info(f"Subscription cancelled for user {current_user.user_id}")
            return SuccessResponse(
                message="Subscription cancelled successfully. You have been reverted to the free plan."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active subscription found to cancel"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Subscription cancellation failed for user {current_user.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Subscription cancellation failed. Please try again."
        )

@router.get("/subscription/status")
async def get_subscription_status(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """
    Get detailed subscription status information.
    """
    usage_tracker = get_usage_tracker(db)
    subscription = usage_tracker.get_active_subscription(current_user.user_id)
    usage_log = usage_tracker.get_user_usage(current_user.user_id)
    is_premium = usage_tracker.is_premium_user(current_user.user_id)
    
    status_info = {
        "is_premium": is_premium,
        "user_role": current_user.role.value,
        "has_active_subscription": subscription is not None,
        "usage_info": {
            "total_uses": usage_log.total_uses if usage_log else 0,
            "remaining_uses": usage_log.remaining_uses if usage_log else 10,
            "last_used_at": usage_log.last_used_at if usage_log else None
        }
    }
    
    if subscription:
        status_info["subscription"] = {
            "plan_type": subscription.plan_type.value,
            "start_date": subscription.start_date.isoformat(),
            "end_date": subscription.end_date.isoformat() if subscription.end_date else None,
            "is_active": subscription.is_active,
            "amount": float(subscription.amount),
            "currency": subscription.currency
        }
        
        # Calculate days remaining
        if subscription.end_date:
            days_remaining = (subscription.end_date - date.today()).days
            status_info["subscription"]["days_remaining"] = max(0, days_remaining)
    
    return status_info

@router.delete("/account", response_model=SuccessResponse)
async def delete_account(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """
    Delete user account (soft delete).
    
    Deactivates the account instead of permanently deleting it.
    This preserves data integrity and allows for account recovery.
    """
    try:
        # Soft delete - deactivate account
        current_user.is_active = False
        
        # Cancel any active subscriptions
        subscription_manager = get_subscription_manager(db)
        subscription_manager.cancel_subscription(current_user.user_id)
        
        db.commit()
        
        logger.info(f"Account deactivated for user {current_user.user_id}")
        
        return SuccessResponse(
            message="Account deactivated successfully. Contact support to reactivate."
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Account deletion failed for user {current_user.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Account deletion failed. Please try again."
        )