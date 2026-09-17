from typing import List, Dict, Any, Tuple, Optional
from app.ai.chunker import layout_chunker, DocumentChunk
from app.ai.retriever import HybridRetriever
from app.ai.reranker import reranker
from app.ai.grounding import grounding_guard
from app.schemas.all_schemas import Citation, ChatMessageResponse

class DocumentRAGService:
    """
    High-Level Hybrid RAG Coordinator for SecurePDF AI.
    Integrates Layout Chunker, Dense/Sparse Hybrid Retrieval, Cross-Encoder Reranking,
    and Grounded Synthesis.
    """

    def __init__(self):
        # Cache active retrievers by document_id in memory for ephemeral speed
        self._retrievers: Dict[str, HybridRetriever] = {}

    async def index_document(self, document_id: str, pdf_buffer: bytes) -> int:
        """
        Parses document into layout chunks and computes hybrid dense embeddings.
        Returns total number of indexed chunks.
        """
        chunks = layout_chunker.chunk_pdf(pdf_buffer)
        if not chunks:
            # Fallback if document is minimal
            chunks = [DocumentChunk(0, 1, "Empty document content", [0, 0, 100, 100])]

        retriever = HybridRetriever(chunks)
        await retriever.initialize_embeddings()
        self._retrievers[document_id] = retriever
        return len(chunks)

    async def query_document(
        self,
        document_id: str,
        query: str,
        pdf_buffer: Optional[bytes] = None,
        top_k: int = 5,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> Tuple[str, List[Citation], float]:
        """
        Executes hybrid retrieval, reranking, and citation-grounded response generation.
        """
        # Ensure retriever exists
        if document_id not in self._retrievers:
            if pdf_buffer:
                await self.index_document(document_id, pdf_buffer)
            else:
                return "Document index expired or not found in memory.", [], 0.0

        retriever = self._retrievers[document_id]

        # 1. Hybrid Retrieval (Dense + BM25 + RRF)
        candidates = await retriever.retrieve(query, top_k=top_k * 2)

        # 2. Cross-Encoder Reranking
        reranked = reranker.rerank(query, candidates)[:top_k]

        # 3. Grounded Answer Synthesis with Strict Citations
        answer, citations, confidence = await grounding_guard.generate_grounded_answer(
            query,
            reranked,
            chat_history=chat_history
        )

        return answer, citations, confidence

    async def search_document(
        self,
        document_id: str,
        query: str,
        pdf_buffer: Optional[bytes] = None,
        top_k: int = 10,
        search_mode: str = "hybrid"
    ) -> List[Dict[str, Any]]:
        """
        Search document in exact, semantic, or hybrid mode.
        """
        if document_id not in self._retrievers and pdf_buffer:
            await self.index_document(document_id, pdf_buffer)

        if document_id not in self._retrievers:
            return []

        retriever = self._retrievers[document_id]
        results = await retriever.retrieve(query, top_k=top_k)
        
        output = []
        for chunk, score, match_type in results:
            output.append({
                "page": chunk.page_number,
                "chunk_index": chunk.chunk_index,
                "content": chunk.content,
                "score": round(score, 4),
                "bbox": chunk.bbox,
                "match_type": match_type
            })
        return output

rag_service = DocumentRAGService()
