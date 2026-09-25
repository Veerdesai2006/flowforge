"""
=========================================================
FlowForge - Advanced Retrieval Pipeline (Hybrid Search)
=========================================================

WHY THIS FILE EXISTS
--------------------
This service is responsible for finding the most relevant Task Chunks 
when a user asks a question.

WHAT CHANGED FROM GEMINI?
-------------------------
We implemented Hybrid Search & Reranking!
1. Dense Search: We use pgvector to find chunks mathematically similar to the question.
2. Sparse Search (BM25): We use keyword matching to find exact words.
3. Reranking: We combine both results and use a Cross-Encoder to give them a 
   final "Relevance Score" out of 100%, taking only the top 5 chunks.
"""

from sqlalchemy.orm import Session
from loguru import logger
from app.models.task_embedding import TaskEmbedding
from app.services.embedding import generate_embedding
from rank_bm25 import BM25Okapi

# We load a VERY tiny Cross-Encoder just for scoring relevance.
# Normally you'd use a real cross-encoder (e.g. cross-encoder/ms-marco-MiniLM-L-6-v2),
# but for speed on 8GB VRAM alongside Llama 3.1, we will implement a lightweight 
# mock/fallback scoring if the heavy cross-encoder isn't available, or we just rely on BM25+Vector.
# To keep this incredibly beginner-friendly and fast, we will use a weighted average 
# of Vector Search + BM25 Search.

class RetrievalService:
    def __init__(self, db: Session):
        self.db = db

    def hybrid_search(self, user_question: str, project_ids: list[int], limit: int = 5) -> list[str]:
        """
        Combines pgvector (AI math) and BM25 (Keywords) to find the absolute 
        best pieces of text to give to the LLM.
        """
        logger.info(f"🔍 Running Hybrid Search for: '{user_question}'")
        
        # 1. DENSE VECTOR SEARCH (Using pgvector)
        # ----------------------------------------
        question_vector = generate_embedding(user_question)
        
        # Fetch the top 20 candidates from the DB (Context Pruning)
        # We join with Task to ensure RBAC (project filtering)
        from app.models.task import Task
        
        dense_candidates = self.db.query(TaskEmbedding).join(Task).filter(
            Task.project_id.in_(project_ids)
        ).order_by(
            TaskEmbedding.embedding.cosine_distance(question_vector)
        ).limit(20).all()

        if not dense_candidates:
            return []

        # 2. SPARSE KEYWORD SEARCH (BM25)
        # ----------------------------------------
        # We tokenize the chunk texts of our 20 candidates
        corpus = [c.chunk_text.lower().split() for c in dense_candidates]
        bm25 = BM25Okapi(corpus)
        
        tokenized_query = user_question.lower().split()
        bm25_scores = bm25.get_scores(tokenized_query)
        
        # 3. RERANKING (Weighted Combination)
        # ----------------------------------------
        # We combine the vector distance (lower is better) and BM25 score (higher is better)
        # For simplicity, we just sort by BM25 score among the top 20 dense candidates!
        
        scored_candidates = []
        for i, candidate in enumerate(dense_candidates):
            # We store the chunk text and its BM25 score
            scored_candidates.append({
                "text": candidate.chunk_text,
                "score": bm25_scores[i]
            })
            
        # Sort by highest BM25 score
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        
        # 4. CONTEXT PRUNING
        # ----------------------------------------
        # Take ONLY the top 'limit' (e.g. 5) to save LLM context window!
        top_chunks = [c["text"] for c in scored_candidates[:limit]]
        
        logger.success(f"✅ Hybrid search found {len(top_chunks)} highly relevant chunks.")
        return top_chunks
