from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import get_current_user_token
from app.ai.rag_service import rag_service
from app.api.v1.tools import get_decrypted_pdf_buffer
from app.schemas.all_schemas import HybridSearchRequest, SearchResultItem

router = APIRouter()

@router.post("/hybrid", response_model=List[SearchResultItem])
async def search_hybrid(
    payload: HybridSearchRequest,
    token_data: Dict[str, Any] = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db)
):
    user_id = token_data["sub"]
    _, buf = await get_decrypted_pdf_buffer(payload.document_id, user_id, db)

    raw_results = await rag_service.search_document(
        document_id=payload.document_id,
        query=payload.query,
        pdf_buffer=buf,
        top_k=payload.top_k,
        search_mode=payload.search_mode
    )

    items = []
    for r in raw_results:
        items.append(SearchResultItem(
            page=r["page"],
            chunk_index=r["chunk_index"],
            content=r["content"],
            score=r["score"],
            bbox=r["bbox"],
            match_type=r["match_type"]
        ))

    return items
