from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import get_current_user_token
from app.services.redactor import redactor_service
from app.services.security_service import security_service
from app.api.v1.tools import get_decrypted_pdf_buffer, save_modified_pdf
from app.schemas.all_schemas import (
    DeepRedactionRequest, EncryptPDFRequest, DecryptPDFRequest,
    SecurityReportResponse, DocumentResponse
)

router = APIRouter()

@router.post("/deep-redact", response_model=DocumentResponse)
async def deep_redact(
    payload: DeepRedactionRequest,
    token_data: Dict[str, Any] = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db)
):
    user_id = token_data["sub"]
    orig_doc, buf = await get_decrypted_pdf_buffer(payload.document_id, user_id, db)

    redacted_bytes = redactor_service.apply_deep_redaction(
        buf,
        redactions=payload.redactions,
        burn_raster_pixels=payload.burn_raster_pixels,
        scrub_metadata=payload.scrub_metadata,
        clean_fonts=payload.clean_fonts
    )

    return await save_modified_pdf(
        user_id,
        f"redacted_{orig_doc.original_filename}",
        redacted_bytes,
        db
    )

@router.get("/scan-pii/{document_id}")
async def scan_pii(
    document_id: str,
    token_data: Dict[str, Any] = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db)
):
    user_id = token_data["sub"]
    _, buf = await get_decrypted_pdf_buffer(document_id, user_id, db)
    return redactor_service.scan_for_sensitive_entities(buf)

@router.post("/encrypt", response_model=DocumentResponse)
async def encrypt_document(
    payload: EncryptPDFRequest,
    token_data: Dict[str, Any] = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db)
):
    user_id = token_data["sub"]
    orig_doc, buf = await get_decrypted_pdf_buffer(payload.document_id, user_id, db)

    enc_bytes = security_service.encrypt_pdf(
        buf,
        user_password=payload.user_password,
        owner_password=payload.owner_password,
        allow_printing=payload.allow_printing,
        allow_copying=payload.allow_copying
    )

    return await save_modified_pdf(
        user_id,
        f"aes256_locked_{orig_doc.original_filename}",
        enc_bytes,
        db
    )

@router.post("/decrypt", response_model=DocumentResponse)
async def decrypt_document(
    payload: DecryptPDFRequest,
    token_data: Dict[str, Any] = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db)
):
    user_id = token_data["sub"]
    orig_doc, buf = await get_decrypted_pdf_buffer(payload.document_id, user_id, db)

    dec_bytes = security_service.decrypt_pdf(buf, payload.password)
    return await save_modified_pdf(
        user_id,
        f"unlocked_{orig_doc.original_filename}",
        dec_bytes,
        db
    )

@router.post("/sanitize-metadata", response_model=DocumentResponse)
async def sanitize_metadata(
    document_id: str,
    token_data: Dict[str, Any] = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db)
):
    user_id = token_data["sub"]
    orig_doc, buf = await get_decrypted_pdf_buffer(document_id, user_id, db)

    clean_bytes = security_service.sanitize_metadata(buf)
    return await save_modified_pdf(
        user_id,
        f"sanitized_{orig_doc.original_filename}",
        clean_bytes,
        db
    )

@router.get("/audit-report/{document_id}", response_model=SecurityReportResponse)
async def get_security_audit_report(
    document_id: str,
    token_data: Dict[str, Any] = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db)
):
    user_id = token_data["sub"]
    _, buf = await get_decrypted_pdf_buffer(document_id, user_id, db)

    report_data, _ = security_service.generate_security_audit_report(buf, document_id)
    return report_data
