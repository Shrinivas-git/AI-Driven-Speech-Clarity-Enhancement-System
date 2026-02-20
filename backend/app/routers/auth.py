"""
Authentication API routes.

This module provides endpoints for:
- User registration
- User login
- User logout
- Password management
- Token validation
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import timedelta
import logging

from ..database import get_database
from ..models import User, UsageLog, Subscription, UserRole, PlanType
from ..auth import (
    hash_password, authenticate_user, create_access_token, 
    create_user_session, get_current_active_user, logout_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from ..schemas import (
    UserRegister, UserLogin, Token, UserResponse, 
    PasswordChange, SuccessResponse, ErrorResponse
)

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserRegister,
    request: Request,
    db: Session = Depends(get_database)
):
    """
    Register a new user account.
    
    Creates a new user with:
    - Hashed password
    - Default 'normal' role
    - Initial usage log (10 free uses)
    - Free subscription plan
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    try:
        # Create new user
        hashed_password = hash_password(user_data.password)
        new_user = User(
            name=user_data.name,
            email=user_data.email,
            password_hash=hashed_password,
            role=UserRole.NORMAL,
            is_active=True,
            email_verified=False  # In production, implement email verification
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"New user registered: {new_user.email} (ID: {new_user.user_id})")
        
        # Note: UsageLog and Subscription are created automatically via database triggers
        # But we'll create them manually to ensure they exist
        
        # Create usage log
        usage_log = UsageLog(
            user_id=new_user.user_id,
            total_uses=0,
            remaining_uses=10
        )
        db.add(usage_log)
        
        # Create free subscription
        from datetime import date
        subscription = Subscription(
            user_id=new_user.user_id,
            plan_type=PlanType.FREE,
            start_date=date.today(),
            is_active=True
        )
        db.add(subscription)
        
        db.commit()
        
        return UserResponse.from_orm(new_user)
        
    except Exception as e:
        db.rollback()
        logger.error(f"User registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again."
        )

@router.post("/login", response_model=Token)
async def login_user(
    user_credentials: UserLogin,
    request: Request,
    db: Session = Depends(get_database)
):
    """
    Authenticate user and return JWT token.
    
    Returns:
    - JWT access token
    - Token type (bearer)
    - Expiration time in seconds
    """
    # Authenticate user
    user = authenticate_user(db, user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is deactivated"
        )
    
    try:
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.user_id), "email": user.email},  # Convert user_id to string
            expires_delta=access_token_expires
        )
        
        # Create session record
        create_user_session(db, user, access_token, request)
        
        logger.info(f"User logged in: {user.email} (ID: {user.user_id})")
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convert to seconds
        )
        
    except Exception as e:
        logger.error(f"Login failed for {user_credentials.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again."
        )

@router.post("/logout", response_model=SuccessResponse)
async def logout_user_endpoint(
    current_user: User = Depends(get_current_active_user),
    credentials = Depends(security),
    db: Session = Depends(get_database)
):
    """
    Logout user by invalidating their session.
    """
    try:
        success = logout_user(db, credentials.credentials)
        if success:
            logger.info(f"User logged out: {current_user.email}")
            return SuccessResponse(
                message="Successfully logged out"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Logout failed"
            )
    except Exception as e:
        logger.error(f"Logout error for user {current_user.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed. Please try again."
        )

@router.post("/change-password", response_model=SuccessResponse)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """
    Change user password.
    
    Requires current password for verification.
    """
    from ..auth import verify_password
    
    # Verify current password
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    try:
        # Update password
        new_password_hash = hash_password(password_data.new_password)
        current_user.password_hash = new_password_hash
        
        db.commit()
        
        logger.info(f"Password changed for user: {current_user.email}")
        
        return SuccessResponse(
            message="Password changed successfully"
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Password change failed for user {current_user.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed. Please try again."
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user information.
    
    Returns user profile data for the authenticated user.
    """
    return UserResponse.from_orm(current_user)

@router.get("/validate-token")
async def validate_token(
    current_user: User = Depends(get_current_active_user)
):
    """
    Validate JWT token.
    
    Returns user information if token is valid.
    Used by frontend to check authentication status.
    """
    return {
        "valid": True,
        "user_id": current_user.user_id,
        "email": current_user.email,
        "role": current_user.role.value,
        "name": current_user.name
    }