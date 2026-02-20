"""
Pydantic schemas for API request/response models.

This module defines all the data models used for API serialization:
- Authentication schemas (login, register, token)
- User management schemas
- Audio processing schemas
- Subscription schemas
- Admin schemas
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, validator
from .models import UserRole, PlanType, PaymentStatus, OutputMode

# ===================================================
# AUTHENTICATION SCHEMAS
# ===================================================

class UserRegister(BaseModel):
    """Schema for user registration."""
    name: str = Field(..., min_length=2, max_length=100, description="Full name")
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=6, max_length=100, description="Password (min 6 characters)")
    
    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()

class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., description="Password")

class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Token expiration time in seconds")

class TokenData(BaseModel):
    """Schema for token payload data."""
    user_id: Optional[int] = None
    email: Optional[str] = None

# ===================================================
# USER SCHEMAS
# ===================================================

class UserBase(BaseModel):
    """Base user schema with common fields."""
    name: str
    email: EmailStr
    role: UserRole

class UserResponse(UserBase):
    """Schema for user response data."""
    user_id: int
    is_active: bool
    email_verified: bool
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    """Schema for updating user information."""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    
    @validator('name')
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip() if v else v

class PasswordChange(BaseModel):
    """Schema for password change."""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=6, max_length=100, description="New password")

# ===================================================
# USAGE AND SUBSCRIPTION SCHEMAS
# ===================================================

class UsageInfo(BaseModel):
    """Schema for user usage information."""
    total_uses: int
    remaining_uses: int
    is_premium: bool
    last_used_at: Optional[datetime]
    user_role: str
    
    class Config:
        from_attributes = True

class SubscriptionResponse(BaseModel):
    """Schema for subscription information."""
    subscription_id: int
    plan_type: PlanType
    start_date: date
    end_date: Optional[date]
    is_active: bool
    amount: float
    currency: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class SubscriptionCreate(BaseModel):
    """Schema for creating a subscription."""
    plan_type: PlanType = Field(..., description="Subscription plan type")
    duration_months: int = Field(1, ge=1, le=12, description="Duration in months (1-12)")

class PricingPlan(BaseModel):
    """Schema for pricing plan information."""
    plan_type: PlanType
    name: str
    price: float
    currency: str
    duration: str
    features: List[str]
    is_popular: bool = False

# ===================================================
# AUDIO PROCESSING SCHEMAS
# ===================================================

class AudioProcessRequest(BaseModel):
    """Schema for audio processing request."""
    output_mode: OutputMode = Field(OutputMode.BOTH, description="Output mode: audio, text, or both")
    calculate_metrics: bool = Field(True, description="Whether to calculate fluency metrics")
    realtime: bool = Field(False, description="Whether this is a real-time recording")

class FluencyMetrics(BaseModel):
    """Schema for fluency metrics."""
    repetitions: int
    fillers: int
    pauses: int
    grammar_errors: int
    total_words: int
    fluency_score: float

class FluencyComparison(BaseModel):
    """Schema for before/after fluency comparison."""
    before: FluencyMetrics
    after: FluencyMetrics
    improvement: Dict[str, float]

class AudioProcessResponse(BaseModel):
    """Schema for audio processing response."""
    audio_id: int
    cleaned_text: Optional[str] = None
    raw_text: Optional[str] = None
    enhanced_audio_filename: Optional[str] = None
    fluency_metrics: Optional[FluencyComparison] = None
    processing_duration: Optional[float] = None
    usage_info: UsageInfo
    message: str

# ===================================================
# HISTORY SCHEMAS
# ===================================================

class AudioHistoryResponse(BaseModel):
    """Schema for audio history item."""
    audio_id: int
    original_filename: str
    transcript_raw: Optional[str]
    transcript_cleaned: Optional[str]
    output_mode: OutputMode
    processing_duration: Optional[float]
    file_size_mb: Optional[float]
    created_at: datetime
    fluency_scores: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

class AudioHistoryList(BaseModel):
    """Schema for paginated audio history."""
    items: List[AudioHistoryResponse]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool

# ===================================================
# DASHBOARD SCHEMAS
# ===================================================

class UserDashboard(BaseModel):
    """Schema for user dashboard data."""
    user_info: UserResponse
    usage_info: UsageInfo
    subscription_info: Optional[SubscriptionResponse]
    recent_activity: List[AudioHistoryResponse]
    statistics: Dict[str, Any]

class UserStatistics(BaseModel):
    """Schema for user statistics."""
    total_processed_files: int
    total_processing_time: float
    average_improvement_score: float
    most_active_day: Optional[str]
    files_this_month: int
    improvement_trend: List[Dict[str, Any]]

# ===================================================
# ADMIN SCHEMAS
# ===================================================

class AdminUserResponse(UserResponse):
    """Extended user schema for admin views."""
    usage_info: UsageInfo
    subscription_info: Optional[SubscriptionResponse]
    total_processed_files: int
    last_activity: Optional[datetime]

class AdminUsersList(BaseModel):
    """Schema for admin users list."""
    items: List[AdminUserResponse]
    total: int
    page: int
    per_page: int

class SystemStatistics(BaseModel):
    """Schema for system-wide statistics."""
    total_users: int
    premium_users: int
    free_users: int
    active_subscriptions: int
    total_usage: int
    average_usage_per_user: float
    users_at_limit: int
    conversion_rate: float
    recent_signups: int
    revenue_this_month: float

class AdminUserUpdate(BaseModel):
    """Schema for admin user updates."""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    reset_usage: Optional[bool] = Field(False, description="Reset user's usage limit")
    new_usage_limit: Optional[int] = Field(10, ge=0, le=1000, description="New usage limit")

# ===================================================
# SYSTEM SETTINGS SCHEMAS
# ===================================================

class SystemSettingResponse(BaseModel):
    """Schema for system setting."""
    setting_key: str
    setting_value: str
    description: Optional[str]
    updated_at: datetime
    
    class Config:
        from_attributes = True

class SystemSettingUpdate(BaseModel):
    """Schema for updating system setting."""
    setting_value: str = Field(..., description="New setting value")

# ===================================================
# ERROR SCHEMAS
# ===================================================

class ErrorResponse(BaseModel):
    """Schema for error responses."""
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None

class ValidationErrorResponse(BaseModel):
    """Schema for validation error responses."""
    error: str = "Validation Error"
    details: List[Dict[str, Any]]

# ===================================================
# SUCCESS SCHEMAS
# ===================================================

class SuccessResponse(BaseModel):
    """Schema for success responses."""
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None

class MessageResponse(BaseModel):
    """Schema for simple message responses."""
    message: str