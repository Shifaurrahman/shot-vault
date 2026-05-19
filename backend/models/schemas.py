from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# ─── Upload ────────────────────────────────────────────────────────────────────

class UploadRequest(BaseModel):
    title: str
    description: str
    shot_type: Optional[str] = None
    notes: Optional[str] = None
    tags: list[str] = []


class UploadResponse(BaseModel):
    id: str
    title: str
    message: str
    file_url: Optional[str] = None


# ─── Query ─────────────────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5
    filter_type: Optional[str] = None   # "image" | "video" | None = both


class ShotResult(BaseModel):
    id: str
    title: str
    description: str
    shot_type: Optional[str] = None
    notes: Optional[str] = None
    tags: list[str] = []
    media_type: Optional[str] = None    # "image" | "video"
    file_url: Optional[str] = None
    score: float
    created_at: Optional[str] = None


class QueryResponse(BaseModel):
    query: str
    answer: str                          # ← Claude's natural language answer
    results: list[ShotResult]
    total: int


# ─── Health ────────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    app: str
    version: str
    embedding_model: str
    vector_db: str
    storage_backend: str
    llm_model: str
    llm_enabled: bool