"""
Usage limit system for Speech Clarity Enhancement.

This module manages:
- Free vs Premium usage tracking
- Usage limit enforcement
- Usage statistics and reporting
- Subscription-based access control
"""

from datetime import datetime, date
from typing import Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from .models import User, UsageLog, Subscription, UserRole, PlanType
import logging

logger = logging.getLogger(__name__)

class UsageLimitError(Exception):
    """Exception raised when usage limit is exceeded."""
    pass

class UsageTracker:
    """
    Handles usage tracking and limit enforcement.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_usage(self, user_id: int) -> Optional[UsageLog]:
        """
        Get current usage statistics for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            UsageLog: User's usage record or None if not found
        """
        return self.db.query(UsageLog).filter(UsageLog.user_id == user_id).first()
    
    def get_active_subscription(self, user_id: int) -> Optional[Subscription]:
        """
        Get user's active subscription.
        
        Args:
            user_id: User ID
            
        Returns:
            Subscription: Active subscription or None
        """
        today = date.today()
        return self.db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.is_active == True,
            Subscription.start_date <= today,
            (Subscription.end_date.is_(None) | (Subscription.end_date >= today))
        ).first()
    
    def is_premium_user(self, user_id: int) -> bool:
        """
        Check if user has premium access.
        
        Args:
            user_id: User ID
            
        Returns:
            bool: True if user has premium access
        """
        # Check user role
        user = self.db.query(User).filter(User.user_id == user_id).first()
        if user and user.role in [UserRole.PREMIUM, UserRole.ADMIN]:
            return True
        
        # Check active premium subscription
        subscription = self.get_active_subscription(user_id)
        if subscription and subscription.plan_type in [PlanType.MONTHLY_PREMIUM, PlanType.YEARLY_PREMIUM]:
            return True
        
        return False
    
    def can_process_audio(self, user_id: int) -> Tuple[bool, str, Dict]:
        """
        Check if user can process audio based on usage limits.
        
        Args:
            user_id: User ID
            
        Returns:
            Tuple: (can_process, message, usage_info)
        """
        # Get user and usage information
        user = self.db.query(User).filter(User.user_id == user_id).first()
        if not user:
            return False, "User not found", {}
        
        usage_log = self.get_user_usage(user_id)
        if not usage_log:
            # Create usage log if it doesn't exist
            usage_log = self._create_usage_log(user_id)
        
        # Check if user is premium
        is_premium = self.is_premium_user(user_id)
        
        usage_info = {
            "is_premium": is_premium,
            "total_uses": usage_log.total_uses,
            "remaining_uses": usage_log.remaining_uses,
            "last_used_at": usage_log.last_used_at,
            "user_role": user.role.value
        }
        
        # Premium users have unlimited access
        if is_premium:
            return True, "Premium access - unlimited usage", usage_info
        
        # Check free usage limit
        if usage_log.remaining_uses <= 0:
            return False, "Free usage limit exceeded. Upgrade to premium for unlimited access.", usage_info
        
        return True, f"Free usage available ({usage_log.remaining_uses} remaining)", usage_info
    
    def consume_usage(self, user_id: int) -> Dict:
        """
        Consume one usage credit for the user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dict: Updated usage information
            
        Raises:
            UsageLimitError: If usage limit exceeded
        """
        # Check if user can process
        can_process, message, usage_info = self.can_process_audio(user_id)
        if not can_process:
            raise UsageLimitError(message)
        
        # Get usage log
        usage_log = self.get_user_usage(user_id)
        
        # Update usage for non-premium users
        if not usage_info["is_premium"]:
            usage_log.remaining_uses = max(0, usage_log.remaining_uses - 1)
        
        usage_log.total_uses += 1
        usage_log.last_used_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(usage_log)
        
        logger.info(f"Usage consumed for user {user_id}. Remaining: {usage_log.remaining_uses}")
        
        return {
            "total_uses": usage_log.total_uses,
            "remaining_uses": usage_log.remaining_uses,
            "is_premium": usage_info["is_premium"],
            "last_used_at": usage_log.last_used_at
        }
    
    def reset_user_usage(self, user_id: int, new_limit: int = 10) -> bool:
        """
        Reset user's usage limit (admin function).
        
        Args:
            user_id: User ID
            new_limit: New usage limit
            
        Returns:
            bool: True if reset successful
        """
        try:
            usage_log = self.get_user_usage(user_id)
            if usage_log:
                usage_log.remaining_uses = new_limit
                usage_log.reset_date = date.today()
                self.db.commit()
                
                logger.info(f"Usage reset for user {user_id} to {new_limit}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to reset usage for user {user_id}: {e}")
            self.db.rollback()
            return False
    
    def get_usage_statistics(self) -> Dict:
        """
        Get system-wide usage statistics (admin function).
        
        Returns:
            Dict: Usage statistics
        """
        try:
            # Total users by type
            total_users = self.db.query(User).filter(User.is_active == True).count()
            premium_users = self.db.query(User).filter(
                User.is_active == True,
                User.role.in_([UserRole.PREMIUM, UserRole.ADMIN])
            ).count()
            
            # Active premium subscriptions
            today = date.today()
            active_subscriptions = self.db.query(Subscription).filter(
                Subscription.is_active == True,
                Subscription.plan_type.in_([PlanType.MONTHLY_PREMIUM, PlanType.YEARLY_PREMIUM]),
                Subscription.start_date <= today,
                (Subscription.end_date.is_(None) | (Subscription.end_date >= today))
            ).count()
            
            # Usage statistics
            total_usage = self.db.query(func.sum(UsageLog.total_uses)).scalar() or 0
            avg_usage = self.db.query(func.avg(UsageLog.total_uses)).scalar() or 0
            
            # Users who hit the limit
            users_at_limit = self.db.query(UsageLog).filter(
                UsageLog.remaining_uses == 0
            ).count()
            
            return {
                "total_users": total_users,
                "premium_users": premium_users,
                "free_users": total_users - premium_users,
                "active_subscriptions": active_subscriptions,
                "total_usage": int(total_usage),
                "average_usage_per_user": round(float(avg_usage), 2),
                "users_at_limit": users_at_limit,
                "conversion_rate": round((active_subscriptions / total_users * 100), 2) if total_users > 0 else 0
            }
        except Exception as e:
            logger.error(f"Failed to get usage statistics: {e}")
            return {}
    
    def _create_usage_log(self, user_id: int) -> UsageLog:
        """
        Create a new usage log for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            UsageLog: Created usage log
        """
        usage_log = UsageLog(
            user_id=user_id,
            total_uses=0,
            remaining_uses=10  # Default free limit
        )
        self.db.add(usage_log)
        self.db.commit()
        self.db.refresh(usage_log)
        
        logger.info(f"Created usage log for user {user_id}")
        return usage_log

def get_usage_tracker(db: Session) -> UsageTracker:
    """
    Factory function to create UsageTracker instance.
    
    Args:
        db: Database session
        
    Returns:
        UsageTracker: Usage tracker instance
    """
    return UsageTracker(db)

class SubscriptionManager:
    """
    Manages subscription operations.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_subscription(
        self,
        user_id: int,
        plan_type: PlanType,
        duration_months: int = 1
    ) -> Subscription:
        """
        Create a new subscription for a user.
        
        Args:
            user_id: User ID
            plan_type: Type of subscription plan
            duration_months: Duration in months
            
        Returns:
            Subscription: Created subscription
        """
        # Deactivate existing subscriptions
        self.db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.is_active == True
        ).update({"is_active": False})
        
        # Calculate dates
        start_date = date.today()
        if plan_type == PlanType.FREE:
            end_date = None
            amount = 0.00
        elif plan_type == PlanType.MONTHLY_PREMIUM:
            end_date = date(start_date.year, start_date.month + duration_months, start_date.day)
            amount = 9.99 * duration_months
        elif plan_type == PlanType.YEARLY_PREMIUM:
            end_date = date(start_date.year + 1, start_date.month, start_date.day)
            amount = 99.99
        else:
            raise ValueError(f"Invalid plan type: {plan_type}")
        
        # Create new subscription
        subscription = Subscription(
            user_id=user_id,
            plan_type=plan_type,
            start_date=start_date,
            end_date=end_date,
            amount=amount,
            is_active=True
        )
        
        self.db.add(subscription)
        self.db.commit()
        self.db.refresh(subscription)
        
        # Update user role if premium
        if plan_type in [PlanType.MONTHLY_PREMIUM, PlanType.YEARLY_PREMIUM]:
            user = self.db.query(User).filter(User.user_id == user_id).first()
            if user and user.role == UserRole.NORMAL:
                user.role = UserRole.PREMIUM
                self.db.commit()
        
        logger.info(f"Created {plan_type.value} subscription for user {user_id}")
        return subscription
    
    def cancel_subscription(self, user_id: int) -> bool:
        """
        Cancel user's active subscription.
        
        Args:
            user_id: User ID
            
        Returns:
            bool: True if cancellation successful
        """
        try:
            subscription = self.db.query(Subscription).filter(
                Subscription.user_id == user_id,
                Subscription.is_active == True
            ).first()
            
            if subscription:
                subscription.is_active = False
                subscription.end_date = date.today()
                
                # Revert user role to normal if they were premium
                user = self.db.query(User).filter(User.user_id == user_id).first()
                if user and user.role == UserRole.PREMIUM:
                    user.role = UserRole.NORMAL
                
                self.db.commit()
                logger.info(f"Cancelled subscription for user {user_id}")
                return True
            
            return False
        except Exception as e:
            logger.error(f"Failed to cancel subscription for user {user_id}: {e}")
            self.db.rollback()
            return False

def get_subscription_manager(db: Session) -> SubscriptionManager:
    """
    Factory function to create SubscriptionManager instance.
    
    Args:
        db: Database session
        
    Returns:
        SubscriptionManager: Subscription manager instance
    """
    return SubscriptionManager(db)