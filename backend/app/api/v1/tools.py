import io
import fitz
from typing import Dict, Any, List, Tuple
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.db.models import Document, Job, AuditLog
from app.core.security import get_current_user_token
from app.core.zero_trust import ZeroTrustCrypto
from app.services.storage import storage_service
from app.services.pdf_modifier import pdf_modifier
from app.api.v1.documents import SESSION_DOC_KEYS
from app.schemas.all_schemas import (
    MergeRequest, SplitRequest, RotateRequest, CropRequest,
    WatermarkRequest, CompressRequest, BatesNumberRequest,
    PageNumberRequest, MetadataEditRequest, DocumentResponse
)

router = APIRouter()

async def get_decrypted_pdf_buffer(doc_id: str, user_id: str, db: AsyncSession) -> Tuple[Document, bytes]:
    stmt = select(Document).where(Document.id == doc_id, Document.user_id == user_id, Document.is_deleted == False)
    res = await db.execute(stmt)
    doc_record = res.scalars().first()
    if not doc_record:
        raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")

    aes_key = SESSION_DOC_KEYS.get(doc_id)
    if not aes_key:
        raise HTTPException(status_code=410, detail=f"Ephemeral encryption key for {doc_id} expired. Re-upload.")

    pdf_bytes = storage_service.retrieve_document(doc_record.encrypted_storage_path, aes_key, doc_id)
    return doc_record, pdf_bytes

async def save_modified_pdf(user_id: str, filename: str, pdf_bytes: bytes, db: AsyncSession) -> DocumentResponse:
    doc_id = "doc_" + ZeroTrustCrypto.compute_sha256(pdf_bytes)[:12]
    enc_path, aes_key, sha256_hash = storage_service.store_document(doc_id, pdf_bytes)
    SESSION_DOC_KEYS[doc_id] = aes_key

    doc_obj = fitz.open(stream=pdf_bytes, filetype="pdf")
    page_count = len(doc_obj)
    doc_obj.close()

    new_doc = Document(
        id=doc_id,
        user_id=user_id,
        original_filename=filename,
        encrypted_storage_path=enc_path,
        sha256_hash=sha256_hash,
        file_size=len(pdf_bytes),
        mime_type="application/pdf",
        page_count=page_count,
        encryption_key_hash=ZeroTrustCrypto.compute_sha256(aes_key),
        is_sanitized=False
    )
    db.add(new_doc)
    await db.commit()
    await db.refresh(new_doc)
    return DocumentResponse.model_validate(new_doc)


@router.post("/merge", response_model=DocumentResponse)
async def merge_pdfs(
    payload: MergeRequest,
    token_data: Dict[str, Any] = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db)
):
    user_id = token_data["sub"]
    buffers = []
    for d_id in payload.document_ids:
        _, buf = await get_decrypted_pdf_buffer(d_id, user_id, db)
        buffers.append(buf)

    merged_bytes = pdf_modifier.merge_pdfs(buffers)
    return await save_modified_pdf(user_id, payload.output_filename or "merged.pdf", merged_bytes, db)


@router.post("/split", response_model=List[DocumentResponse])
async def split_pdf(
    payload: SplitRequest,
    token_data: Dict[str, Any] = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db)
):
    user_id = token_data["sub"]
    orig_doc, buf = await get_decrypted_pdf_buffer(payload.document_id, user_id, db)
    split_buffers = pdf_modifier.split_pdf(buf, payload.split_ranges)

    results = []
    for idx, s_buf in enumerate(split_buffers):
        name = f"{orig_doc.original_filename.replace('.pdf', '')}_part_{idx + 1}.pdf"
        res = await save_modified_pdf(user_id, name, s_buf, db)
        results.append(res)

    return results


@router.post("/rotate", response_model=DocumentResponse)
async def rotate_pdf(
    payload: RotateRequest,
    token_data: Dict[str, Any] = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db)
):
    user_id = token_data["sub"]
    orig_doc, buf = await get_decrypted_pdf_buffer(payload.document_id, user_id, db)
    rotated_bytes = pdf_modifier.rotate_pdf(buf, payload.angle, payload.page_numbers)
    return await save_modified_pdf(user_id, f"rotated_{orig_doc.original_filename}", rotated_bytes, db)


@router.post("/crop", response_model=DocumentResponse)
async def crop_pdf(
    payload: CropRequest,
    token_data: Dict[str, Any] = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db)
):
    user_id = token_data["sub"]
    orig_doc, buf = await get_decrypted_pdf_buffer(payload.document_id, user_id, db)
    cropped_bytes = pdf_modifier.crop_pdf(buf, payload.page_number, payload.crop_box)
    return await save_modified_pdf(user_id, f"cropped_{orig_doc.original_filename}", cropped_bytes, db)


