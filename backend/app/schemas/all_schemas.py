from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field

# --- AUTH SCHEMAS ---
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    email: str
    role: str
    is_pro: bool

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: Optional[str] = None
    role: str
    is_active: bool
    is_verified: bool
    is_pro: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ApiKeyCreate(BaseModel):
    name: str = Field(..., max_length=128)

class ApiKeyResponse(BaseModel):
    id: str
    name: str
    key_prefix: str
    raw_api_key: Optional[str] = None  # Only returned on creation
    is_active: bool
    created_at: datetime


# --- DOCUMENT SCHEMAS ---
class DocumentResponse(BaseModel):
    id: str
    original_filename: str
    sha256_hash: str
    file_size: int
    mime_type: str
    page_count: int
    is_sanitized: bool
    created_at: datetime

    class Config:
        from_attributes = True

class DocumentDetailResponse(DocumentResponse):
    threat_level: Optional[str] = "CLEAN"
    security_score: int = 100
    is_encrypted: bool = False
    has_signatures: bool = False


# --- PDF MODIFICATION SCHEMAS ---
class MergeRequest(BaseModel):
    document_ids: List[str] = Field(..., min_items=2)
    output_filename: Optional[str] = "merged_document.pdf"

class SplitRequest(BaseModel):
    document_id: str
    split_ranges: List[str] = Field(..., description="e.g. ['1-3', '4-5', '6']")

class RotateRequest(BaseModel):
    document_id: str
    angle: int = Field(..., description="90, 180, or 270")
    page_numbers: Optional[List[int]] = None  # None = all pages

class CropRequest(BaseModel):
    document_id: str
    page_number: int
    crop_box: List[float] = Field(..., description="[x0, y0, x1, y1]")

class WatermarkRequest(BaseModel):
    document_id: str
    watermark_text: Optional[str] = "CONFIDENTIAL"
    watermark_image_id: Optional[str] = None
    opacity: float = Field(0.3, ge=0.0, le=1.0)
    rotation: int = 45
    font_size: int = 40
    color_rgb: List[int] = [128, 128, 128]

class CompressRequest(BaseModel):
    document_id: str
    quality_level: str = Field("medium", description="low, medium, high, extreme")
    dpi: int = 150

class BatesNumberRequest(BaseModel):
    document_id: str
    prefix: str = "SPDF-"
    start_number: int = 1000
    digits: int = 6
    position: str = "bottom-right"  # top-left, top-right, bottom-left, bottom-right, bottom-center
    font_size: int = 10

class PageNumberRequest(BaseModel):
    document_id: str
    format_style: str = "Page {n} of {total}"
    position: str = "bottom-center"
    start_page: int = 1

class MetadataEditRequest(BaseModel):
    document_id: str
    title: Optional[str] = None
    author: Optional[str] = None
    subject: Optional[str] = None
    keywords: Optional[str] = None
    creator: Optional[str] = None


# --- CONVERSION SCHEMAS ---
class ConvertRequest(BaseModel):
    document_id: str
    target_format: str = Field(..., description="docx, xlsx, pptx, html, epub, md, png, jpg, webp, pdf")
    dpi: Optional[int] = 200
    extract_type: Optional[str] = None  # images, tables, text


# --- OCR SCHEMAS ---
class OCRRequest(BaseModel):
    document_id: str
    engine: str = Field("tesseract", description="tesseract or paddleocr")
    language: str = "eng"
    apply_deskew: bool = True
    apply_denoise: bool = True
    apply_adaptive_threshold: bool = True
    generate_searchable_pdf: bool = True

class OCRBoundingBox(BaseModel):
    page: int
    text: str
    confidence: float
    bbox: List[float]  # [x0, y0, x1, y1]

class OCRResponse(BaseModel):
    job_id: str
    document_id: str
    page_count: int
    full_text: str
    bounding_boxes: List[OCRBoundingBox]
    confidence_avg: float
    searchable_pdf_id: Optional[str] = None


# --- AI CHAT & RAG SCHEMAS ---
class ChatCreateRequest(BaseModel):
    document_id: str
    title: Optional[str] = "Document Intelligence Chat"

class ChatQueryRequest(BaseModel):
    chat_id: str
    query: str
    use_hybrid_search: bool = True
    top_k: int = 5
    temperature: float = 0.1

class Citation(BaseModel):
    page: int
    text: str
    bbox: List[float]
    confidence: float

class ChatMessageResponse(BaseModel):
    id: str
    chat_id: str
    role: str
    content: str
    citations: List[Citation] = []
    confidence_score: float = 1.0
    created_at: datetime


# --- HYBRID SEARCH SCHEMAS ---
class HybridSearchRequest(BaseModel):
    document_id: str
    query: str
    search_mode: str = "hybrid"  # exact, semantic, hybrid, clause, table
    top_k: int = 10

class SearchResultItem(BaseModel):
    page: int
    chunk_index: int
    content: str
    score: float
    bbox: List[float]
    match_type: str  # dense, sparse, exact


# --- SECURITY & REDACTION SCHEMAS ---
class RedactionItem(BaseModel):
    page: int
    bbox: Optional[List[float]] = None
    text_pattern: Optional[str] = None  # Regex pattern, e.g. SSN, Email, Credit Card
    entity_type: Optional[str] = None  # PII, CREDIT_CARD, EMAIL, PHONE, CUSTOM

class DeepRedactionRequest(BaseModel):
    document_id: str
    redactions: List[RedactionItem]
    burn_raster_pixels: bool = True
    scrub_metadata: bool = True
    clean_fonts: bool = True

class EncryptPDFRequest(BaseModel):
    document_id: str
    user_password: str
    owner_password: Optional[str] = None
    allow_printing: bool = False
    allow_copying: bool = False

class DecryptPDFRequest(BaseModel):
    document_id: str
    password: str

class SecurityReportResponse(BaseModel):
    document_id: str
    overall_security_score: int
    encryption_status: str
    pdf_version: str
    threat_level: str
    detected_threats: List[str]
    metadata_fields_found: Dict[str, str]
    hidden_layers_detected: bool
    javascript_present: bool
    launch_actions_present: bool
    embedded_files_count: int


# --- PIPELINE BUILDER SCHEMAS ---
class PipelineNode(BaseModel):
    id: str
    type: str  # ingest, ocr, split, merge, compress, convert, watermark, redact, encrypt, export
    position: Dict[str, float]  # {"x": 100, "y": 200}
    data: Dict[str, Any]

class PipelineEdge(BaseModel):
    id: str
    source: str
    target: str

class PipelineCreate(BaseModel):
    name: str
    description: Optional[str] = None
    nodes: List[PipelineNode]
    edges: List[PipelineEdge]
    is_template: bool = False

class PipelineExecuteRequest(BaseModel):
    pipeline_id: str
    input_document_id: str

class PipelineStepProgress(BaseModel):
    node_id: str
    node_type: str
    status: str  # PENDING, RUNNING, COMPLETED, FAILED
    progress: float
    output_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# --- ADMIN & TELEMETRY SCHEMAS ---
class AdminTelemetry(BaseModel):
    total_users: int
    active_sessions: int
    total_documents_processed: int
    ai_queries_executed: int
    queue_backlog: int
    worker_health: str
    active_workers_count: int
    memory_usage_mb: float
    uptime_seconds: float
