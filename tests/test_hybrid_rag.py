import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

import pytest
from app.ai.chunker import layout_chunker
from app.ai.retriever import HybridRetriever
from app.ai.rag_service import rag_service
from app.ai.grounding import grounding_guard

@pytest.mark.asyncio
async def test_layout_chunker(sample_pdf_bytes):
    chunks = layout_chunker.chunk_pdf(sample_pdf_bytes)
    assert len(chunks) >= 2
    assert chunks[0].page_number == 1
    assert len(chunks[0].bbox) == 4

@pytest.mark.asyncio
async def test_hybrid_retrieval(sample_pdf_bytes):
    chunks = layout_chunker.chunk_pdf(sample_pdf_bytes)
    retriever = HybridRetriever(chunks)
    await retriever.initialize_embeddings()

    results = await retriever.retrieve("cryptography AES-256", top_k=2)
    assert len(results) > 0
    top_chunk, score, match_type = results[0]
    assert "AES-256" in top_chunk.content or "cryptography" in top_chunk.content.lower()

@pytest.mark.asyncio
async def test_anti_hallucination_guard_fallback():
    # When query is completely absent from context
    ans, citations, conf = await grounding_guard.generate_grounded_answer(
        "What is the secret recipe for quantum cold fusion?",
        []
    )
    assert ans == grounding_guard.FALLBACK_MESSAGE
    assert len(citations) == 0
    assert conf == 0.0
