"""
Authentication and authorization system for Speech Clarity Enhancement.

This module provides:
- Password hashing and verification using bcrypt
- JWT token creation and validation
- User authentication middleware
- Role-based access control
- Session management
"""

import os
import hashlib
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from .database import get_database
from .models import User, UserSession, UserRole
import logging

logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# JWT token security
security = HTTPBearer()

class AuthenticationError(Exception):
    """Custom exception for authentication errors."""
    pass

class AuthorizationError(Exception):
    """Custom exception for authorization errors."""
    pass

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt directly.
    
    Args:
        password: Plain text password
        
    Returns:
        str: Hashed password
    """
    # Truncate to 72 bytes for bcrypt compatibility
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash using bcrypt directly.
    
    Args:
        plain_password: Plain text password
        hashed_password: Bcrypt hashed password
        
    Returns:
        bool: True if password matches, False otherwise
    """
    try:
        password_bytes = plain_password.encode('utf-8')[:72]
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Payload data to encode in token
        expires_delta: Token expiration time (default: 7 days)
        
    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Dict: Decoded token payload
        
    Raises:
        AuthenticationError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        logger.warning(f"JWT verification failed: {e}")
        raise AuthenticationError("Invalid or expired token")

def hash_token(token: str) -> str:
    """
    Create a hash of the token for secure storage.
    
    Args:
        token: JWT token string
        
    Returns:
        str: SHA256 hash of the token
    """
    return hashlib.sha256(token.encode()).hexdigest()

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    Authenticate a user with email and password.
    
    Args:
        db: Database session
        email: User email
        password: Plain text password
        
    Returns:
        User: User object if authentication successful, None otherwise
    """
    user = db.query(User).filter(User.email == email, User.is_active == True).first()
    if not user:
        return None
    
    if not verify_password(password, user.password_hash):
        return None
    
    return user

def create_user_session(
    db: Session, 
    user: User, 
    token: str, 
    request: Request
) -> UserSession:
    """
    Create a new user session record.
    
    Args:
        db: Database session
        user: User object
        token: JWT token
        request: FastAPI request object
        
    Returns:
        UserSession: Created session record
    """
    # Calculate token expiration
    expires_at = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Get client information
    user_agent = request.headers.get("user-agent", "")
    ip_address = request.client.host if request.client else "unknown"
    
    # Create session record
    session = UserSession(
        user_id=user.user_id,
        token_hash=hash_token(token),
        expires_at=expires_at,
        user_agent=user_agent,
        ip_address=ip_address
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return session

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_database)
) -> User:
    """
    Get the current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer token credentials
        db: Database session
        
    Returns:
        User: Current authenticated user
        
    Raises:
        HTTPException: If authentication fails
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify token
        payload = verify_token(credentials.credentials)
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        
        # Convert string back to int
        try:
            user_id = int(user_id_str)
        except (ValueError, TypeError):
            raise credentials_exception
            
    except AuthenticationError:
        raise credentials_exception
    
    # Check if session exists and is active
    token_hash = hash_token(credentials.credentials)
    session = db.query(UserSession).filter(
        UserSession.token_hash == token_hash,
        UserSession.is_active == True,
        UserSession.expires_at > datetime.utcnow()
    ).first()
    
    if not session:
        raise credentials_exception
    
    # Get user
    user = db.query(User).filter(
        User.user_id == user_id,
        User.is_active == True
    ).first()
    
    if user is None:
        raise credentials_exception
    
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get current active user (additional check for account status).
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User: Current active user
        
    Raises:
        HTTPException: If user account is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )
    return current_user

def require_role(required_role: UserRole):
    """
    Dependency factory for role-based access control.
    
    Args:
        required_role: Minimum required user role
        
    Returns:
        Function: Dependency function that checks user role
    """
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        # Define role hierarchy
        role_hierarchy = {
            UserRole.NORMAL: 1,
            UserRole.PREMIUM: 2,
            UserRole.ADMIN: 3
        }
        
        user_level = role_hierarchy.get(current_user.role, 0)
        required_level = role_hierarchy.get(required_role, 999)
        
        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {required_role.value}"
            )
        
        return current_user
    
    return role_checker

def logout_user(db: Session, token: str) -> bool:
    """
    Logout user by deactivating their session.
    
    Args:
        db: Database session
        token: JWT token to invalidate
        
    Returns:
        bool: True if logout successful, False otherwise
    """
    try:
        token_hash = hash_token(token)
        session = db.query(UserSession).filter(
            UserSession.token_hash == token_hash,
            UserSession.is_active == True
        ).first()
        
        if session:
            session.is_active = False
            db.commit()
            return True
        
        return False
    except Exception as e:
        logger.error(f"Logout error: {e}")
        db.rollback()
        return False

def cleanup_expired_sessions(db: Session) -> int:
    """
    Clean up expired sessions from the database.
    
    Args:
        db: Database session
        
    Returns:
        int: Number of sessions cleaned up
    """
    try:
        expired_sessions = db.query(UserSession).filter(
            UserSession.expires_at < datetime.utcnow()
        )
        count = expired_sessions.count()
        expired_sessions.update({"is_active": False})
        db.commit()
        
        logger.info(f"Cleaned up {count} expired sessions")
        return count
    except Exception as e:
        logger.error(f"Session cleanup error: {e}")
        db.rollback()
        return 0

# Optional: Dependency for admin-only endpoints
require_admin = require_role(UserRole.ADMIN)

# Optional: Dependency for premium users
require_premium = require_role(UserRole.PREMIUM)