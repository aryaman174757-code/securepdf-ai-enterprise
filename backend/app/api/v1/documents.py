import io
import fitz
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.db.session import get_db
from app.db.models import Document, AuditLog
from app.core.security import get_current_user_token
from app.core.malware import MalwareScanner
from app.core.zero_trust import ZeroTrustCrypto
from app.services.storage import storage_service
from app.schemas.all_schemas import DocumentResponse, DocumentDetailResponse

router = APIRouter()

# Memory cache for active session encryption keys (ephemeral zero-trust)
SESSION_DOC_KEYS: Dict[str, bytes] = {}

@router.post("/upload", response_model=DocumentDetailResponse)
async def upload_document(
    file: UploadFile = File(...),
    token_data: Dict[str, Any] = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db)
):
    user_id = token_data["sub"]
    contents = await file.read()
    
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    # 1. Deep Malware & Magic Byte Scan
    scan_result = MalwareScanner.scan_pdf_buffer(contents)
    if not scan_result.is_safe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Security scan rejected file: {', '.join(scan_result.threats)}"
        )

    # 2. Extract Document Geometry
    try:
        doc = fitz.open(stream=contents, filetype="pdf")
        page_count = len(doc)
        is_encrypted = doc.is_encrypted
        doc.close()
    except Exception:
        page_count = 1
        is_encrypted = False

    # 3. Encrypt & Store using Ephemeral AES-256 Key
    doc_id = str(fitz.TOOLS.gen_uuid()) if hasattr(fitz.TOOLS, 'gen_uuid') else str(fitz.utils.gen_uuid() if hasattr(fitz.utils, 'gen_uuid') else "doc_" + ZeroTrustCrypto.compute_sha256(contents)[:12])
    enc_path, aes_key, sha256_hash = storage_service.store_document(doc_id, contents)
    
    # Store ephemeral key in memory cache
    SESSION_DOC_KEYS[doc_id] = aes_key

    # 4. Persist Record to DB
    new_doc = Document(
        id=doc_id,
        user_id=user_id,
        original_filename=file.filename or "document.pdf",
        encrypted_storage_path=enc_path,
        sha256_hash=sha256_hash,
        file_size=len(contents),
        mime_type=file.content_type or "application/pdf",
        page_count=page_count,
        encryption_key_hash=ZeroTrustCrypto.compute_sha256(aes_key),
        is_sanitized=False
    )
    db.add(new_doc)
    
    # Audit trail
    audit = AuditLog(
        user_id=user_id,
        action="DOCUMENT_UPLOAD",
        resource_type="document",
        resource_id=doc_id,
        metadata_json={"filename": file.filename, "size": len(contents), "threat_level": scan_result.threat_level}
    )
    db.add(audit)
    await db.commit()
    await db.refresh(new_doc)

    return DocumentDetailResponse(
        id=new_doc.id,
        original_filename=new_doc.original_filename,
        sha256_hash=new_doc.sha256_hash,
        file_size=new_doc.file_size,
        mime_type=new_doc.mime_type,
        page_count=new_doc.page_count,
        is_sanitized=new_doc.is_sanitized,
        created_at=new_doc.created_at,
        threat_level=scan_result.threat_level,
        security_score=100 if scan_result.is_safe else 50,
        is_encrypted=is_encrypted
    )

@router.get("/", response_model=List[DocumentResponse])
async def list_user_documents(
    token_data: Dict[str, Any] = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db)
):
    user_id = token_data["sub"]
    stmt = select(Document).where(Document.user_id == user_id, Document.is_deleted == False).order_by(Document.created_at.desc())
    res = await db.execute(stmt)
    return res.scalars().all()

@router.get("/{document_id}/download")
async def download_document(
    document_id: str,
    token_data: Dict[str, Any] = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db)
):
    user_id = token_data["sub"]
    stmt = select(Document).where(Document.id == document_id, Document.user_id == user_id, Document.is_deleted == False)
    res = await db.execute(stmt)
    doc_record = res.scalars().first()
    if not doc_record:
        raise HTTPException(status_code=404, detail="Document not found")

    aes_key = SESSION_DOC_KEYS.get(document_id)
    if not aes_key:
        raise HTTPException(status_code=410, detail="Ephemeral key expired. Re-upload document.")

    decrypted_bytes = storage_service.retrieve_document(
        doc_record.encrypted_storage_path,
        aes_key,
        document_id
    )

    return Response(
        content=decrypted_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{doc_record.original_filename}"'}
    )
