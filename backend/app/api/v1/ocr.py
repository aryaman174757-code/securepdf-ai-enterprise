from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import get_current_user_token
from app.services.ocr_engine import ocr_service
from app.api.v1.tools import get_decrypted_pdf_buffer, save_modified_pdf
from app.schemas.all_schemas import OCRRequest, OCRResponse

router = APIRouter()

@router.post("/process", response_model=OCRResponse)
async def process_ocr(
    payload: OCRRequest,
    token_data: Dict[str, Any] = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db)
):
    user_id = token_data["sub"]
    doc_record, buf = await get_decrypted_pdf_buffer(payload.document_id, user_id, db)

    ocr_res, searchable_pdf_bytes = ocr_service.run_ocr_on_pdf(
        buf,
        engine=payload.engine,
        language=payload.language,
        apply_deskew=payload.apply_deskew,
        apply_denoise=payload.apply_denoise,
        apply_adaptive_thresh=payload.apply_adaptive_threshold,
        generate_searchable_pdf=payload.generate_searchable_pdf
    )

    ocr_res.document_id = payload.document_id
    ocr_res.job_id = "ocr_job_" + doc_record.id[:8]

    # If searchable PDF generated, persist as new document
    if searchable_pdf_bytes:
        new_doc = await save_modified_pdf(
            user_id,
            f"ocr_searchable_{doc_record.original_filename}",
            searchable_pdf_bytes,
            db
        )
        ocr_res.searchable_pdf_id = new_doc.id

    return ocr_res
