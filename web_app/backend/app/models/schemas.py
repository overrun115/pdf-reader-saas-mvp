from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Enums
class UserTierSchema(str, Enum):
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class FileStatusSchema(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class OutputFormatSchema(str, Enum):
    EXCEL = "excel"
    CSV = "csv"
    WORD = "word"
    BOTH = "both"

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    tier: UserTierSchema
    subscription_active: bool
    files_processed_this_month: int
    total_files_processed: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None

# Authentication Schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None

# File Schemas
class FileUploadResponse(BaseModel):
    id: int
    original_filename: str
    file_size: int
    status: FileStatusSchema
    created_at: datetime

class FileProcessRequest(BaseModel):
    output_format: OutputFormatSchema = OutputFormatSchema.EXCEL

class ProcessedFileResponse(BaseModel):
    id: int
    original_filename: str
    file_size: int
    status: FileStatusSchema
    output_format: OutputFormatSchema
    tables_found: int
    total_rows: int
    processing_time: Optional[float]
    error_message: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    download_url: Optional[str] = None
    
    class Config:
        from_attributes = True

# Dashboard Schemas
class UserStats(BaseModel):
    files_processed_today: int
    files_processed_this_month: int
    total_files_processed: int
    tier: UserTierSchema
    tier_limit: int
    remaining_files: int

class RecentFile(BaseModel):
    id: int
    original_filename: str
    status: FileStatusSchema
    tables_found: int
    created_at: datetime
    download_url: Optional[str] = None

class DashboardResponse(BaseModel):
    user_stats: UserStats
    recent_files: List[RecentFile]

# Admin Schemas
class AdminUserResponse(UserResponse):
    hashed_password: str
    subscription_id: Optional[str]

class AdminStats(BaseModel):
    total_users: int
    active_users: int
    total_files_processed: int
    files_processed_today: int
    files_by_tier: dict

# Password Reset
class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str
    new_password: str
    
    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

# API Response Wrappers
class ResponseModel(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    error_code: Optional[str] = None

# Stripe/Payment Schemas
class SubscriptionPlan(BaseModel):
    tier: UserTierSchema
    name: str
    price: float
    price_id: str
    features: List[str]
    files_per_month: int

class CreateCheckoutRequest(BaseModel):
    price_id: str
    success_url: str
    cancel_url: str

class CheckoutResponse(BaseModel):
    checkout_url: str
    session_id: str

class BillingPortalRequest(BaseModel):
    return_url: str

class BillingPortalResponse(BaseModel):
    portal_url: str

class SubscriptionStatus(BaseModel):
    tier: UserTierSchema
    subscription_active: bool
    subscription_id: Optional[str]
    subscription_end_date: Optional[datetime]
    stripe_customer_id: Optional[str]

class WebhookEvent(BaseModel):
    type: str
    data: dict

# Trial Schemas
class TrialFileUploadResponse(BaseModel):
    session_id: str
    file_id: str
    filename: str
    message: str
    remaining_uploads: int

class TrialLimitations(BaseModel):
    max_tables: int
    max_rows_per_table: int
    download_requires_email: bool

class TableData(BaseModel):
    data: List[List[str]]
    headers: Optional[List[str]] = None
    table_index: int
    trial_message: Optional[str] = None

class FileProcessResult(BaseModel):
    tables: List[TableData]
    total_tables_found: int
    processing_time: Optional[float] = None
    is_trial: bool = False
    trial_limitations: Optional[TrialLimitations] = None
    trial_message: Optional[str] = None

class TrialDownloadRequest(BaseModel):
    email: str
    format: OutputFormatSchema = OutputFormatSchema.EXCEL
    selected_tables: Optional[List[int]] = None

class TrialDownloadResponse(BaseModel):
    message: str
    download_token: str
    expires_in: str

class TrialSessionInfo(BaseModel):
    session_id: str
    created_at: str
    files_uploaded: int
    remaining_uploads: int
    email: Optional[str] = None
    files: List[dict]

# Table Editor Schemas
class EditableTableCreate(BaseModel):
    table_index: int
    table_name: Optional[str] = None
    original_data: List[List[str]]
    edited_data: List[List[str]]
    headers: Optional[List[str]] = None

class EditableTableUpdate(BaseModel):
    table_name: Optional[str] = None
    edited_data: List[List[str]]
    headers: Optional[List[str]] = None

class EditableTableResponse(BaseModel):
    id: int
    file_id: int
    table_index: int
    table_name: Optional[str]
    original_data: List[List[str]]
    edited_data: List[List[str]]
    headers: Optional[List[str]]
    rows_count: int
    columns_count: int
    has_changes: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class TableEditorData(BaseModel):
    table_index: int
    table_name: Optional[str] = None
    data: List[List[str]]
    headers: Optional[List[str]] = None
    rows_count: int
    columns_count: int
    has_changes: bool = False

class FileTablesResponse(BaseModel):
    file_id: int
    filename: str
    tables: List[TableEditorData]
    total_tables: int

class CellUpdateRequest(BaseModel):
    row_index: int
    col_index: int
    value: str

class RowColumnOperationRequest(BaseModel):
    operation: str  # 'add_row', 'delete_row', 'add_column', 'delete_column'
    index: int
    data: Optional[List[str]] = None  # For add operations

class TableExportRequest(BaseModel):
    format: OutputFormatSchema = OutputFormatSchema.EXCEL
    selected_tables: Optional[List[int]] = None  # If None, export all tables