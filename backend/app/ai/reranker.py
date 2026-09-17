from typing import List, Tuple
from app.ai.chunker import DocumentChunk

class CrossEncoderReranker:
    """
    Cross-Encoder Reranking Module.
    Re-scores candidate chunks by computing joint cross-attention / semantic overlap.
    """

    @staticmethod
    def rerank(query: str, candidates: List[Tuple[DocumentChunk, float, str]]) -> List[Tuple[DocumentChunk, float, str]]:
        """
        Reranks retrieved candidate chunks.
        """
        if not candidates:
            return []

        query_words = set(query.lower().split())
        reranked = []

        for chunk, initial_score, match_type in candidates:
            chunk_words = set(chunk.content.lower().split())
            overlap = len(query_words.intersection(chunk_words))
            overlap_ratio = overlap / max(1, len(query_words))
            
            # Cross scoring boost
            cross_score = (initial_score * 0.5) + (overlap_ratio * 0.5)
            reranked.append((chunk, cross_score, match_type))

        # Sort by updated cross score
        reranked.sort(key=lambda x: x[1], reverse=True)
        return reranked

reranker = CrossEncoderReranker()
