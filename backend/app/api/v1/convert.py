from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import get_current_user_token
from app.services.converter import converter_service
from app.api.v1.tools import get_decrypted_pdf_buffer, save_modified_pdf
from app.schemas.all_schemas import ConvertRequest, DocumentResponse

router = APIRouter()

@router.post("/to-format")
async def convert_document(
    payload: ConvertRequest,
    token_data: Dict[str, Any] = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db)
):
    user_id = token_data["sub"]
    doc_record, buf = await get_decrypted_pdf_buffer(payload.document_id, user_id, db)
    fmt = payload.target_format.lower()

    if fmt == "docx":
        docx_bytes = converter_service.pdf_to_docx(buf)
        return Response(
            content=docx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f'attachment; filename="{doc_record.original_filename}.docx"'}
        )
    elif fmt in ["xlsx", "excel"]:
        xlsx_bytes = converter_service.pdf_to_excel(buf)
        return Response(
            content=xlsx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f'attachment; filename="{doc_record.original_filename}.xlsx"'}
        )
    elif fmt in ["pptx", "ppt"]:
        pptx_bytes = converter_service.pdf_to_pptx(buf)
        return Response(
            content=pptx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            headers={"Content-Disposition": f'attachment; filename="{doc_record.original_filename}.pptx"'}
        )
    elif fmt == "md" or fmt == "markdown":
        md_text = converter_service.pdf_to_markdown(buf)
        return {"format": "markdown", "content": md_text}
    elif fmt == "html":
        html_text = converter_service.pdf_to_html(buf)
        return {"format": "html", "content": html_text}
    elif fmt in ["png", "jpg", "webp"]:
        imgs = converter_service.pdf_to_images(buf, format=fmt, dpi=payload.dpi or 200)
        return Response(
            content=imgs[0] if imgs else b"",
            media_type=f"image/{fmt.lower()}",
            headers={"Content-Disposition": f'attachment; filename="page_1.{fmt.lower()}"'}
        )
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported conversion format: {fmt}")

@router.post("/from-images", response_model=DocumentResponse)
async def images_to_pdf(
    files: List[UploadFile] = File(...),
    token_data: Dict[str, Any] = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db)
):
    user_id = token_data["sub"]
    image_buffers = []
    for f in files:
        b = await f.read()
        image_buffers.append(b)

    pdf_bytes = converter_service.images_to_pdf(image_buffers)
    return await save_modified_pdf(user_id, "images_converted.pdf", pdf_bytes, db)

@router.get("/extract-assets/{document_id}")
async def extract_assets(
    document_id: str,
    token_data: Dict[str, Any] = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db)
):
    user_id = token_data["sub"]
    _, buf = await get_decrypted_pdf_buffer(document_id, user_id, db)
    return converter_service.extract_assets(buf)
