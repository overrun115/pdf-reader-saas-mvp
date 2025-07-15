from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

# Document intelligence enums will be imported after Base is defined

Base = declarative_base()

class UserTier(str, enum.Enum):
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class FileStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class OutputFormat(str, enum.Enum):
    EXCEL = "excel"
    CSV = "csv"
    BOTH = "both"

# Document Intelligence Enums
class DocumentType(str, enum.Enum):
    PDF = "pdf"
    WORD = "word"
    EXCEL = "excel"
    HTML = "html"
    TEXT = "text"
    CSV = "csv"

class ProcessingType(str, enum.Enum):
    OCR_ANALYSIS = "ocr_analysis"
    LAYOUT_ANALYSIS = "layout_analysis"
    VALIDATION_ANALYSIS = "validation_analysis"
    COMPLETE_ANALYSIS = "complete_analysis"
    WORD_INTELLIGENCE = "word_intelligence"
    EXCEL_INTELLIGENCE = "excel_intelligence"
    DOCUMENT_CONVERSION = "document_conversion"

class ProcessingStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class QualityLevel(str, enum.Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    UNKNOWN = "unknown"

# Enterprise Enums
class TenantStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    INACTIVE = "inactive"
    TRIAL = "trial"

class TenantTier(str, enum.Enum):
    STARTUP = "startup"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"

class IntegrationType(str, enum.Enum):
    CRM_SALESFORCE = "crm_salesforce"
    CRM_HUBSPOT = "crm_hubspot"
    ERP_SAP = "erp_sap"
    ERP_ORACLE = "erp_oracle"
    DMS_SHAREPOINT = "dms_sharepoint"
    DMS_DROPBOX = "dms_dropbox"

class SecurityLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ComplianceStandard(str, enum.Enum):
    GDPR = "gdpr"
    HIPAA = "hipaa"
    SOX = "sox"
    PCI_DSS = "pci_dss"
    ISO_27001 = "iso_27001"
    SOC_2 = "soc_2"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    
    # Subscription info
    tier = Column(Enum(UserTier), default=UserTier.FREE)
    subscription_id = Column(String, nullable=True)  # Stripe subscription ID
    subscription_active = Column(Boolean, default=True)
    stripe_customer_id = Column(String, nullable=True)  # Stripe customer ID
    subscription_end_date = Column(DateTime(timezone=True), nullable=True)  # When current subscription ends
    
    # Usage tracking
    files_processed_this_month = Column(Integer, default=0)
    total_files_processed = Column(Integer, default=0)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    email_verification_token = Column(String, nullable=True)
    email_verification_token_expires = Column(DateTime(timezone=True), nullable=True)
    password_reset_token = Column(String, nullable=True)
    password_reset_token_expires = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    files = relationship("ProcessedFile", back_populates="user")

class ProcessedFile(Base):
    __tablename__ = "processed_files"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # File info
    original_filename = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)  # Size in bytes
    file_hash = Column(String, nullable=False)   # For deduplication
    file_type = Column(String, nullable=False, default='pdf')  # 'pdf' o 'image'
    
    # Processing info
    status = Column(Enum(FileStatus), default=FileStatus.UPLOADED)
    output_format = Column(Enum(OutputFormat), default=OutputFormat.EXCEL)
    
    # Results
    tables_found = Column(Integer, default=0)
    total_rows = Column(Integer, default=0)
    processing_time = Column(Float, nullable=True)  # Time in seconds
    
    # File paths
    input_file_path = Column(String, nullable=False)
    output_file_path = Column(String, nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="files")
    editable_tables = relationship("EditableTableData", back_populates="file", cascade="all, delete-orphan")

class EditableTableData(Base):
    __tablename__ = "editable_table_data"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("processed_files.id", ondelete="CASCADE"), nullable=False)
    
    # Table identification
    table_index = Column(Integer, nullable=False)  # Table number within the file
    table_name = Column(String, nullable=True)     # User-defined table name
    
    # Table data
    original_data = Column(JSON, nullable=False)   # Original extracted data
    edited_data = Column(JSON, nullable=False)     # Current edited data
    previous_data = Column(JSON, nullable=True)    # Previous state for undo functionality
    headers = Column(JSON, nullable=True)          # Column headers
    
    # Metadata
    rows_count = Column(Integer, default=0)
    columns_count = Column(Integer, default=0)
    has_changes = Column(Boolean, default=False)   # Quick check if table was modified
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    file = relationship("ProcessedFile", back_populates="editable_tables")

class APIKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    key_name = Column(String, nullable=False)
    key_hash = Column(String, nullable=False)
    key_prefix = Column(String, nullable=False)  # First 8 chars for display
    
    # Usage tracking
    requests_made = Column(Integer, default=0)
    last_used = Column(DateTime(timezone=True), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)

class UsageLog(Base):
    __tablename__ = "usage_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Action info
    action = Column(String, nullable=False)  # "file_upload", "file_process", etc.
    details = Column(Text, nullable=True)    # JSON string with additional info
    
    # Request info
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    api_key_used = Column(String, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# DOCUMENT INTELLIGENCE MODELS

class DocumentIntelligenceAnalysis(Base):
    """
    Table to store document intelligence analysis results
    """
    __tablename__ = "document_intelligence_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Document info
    original_filename = Column(String, nullable=False)
    document_type = Column(Enum(DocumentType), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_hash = Column(String, nullable=False)
    
    # Processing info
    processing_type = Column(Enum(ProcessingType), nullable=False)
    status = Column(Enum(ProcessingStatus), default=ProcessingStatus.PENDING)
    processing_time = Column(Float, nullable=True)
    
    # Quality metrics
    confidence_score = Column(Float, nullable=True)
    quality_level = Column(Enum(QualityLevel), nullable=True)
    
    # Analysis results (stored as JSON)
    analysis_results = Column(JSON, nullable=True)
    document_metadata = Column(JSON, nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    warnings = Column(JSON, nullable=True)  # Array of warning messages
    
    # File paths
    input_file_path = Column(String, nullable=False)
    output_file_path = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

class DocumentConversion(Base):
    """
    Table to store document conversion operations
    """
    __tablename__ = "document_conversions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    source_analysis_id = Column(Integer, ForeignKey("document_intelligence_analysis.id"), nullable=True)
    
    # Conversion info
    source_format = Column(Enum(DocumentType), nullable=False)
    target_format = Column(Enum(DocumentType), nullable=False)
    conversion_method = Column(String, nullable=True)  # e.g., "pdf_to_word_advanced"
    
    # File info
    source_filename = Column(String, nullable=False)
    output_filename = Column(String, nullable=True)
    source_file_size = Column(Integer, nullable=False)
    output_file_size = Column(Integer, nullable=True)
    
    # Processing metrics
    status = Column(Enum(ProcessingStatus), default=ProcessingStatus.PENDING)
    processing_time = Column(Float, nullable=True)
    conversion_time = Column(Float, nullable=True)
    quality_score = Column(Float, nullable=True)
    
    # Conversion options and results
    conversion_options = Column(JSON, nullable=True)
    conversion_metadata = Column(JSON, nullable=True)
    warnings = Column(JSON, nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    
    # File paths
    source_file_path = Column(String, nullable=False)
    output_file_path = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

class WordDocumentAnalysis(Base):
    """
    Detailed analysis results for Word documents
    """
    __tablename__ = "word_document_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("document_intelligence_analysis.id"), nullable=False)
    
    # Document structure metrics
    total_paragraphs = Column(Integer, default=0)
    total_tables = Column(Integer, default=0)
    total_sections = Column(Integer, default=0)
    total_images = Column(Integer, default=0)
    
    # Content metrics
    word_count = Column(Integer, default=0)
    character_count = Column(Integer, default=0)
    estimated_pages = Column(Integer, default=0)
    
    # Style analysis
    styles_used = Column(JSON, nullable=True)  # Dict of style name -> count
    fonts_used = Column(JSON, nullable=True)   # Dict of font name -> count
    formatting_issues = Column(JSON, nullable=True)  # Array of issues
    consistency_score = Column(Float, nullable=True)
    
    # Quality assessment
    structure_score = Column(Float, nullable=True)
    format_score = Column(Float, nullable=True)
    content_score = Column(Float, nullable=True)
    overall_quality_score = Column(Float, nullable=True)
    
    # NLP analysis (if available)
    entities_found = Column(JSON, nullable=True)
    sentence_count = Column(Integer, nullable=True)
    avg_sentence_length = Column(Float, nullable=True)
    
    # Recommendations
    quality_recommendations = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ExcelDocumentAnalysis(Base):
    """
    Detailed analysis results for Excel documents
    """
    __tablename__ = "excel_document_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("document_intelligence_analysis.id"), nullable=False)
    
    # Workbook structure
    total_worksheets = Column(Integer, default=0)
    total_rows = Column(Integer, default=0)
    total_columns = Column(Integer, default=0)
    total_cells_with_data = Column(Integer, default=0)
    
    # Data analysis
    data_model_detected = Column(String, nullable=True)  # financial, inventory, etc.
    data_model_confidence = Column(Float, nullable=True)
    
    # Formula analysis
    total_formulas = Column(Integer, default=0)
    formula_types = Column(JSON, nullable=True)  # Dict of formula type -> count
    formula_complexity_score = Column(Float, nullable=True)
    
    # Data quality metrics
    data_quality_score = Column(Float, nullable=True)
    missing_data_percentage = Column(Float, nullable=True)
    duplicate_rows_count = Column(Integer, default=0)
    
    # Pattern analysis
    data_patterns = Column(JSON, nullable=True)
    column_types = Column(JSON, nullable=True)
    correlations = Column(JSON, nullable=True)
    
    # Anomaly detection
    outliers_detected = Column(JSON, nullable=True)
    anomaly_score = Column(Float, nullable=True)
    
    # Recommendations
    optimization_recommendations = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ProcessingStatistics(Base):
    """
    Aggregate statistics for processing operations
    """
    __tablename__ = "processing_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Time period (monthly aggregation)
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Document processing counts
    pdf_analyses = Column(Integer, default=0)
    word_analyses = Column(Integer, default=0)
    excel_analyses = Column(Integer, default=0)
    total_analyses = Column(Integer, default=0)
    
    # Conversion counts
    pdf_conversions = Column(Integer, default=0)
    word_conversions = Column(Integer, default=0)
    excel_conversions = Column(Integer, default=0)
    total_conversions = Column(Integer, default=0)
    
    # Processing metrics
    total_processing_time = Column(Float, default=0.0)
    avg_processing_time = Column(Float, default=0.0)
    total_files_processed = Column(Integer, default=0)
    
    # Success rates
    successful_analyses = Column(Integer, default=0)
    failed_analyses = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    
    # Quality metrics
    avg_confidence_score = Column(Float, default=0.0)
    avg_quality_score = Column(Float, default=0.0)
    
    # Storage metrics
    total_storage_used = Column(Integer, default=0)  # bytes
    avg_file_size = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class FeatureUsage(Base):
    """
    Track usage of specific features for analytics and billing
    """
    __tablename__ = "feature_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Feature info
    feature_name = Column(String, nullable=False)  # e.g., "advanced_ocr", "word_analysis"
    feature_category = Column(String, nullable=False)  # e.g., "analysis", "conversion"
    
    # Usage metrics
    usage_count = Column(Integer, default=1)
    processing_time = Column(Float, nullable=True)
    success = Column(Boolean, default=True)
    
    # Context
    document_type = Column(Enum(DocumentType), nullable=True)
    file_size = Column(Integer, nullable=True)
    
    # Additional metadata
    analysis_metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# ==========================================
# ENTERPRISE MULTI-TENANCY TABLES
# ==========================================

class Tenant(Base):
    """
    Multi-tenant organization table
    """
    __tablename__ = "tenants"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_uuid = Column(String, unique=True, index=True, nullable=False)
    
    # Organization info
    organization_name = Column(String, nullable=False)
    domain = Column(String, unique=True, nullable=False)
    subdomain = Column(String, unique=True, nullable=True)
    
    # Tenant configuration
    tier = Column(Enum(TenantTier), default=TenantTier.STARTUP)
    status = Column(Enum(TenantStatus), default=TenantStatus.TRIAL)
    max_users = Column(Integer, default=5)
    max_storage_gb = Column(Integer, default=10)
    
    # Billing info
    billing_email = Column(String, nullable=True)
    subscription_id = Column(String, nullable=True)
    billing_cycle = Column(String, default="monthly")  # monthly, yearly
    trial_end_date = Column(DateTime(timezone=True), nullable=True)
    
    # Configuration
    settings = Column(JSON, default={})
    features_enabled = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    users = relationship("TenantUser", back_populates="tenant")
    integrations = relationship("EnterpriseIntegration", back_populates="tenant")

class TenantUser(Base):
    """
    Users within a tenant organization
    """
    __tablename__ = "tenant_users"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Role and permissions
    role = Column(String, default="user")  # admin, user, viewer
    permissions = Column(JSON, default=[])
    department = Column(String, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    invitation_accepted = Column(Boolean, default=False)
    invitation_token = Column(String, nullable=True)
    
    # Timestamps
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    last_active = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    user = relationship("User")

class EnterpriseIntegration(Base):
    """
    Enterprise integrations (CRM, ERP, etc.)
    """
    __tablename__ = "enterprise_integrations"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    
    # Integration details
    integration_name = Column(String, nullable=False)
    integration_type = Column(Enum(IntegrationType), nullable=False)
    endpoint_url = Column(String, nullable=False)
    
    # Authentication
    api_key_encrypted = Column(Text, nullable=True)
    oauth_token_encrypted = Column(Text, nullable=True)
    credentials_metadata = Column(JSON, default={})
    
    # Configuration
    sync_enabled = Column(Boolean, default=True)
    sync_frequency = Column(String, default="daily")  # manual, hourly, daily, weekly
    last_sync = Column(DateTime(timezone=True), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    connection_status = Column(String, default="pending")  # connected, error, pending
    error_count = Column(Integer, default=0)
    last_error = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    tenant = relationship("Tenant", back_populates="integrations")
    sync_logs = relationship("IntegrationSyncLog", back_populates="integration")

class IntegrationSyncLog(Base):
    """
    Logs of integration synchronizations
    """
    __tablename__ = "integration_sync_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    integration_id = Column(Integer, ForeignKey("enterprise_integrations.id"), nullable=False)
    
    # Sync details
    sync_type = Column(String, nullable=False)  # manual, scheduled, webhook
    direction = Column(String, nullable=False)  # push, pull, bidirectional
    records_processed = Column(Integer, default=0)
    records_success = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    
    # Status and timing
    status = Column(String, nullable=False)  # success, partial, failed
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    processing_time = Column(Float, nullable=True)
    
    # Error handling
    error_details = Column(JSON, nullable=True)
    warnings = Column(JSON, nullable=True)
    
    # Metadata
    sync_metadata = Column(JSON, default={})
    
    # Relationships
    integration = relationship("EnterpriseIntegration", back_populates="sync_logs")

class SecurityThreat(Base):
    """
    Security threats and incidents
    """
    __tablename__ = "security_threats"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Threat details
    threat_type = Column(String, nullable=False)
    threat_severity = Column(Enum(SecurityLevel), nullable=False)
    source_ip = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Description and metadata
    description = Column(Text, nullable=False)
    threat_metadata = Column(JSON, default={})
    
    # Status
    is_resolved = Column(Boolean, default=False)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    
    # Timestamps
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)

class AuditLog(Base):
    """
    Audit logs for compliance and security
    """
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Action details
    action = Column(String, nullable=False)
    resource_type = Column(String, nullable=False)
    resource_id = Column(String, nullable=True)
    
    # Request details
    ip_address = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    request_method = Column(String, nullable=True)
    request_path = Column(String, nullable=True)
    
    # Result
    success = Column(Boolean, nullable=False)
    status_code = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Additional data
    request_data = Column(JSON, nullable=True)
    response_data = Column(JSON, nullable=True)
    audit_metadata = Column(JSON, default={})
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class TenantUsage(Base):
    """
    Tenant usage metrics and billing data
    """
    __tablename__ = "tenant_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    
    # Usage period
    usage_month = Column(Integer, nullable=False)  # 1-12
    usage_year = Column(Integer, nullable=False)
    
    # Document processing metrics
    documents_processed = Column(Integer, default=0)
    total_processing_time = Column(Float, default=0.0)
    storage_used_gb = Column(Float, default=0.0)
    
    # API usage
    api_calls_made = Column(Integer, default=0)
    integration_syncs = Column(Integer, default=0)
    
    # Feature usage
    ai_analyses_performed = Column(Integer, default=0)
    predictions_made = Column(Integer, default=0)
    workflows_executed = Column(Integer, default=0)
    
    # Billing
    billable_amount = Column(Float, default=0.0)
    currency = Column(String, default="USD")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())