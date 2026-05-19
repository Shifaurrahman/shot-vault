"""
Query Route  —  POST /api/query
─────────────────────────────────
Flow:
  1. Receive natural language query from React UI
  2. Embed the query text (same Qwen model, same vector space)
  3. Similarity search in ChromaDB → top-K matched shots
  4. Claude reads the matched shots → generates natural language answer
  5. Return answer + matched shot cards (with file URLs) to React UI

React UI shows:
  ┌─────────────────────────────────────┐
  │ 🤖 Claude's answer                  │
  │ "An extreme wide shot shows the     │
  │  subject in a vast environment…"    │
  └─────────────────────────────────────┘
  [Card: beach shot]  [Card: rooftop]  ...
"""

from fastapi import APIRouter, HTTPException
from models.schemas import QueryRequest, QueryResponse
from services.embedding import embedding_service
from services.vector_store import vector_store
from services.llm import llm_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query_shots(request: QueryRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    # ── 1. Embed the query ────────────────────────────────────────────────────
    try:
        query_embedding = embedding_service.embed_text(request.query)
    except Exception as e:
        logger.error(f"Query embedding failed: {e}")
        raise HTTPException(status_code=500, detail=f"Embedding failed: {str(e)}")

    # ── 2. Similarity search ──────────────────────────────────────────────────
    try:
        results = vector_store.query(
            embedding=query_embedding,
            top_k=request.top_k,
            filter_type=request.filter_type,
        )
    except Exception as e:
        logger.error(f"Vector search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

    # ── 3. Claude generates answer from retrieved shots ───────────────────────
    answer = llm_service.generate_answer(
        query=request.query,
        results=results,
    )

    logger.info(f"Query: '{request.query}' → {len(results)} results | answer: {'yes' if answer else 'no'}")

    return QueryResponse(
        query=request.query,
        answer=answer,
        results=results,
        total=len(results),
    )


@router.get("/query/suggestions")
async def get_suggestions():
    return {
        "suggestions": [
            "extreme wide shot",
            "golden hour lighting",
            "handheld night scene",
            "aerial drone shot",
            "close-up emotion",
            "action chase sequence",
        ]
    }