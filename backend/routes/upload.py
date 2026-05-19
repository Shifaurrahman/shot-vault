"""
Upload Route  —  POST /api/upload
──────────────────────────────────
Flow:
  1. Receive multipart form (title, description, tags, media file)
  2. Save media file to storage (local or S3)
  3. Build combined text for embedding
  4. Generate embedding (multimodal if image, text-only otherwise)
  5. Store vector + metadata in ChromaDB / Qdrant
  6. Return entry ID + file URL to React UI
"""

import uuid
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional

from models.schemas import UploadResponse
from services.embedding import embedding_service
from services.vector_store import vector_store
from services.storage import storage_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Supported media types
IMAGE_TYPES = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
VIDEO_TYPES = {".mp4", ".mov", ".webm", ".avi"}


@router.post("/upload", response_model=UploadResponse)
async def upload_shot(
    title: str = Form(...),
    description: str = Form(...),
    shot_type: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    tags: Optional[str] = Form(""),        # comma-separated from React
    file: Optional[UploadFile] = File(None),
):
    entry_id = str(uuid.uuid4())
    file_url = None
    file_path = None
    media_type = None

    # ── 1. Save media file ────────────────────────────────────────────────────
    if file and file.filename:
        from pathlib import Path
        suffix = Path(file.filename).suffix.lower()

        if suffix in IMAGE_TYPES:
            media_type = "image"
        elif suffix in VIDEO_TYPES:
            media_type = "video"
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {suffix}. Use JPG, PNG, MP4, MOV."
            )

        file_path, file_url = await storage_service.save(file, entry_id)

    # ── 2. Build text for embedding ───────────────────────────────────────────
    # Combine all text fields so the vector captures everything
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []

    embed_text = f"{title}. "
    if shot_type:
        embed_text += f"Shot type: {shot_type}. "
    embed_text += f"{description}. "
    if notes:
        embed_text += f"Notes: {notes}. "
    if tag_list:
        embed_text += f"Tags: {', '.join(tag_list)}."

    # ── 3. Generate embedding ─────────────────────────────────────────────────
    # Multimodal if image uploaded — fuses visual + text into one vector
    # Text-only for video (embed description only; video frame extraction = future)
    try:
        if media_type == "image" and file_path:
            embedding = embedding_service.embed_entry(embed_text, file_path)
        else:
            embedding = embedding_service.embed_entry(embed_text)
    except Exception as e:
        logger.error(f"Embedding failed: {e}")
        raise HTTPException(status_code=500, detail=f"Embedding failed: {str(e)}")

    # ── 4. Store in vector DB ─────────────────────────────────────────────────
    metadata = {
        "title": title,
        "description": description,
        "shot_type": shot_type or "",
        "notes": notes or "",
        "tags": ",".join(tag_list),          # ChromaDB stores as string
        "media_type": media_type or "",
        "file_url": file_url or "",
        "created_at": datetime.utcnow().isoformat(),
    }

    try:
        vector_store.add(entry_id, embedding, metadata)
    except Exception as e:
        logger.error(f"Vector store insert failed: {e}")
        raise HTTPException(status_code=500, detail=f"Storage failed: {str(e)}")

    logger.info(f"Entry saved: {entry_id} | {title} | media: {media_type}")

    return UploadResponse(
        id=entry_id,
        title=title,
        message="Shot saved and embedded successfully.",
        file_url=file_url,
    )


@router.get("/entries/count")
async def entry_count():
    return {"count": vector_store.count()}