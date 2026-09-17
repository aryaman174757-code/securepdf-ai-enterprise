from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.db.models import AIChat, ChatMessage, Document
from app.core.security import get_current_user_token
from app.ai.rag_service import rag_service
from app.api.v1.tools import get_decrypted_pdf_buffer
from app.schemas.all_schemas import ChatCreateRequest, ChatQueryRequest, ChatMessageResponse

router = APIRouter()

@router.post("/create")
async def create_ai_chat(
    payload: ChatCreateRequest,
    token_data: Dict[str, Any] = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db)
):
    user_id = token_data["sub"]
    _, buf = await get_decrypted_pdf_buffer(payload.document_id, user_id, db)
    
    # Pre-index document in RAG memory
    total_chunks = await rag_service.index_document(payload.document_id, buf)

    new_chat = AIChat(
        user_id=user_id,
        document_id=payload.document_id,
        title=payload.title or "Document Intelligence Chat"
    )
    db.add(new_chat)
    await db.commit()
    await db.refresh(new_chat)

    return {
        "chat_id": new_chat.id,
        "document_id": new_chat.document_id,
        "title": new_chat.title,
        "indexed_chunks": total_chunks
    }

@router.post("/{chat_id}/query", response_model=ChatMessageResponse)
async def query_chat(
    chat_id: str,
    payload: ChatQueryRequest,
    token_data: Dict[str, Any] = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db)
):
    user_id = token_data["sub"]
    
    # Verify chat ownership
    stmt = select(AIChat).where(AIChat.id == chat_id, AIChat.user_id == user_id)
    res = await db.execute(stmt)
    chat = res.scalars().first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat conversation not found")

    # Fetch document buffer
    _, buf = await get_decrypted_pdf_buffer(chat.document_id, user_id, db)

    # Save User Query
    user_msg = ChatMessage(
        chat_id=chat_id,
        role="user",
        content=payload.query
    )
    db.add(user_msg)

    # Execute Grounded RAG Query
    answer, citations, confidence = await rag_service.query_document(
        document_id=chat.document_id,
        query=payload.query,
        pdf_buffer=buf,
        top_k=payload.top_k
    )

    # Save Assistant Response
    citation_dicts = [c.model_dump() for c in citations]
    assistant_msg = ChatMessage(
        chat_id=chat_id,
        role="assistant",
        content=answer,
        citations=citation_dicts,
        confidence_score=confidence
    )
    db.add(assistant_msg)
    await db.commit()
    await db.refresh(assistant_msg)

    return ChatMessageResponse(
        id=assistant_msg.id,
        chat_id=assistant_msg.chat_id,
        role=assistant_msg.role,
        content=assistant_msg.content,
        citations=citations,
        confidence_score=assistant_msg.confidence_score,
        created_at=assistant_msg.created_at
    )

@router.get("/{chat_id}/messages")
async def get_chat_history(
    chat_id: str,
    token_data: Dict[str, Any] = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db)
):
    user_id = token_data["sub"]
    stmt = select(AIChat).where(AIChat.id == chat_id, AIChat.user_id == user_id)
    res = await db.execute(stmt)
    chat = res.scalars().first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    msg_stmt = select(ChatMessage).where(ChatMessage.chat_id == chat_id).order_by(ChatMessage.created_at.asc())
    msg_res = await db.execute(msg_stmt)
    return msg_res.scalars().all()
