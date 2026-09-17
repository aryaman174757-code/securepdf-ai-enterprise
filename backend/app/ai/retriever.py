import math
import numpy as np
from typing import List, Dict, Any, Tuple
from rank_bm25 import BM25Okapi
from app.ai.embeddings import embedding_service
from app.ai.chunker import DocumentChunk

class HybridRetriever:
    """
    Hybrid Document Retrieval Engine combining:
    1. Dense Vector Similarity (Cosine distance)
    2. Sparse Lexical Search (BM25Okapi)
    3. Reciprocal Rank Fusion (RRF) with constant k=60
    """

    def __init__(self, chunks: List[DocumentChunk]):
        self.chunks = chunks
        self.corpus_tokens = [c.content.lower().split() for c in chunks]
        self.bm25 = BM25Okapi(self.corpus_tokens) if self.corpus_tokens else None
        self.chunk_embeddings: List[List[float]] = []

    async def initialize_embeddings(self):
        """Pre-compute dense embeddings for all document chunks."""
        texts = [c.content for c in self.chunks]
        if texts:
            self.chunk_embeddings = await embedding_service.get_embeddings(texts)

    async def retrieve(self, query: str, top_k: int = 5, k_rrf: int = 60) -> List[Tuple[DocumentChunk, float, str]]:
        """
        Executes Dense + Sparse Retrieval and fuses rankings using RRF.
        Returns list of (DocumentChunk, fusion_score, match_type).
        """
        if not self.chunks:
            return []

        # 1. Sparse BM25 Scoring & Ranking
        query_tokens = query.lower().split()
        bm25_scores = self.bm25.get_scores(query_tokens) if self.bm25 else [0.0] * len(self.chunks)
        sparse_ranked_indices = np.argsort(bm25_scores)[::-1]

        # 2. Dense Vector Scoring & Ranking
        query_vec = (await embedding_service.get_embeddings([query]))[0]
        q_arr = np.array(query_vec)
        
        dense_scores = []
        for c_vec in self.chunk_embeddings:
            c_arr = np.array(c_vec)
            sim = float(np.dot(q_arr, c_arr) / (np.linalg.norm(q_arr) * np.linalg.norm(c_arr) + 1e-9))
            dense_scores.append(sim)
        
        dense_ranked_indices = np.argsort(dense_scores)[::-1]

        # 3. Reciprocal Rank Fusion (RRF)
        rrf_scores: Dict[int, float] = {}

        # Fuse Sparse Ranks
        for rank, idx in enumerate(sparse_ranked_indices[:50]):
            rrf_scores[idx] = rrf_scores.get(idx, 0.0) + (1.0 / (k_rrf + rank + 1))

        # Fuse Dense Ranks
        for rank, idx in enumerate(dense_ranked_indices[:50]):
            rrf_scores[idx] = rrf_scores.get(idx, 0.0) + (1.0 / (k_rrf + rank + 1))

        # Sort combined results by RRF score
        sorted_rrf = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

        results = []
        for idx, score in sorted_rrf[:top_k]:
            match_type = "hybrid"
            if idx in sparse_ranked_indices[:top_k] and idx not in dense_ranked_indices[:top_k]:
                match_type = "sparse_keyword"
            elif idx in dense_ranked_indices[:top_k] and idx not in sparse_ranked_indices[:top_k]:
                match_type = "dense_semantic"

            results.append((self.chunks[idx], float(score), match_type))

        return results
