"""
SQLAlchemy models for Speech Clarity Enhancement System.

This module defines all database models corresponding to the MySQL schema:
- User: Authentication and user management
- UsageLog: Track free vs premium usage limits
- Subscription: Premium plan management
- AudioHistory: Store processing results
- FluencyScore: Before/after metrics
- UserSession: JWT token management
- SystemSetting: Admin configuration
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Date, ForeignKey, Index, Enum as SQLEnum
from sqlalchemy.types import Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import enum

# Enum definitions for type safety
class UserRole(str, enum.Enum):
    NORMAL = "normal"
    PREMIUM = "premium"
    ADMIN = "admin"

class PlanType(str, enum.Enum):
    FREE = "free"
    MONTHLY_PREMIUM = "monthly_premium"
    YEARLY_PREMIUM = "yearly_premium"

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class OutputMode(str, enum.Enum):
    AUDIO = "audio"
    TEXT = "text"
    BOTH = "both"

class User(Base):
    """
    User model for authentication and user management.
    
    Attributes:
        user_id: Primary key
        name: User's full name
        email: Unique email address
        password_hash: Bcrypt hashed password
        role: User role (normal, premium, admin)
        created_at: Account creation timestamp
        last_login: Last login timestamp
        is_active: Account status flag
        email_verified: Email verification status
    """
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.NORMAL, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    
    # Relationships
    usage_logs = relationship("UsageLog", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    audio_history = relationship("AudioHistory", back_populates="user", cascade="all, delete-orphan")
    user_sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")

class UsageLog(Base):
    """
    Usage tracking for free vs premium limits.
    
    Attributes:
        usage_id: Primary key
        user_id: Foreign key to users table
        total_uses: Total number of enhancements used
        remaining_uses: Remaining free uses (10 for normal users)
        last_used_at: Last usage timestamp
        reset_date: Date for monthly resets (if needed)
    """
    __tablename__ = "usage_logs"
    
    usage_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    total_uses = Column(Integer, default=0)
    remaining_uses = Column(Integer, default=10)  # Free users get 10 uses
    last_used_at = Column(DateTime(timezone=True), nullable=True, index=True)
    reset_date = Column(Date, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="usage_logs")

class Subscription(Base):
    """
    Subscription management for premium plans.
    
    Attributes:
        subscription_id: Primary key
        user_id: Foreign key to users table
        plan_type: Type of subscription plan
        start_date: Subscription start date
        end_date: Subscription end date
        is_active: Active status flag
        payment_status: Payment processing status
        amount: Subscription amount
        currency: Payment currency
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "subscriptions"
    
    subscription_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    plan_type = Column(SQLEnum(PlanType), default=PlanType.FREE, index=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True, index=True)
    is_active = Column(Boolean, default=True, index=True)
    payment_status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)
    amount = Column(Numeric(10, 2), default=0.00)
    currency = Column(String(3), default="USD")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")
    
    # Composite index for common queries
    __table_args__ = (
        Index('idx_user_active_subscription', 'user_id', 'is_active', 'end_date'),
    )

class AudioHistory(Base):
    """
    Store processing results and file history.
    
    Attributes:
        audio_id: Primary key
        user_id: Foreign key to users table
        original_filename: Original uploaded filename
        original_audio_path: Path to original audio file
        enhanced_audio_path: Path to enhanced audio file
        transcript_raw: Raw ASR transcript
        transcript_cleaned: Cleaned transcript
        output_mode: Processing output mode
        processing_duration: Time taken to process (seconds)
        file_size_mb: File size in megabytes
        created_at: Processing timestamp
    """
    __tablename__ = "audio_history"
    
    audio_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    original_filename = Column(String(255), nullable=False)
    original_audio_path = Column(String(500), nullable=False)
    enhanced_audio_path = Column(String(500), nullable=True)
    transcript_raw = Column(Text, nullable=True)
    transcript_cleaned = Column(Text, nullable=True)
    output_mode = Column(SQLEnum(OutputMode), default=OutputMode.BOTH, index=True)
    processing_duration = Column(Numeric(5, 2), nullable=True)
    file_size_mb = Column(Numeric(8, 2), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    user = relationship("User", back_populates="audio_history")
    fluency_scores = relationship("FluencyScore", back_populates="audio_history", cascade="all, delete-orphan")
    
    # Index for recent history queries
    __table_args__ = (
        Index('idx_user_recent_history', 'user_id', 'created_at'),
    )

class FluencyScore(Base):
    """
    Store before/after fluency metrics.
    
    Attributes:
        score_id: Primary key
        audio_id: Foreign key to audio_history table
        before_score: Fluency score before processing
        after_score: Fluency score after processing
        repetition_count_before: Word repetitions before
        repetition_count_after: Word repetitions after
        filler_count_before: Filler words before
        filler_count_after: Filler words after
        pause_count_before: Pauses before
        pause_count_after: Pauses after
        total_words_before: Total words before
        total_words_after: Total words after
        improvement_score: Calculated improvement (after - before)
        created_at: Metrics calculation timestamp
    """
    __tablename__ = "fluency_scores"
    
    score_id = Column(Integer, primary_key=True, index=True)
    audio_id = Column(Integer, ForeignKey("audio_history.audio_id", ondelete="CASCADE"), nullable=False, index=True)
    before_score = Column(Numeric(5, 2), nullable=False, index=True)
    after_score = Column(Numeric(5, 2), nullable=False, index=True)
    repetition_count_before = Column(Integer, default=0)
    repetition_count_after = Column(Integer, default=0)
    filler_count_before = Column(Integer, default=0)
    filler_count_after = Column(Integer, default=0)
    pause_count_before = Column(Integer, default=0)
    pause_count_after = Column(Integer, default=0)
    total_words_before = Column(Integer, default=0)
    total_words_after = Column(Integer, default=0)
    improvement_score = Column(Numeric(5, 2), nullable=True, index=True)  # Calculated field
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    audio_history = relationship("AudioHistory", back_populates="fluency_scores")

class UserSession(Base):
    """
    JWT token management and session tracking.
    
    Attributes:
        session_id: Primary key
        user_id: Foreign key to users table
        token_hash: Hashed JWT token for security
        expires_at: Token expiration timestamp
        created_at: Session creation timestamp
        is_active: Session active status
        user_agent: Browser/client user agent
        ip_address: Client IP address
    """
    __tablename__ = "user_sessions"
    
    session_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(255), nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True, index=True)
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)  # Supports both IPv4 and IPv6
    
    # Relationships
    user = relationship("User", back_populates="user_sessions")

class SystemSetting(Base):
    """
    System configuration and admin settings.
    
    Attributes:
        setting_id: Primary key
        setting_key: Unique setting identifier
        setting_value: Setting value (stored as text)
        description: Human-readable description
        updated_by: User who last updated the setting
        updated_at: Last update timestamp
    """
    __tablename__ = "system_settings"
    
    setting_id = Column(Integer, primary_key=True, index=True)
    setting_key = Column(String(100), unique=True, nullable=False, index=True)
    setting_value = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    updated_by = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    updated_by_user = relationship("User", foreign_keys=[updated_by])