@router.post("/watermark", response_model=DocumentResponse)
async def watermark_pdf(
    payload: WatermarkRequest,
    token_data: Dict[str, Any] = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db)
):
    user_id = token_data["sub"]
    orig_doc, buf = await get_decrypted_pdf_buffer(payload.document_id, user_id, db)
    watermarked_bytes = pdf_modifier.add_watermark(
        buf,
        text=payload.watermark_text or "CONFIDENTIAL",
        opacity=payload.opacity,
        rotation=payload.rotation,
        font_size=payload.font_size
    )
    return await save_modified_pdf(user_id, f"watermarked_{orig_doc.original_filename}", watermarked_bytes, db)


@router.post("/compress", response_model=DocumentResponse)
async def compress_pdf(
    payload: CompressRequest,
    token_data: Dict[str, Any] = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db)
):
    user_id = token_data["sub"]
    orig_doc, buf = await get_decrypted_pdf_buffer(payload.document_id, user_id, db)
    compressed_bytes = pdf_modifier.compress_pdf(buf, quality=payload.quality_level)
    return await save_modified_pdf(user_id, f"compressed_{orig_doc.original_filename}", compressed_bytes, db)


@router.post("/bates-number", response_model=DocumentResponse)
async def bates_number_pdf(
    payload: BatesNumberRequest,
    token_data: Dict[str, Any] = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db)
):
    user_id = token_data["sub"]
    orig_doc, buf = await get_decrypted_pdf_buffer(payload.document_id, user_id, db)
    bates_bytes = pdf_modifier.bates_number_pdf(
        buf,
        prefix=payload.prefix,
        start_number=payload.start_number,
        digits=payload.digits,
        position=payload.position,
        font_size=payload.font_size
    )
    return await save_modified_pdf(user_id, f"bates_{orig_doc.original_filename}", bates_bytes, db)


@router.post("/page-numbers", response_model=DocumentResponse)
async def page_numbers_pdf(
    payload: PageNumberRequest,
    token_data: Dict[str, Any] = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db)
):
    user_id = token_data["sub"]
    orig_doc, buf = await get_decrypted_pdf_buffer(payload.document_id, user_id, db)
    numbered_bytes = pdf_modifier.add_page_numbers(
        buf,
        format_style=payload.format_style,
        position=payload.position,
        start_page=payload.start_page
    )
    return await save_modified_pdf(user_id, f"numbered_{orig_doc.original_filename}", numbered_bytes, db)


@router.post("/grayscale", response_model=DocumentResponse)
async def grayscale_pdf(
    document_id: str,
    token_data: Dict[str, Any] = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db)
):
    user_id = token_data["sub"]
    orig_doc, buf = await get_decrypted_pdf_buffer(document_id, user_id, db)
    gray_bytes = pdf_modifier.convert_to_grayscale(buf)
    return await save_modified_pdf(user_id, f"grayscale_{orig_doc.original_filename}", gray_bytes, db)


@router.post("/flatten", response_model=DocumentResponse)
async def flatten_pdf(
    document_id: str,
    token_data: Dict[str, Any] = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db)
):
    user_id = token_data["sub"]
    orig_doc, buf = await get_decrypted_pdf_buffer(document_id, user_id, db)
    flat_bytes = pdf_modifier.flatten_pdf(buf)
    return await save_modified_pdf(user_id, f"flattened_{orig_doc.original_filename}", flat_bytes, db)


@router.post("/metadata", response_model=DocumentResponse)
async def update_metadata(
    payload: MetadataEditRequest,
    token_data: Dict[str, Any] = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db)
):
    user_id = token_data["sub"]
    orig_doc, buf = await get_decrypted_pdf_buffer(payload.document_id, user_id, db)
    meta = {
        "title": payload.title,
        "author": payload.author,
        "subject": payload.subject,
        "keywords": payload.keywords,
        "creator": payload.creator
    }
    updated_bytes = pdf_modifier.update_metadata(buf, meta)
    return await save_modified_pdf(user_id, f"meta_{orig_doc.original_filename}", updated_bytes, db)


@router.get("/structure/{document_id}")
async def inspect_structure(
    document_id: str,
    token_data: Dict[str, Any] = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db)
):
    user_id = token_data["sub"]
    _, buf = await get_decrypted_pdf_buffer(document_id, user_id, db)
    return pdf_modifier.analyze_structure(buf)


@router.post("/compare")
async def compare_documents(
    doc_id_1: str,
    doc_id_2: str,
    token_data: Dict[str, Any] = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db)
):
    user_id = token_data["sub"]
    _, buf1 = await get_decrypted_pdf_buffer(doc_id_1, user_id, db)
    _, buf2 = await get_decrypted_pdf_buffer(doc_id_2, user_id, db)
    return pdf_modifier.compare_pdfs(buf1, buf2)
