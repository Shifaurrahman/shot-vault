"""
ShotVault — FastAPI Backend
────────────────────────────
Run:  uvicorn main:app --reload
Docs: http://localhost:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import logging

from config import get_settings
from models.schemas import HealthResponse
from routes import upload, query

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)
settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="RAG-based filmmaking shot knowledge base",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded media files
uploads_dir = Path(settings.local_storage_dir)
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/files", StaticFiles(directory=str(uploads_dir)), name="files")

app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(query.router,  prefix="/api", tags=["Query"])


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="ok",
        app=settings.app_name,
        version=settings.app_version,
        embedding_model=settings.embedding_model,
        vector_db=settings.vector_db,
        storage_backend=settings.storage_backend,
        llm_model=settings.anthropic_model,
        llm_enabled=bool(settings.anthropic_api_key),
    )


@app.get("/")
async def root():
    return {
        "message": f"{settings.app_name} API is running.",
        "docs": "/docs",
        "health": "/health",
    }


@app.on_event("startup")
async def startup_event():
    logger.info(f"─── {settings.app_name} v{settings.app_version} starting ───")
    logger.info(f"Embedding model : {settings.embedding_model}")
    logger.info(f"Vector DB       : {settings.vector_db}")
    logger.info(f"Storage backend : {settings.storage_backend}")
    logger.info(f"LLM model       : {settings.anthropic_model}")
    logger.info(f"LLM enabled     : {bool(settings.anthropic_api_key)}")
    logger.info(f"CORS origins    : {settings.cors_origins_list}")
    logger.info("Ready. Docs at http://localhost:8000/docs")