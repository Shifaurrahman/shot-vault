"""
Vector Store Service
─────────────────────
POC  : ChromaDB  (local file, zero setup)
Prod : Qdrant    (change VECTOR_DB=qdrant in .env)

Switching DB = change one line in .env. Code stays the same.
"""

from config import get_settings
from models.schemas import ShotResult
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


# ─── ChromaDB implementation ───────────────────────────────────────────────────

class ChromaVectorStore:
    def __init__(self):
        import chromadb
        from pathlib import Path

        Path(settings.chroma_persist_dir).mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        self.collection = self.client.get_or_create_collection(
            name=settings.chroma_collection,
            metadata={"hnsw:space": "cosine"},  # cosine similarity
        )
        logger.info(f"ChromaDB ready — collection: {settings.chroma_collection}")

    def add(
        self,
        id: str,
        embedding: list[float],
        metadata: dict,
    ) -> None:
        """Store one shot entry."""
        self.collection.add(
            ids=[id],
            embeddings=[embedding],
            metadatas=[metadata],
        )
        logger.info(f"Added entry {id} to ChromaDB")

    def query(
        self,
        embedding: list[float],
        top_k: int = 5,
        filter_type: str | None = None,
    ) -> list[ShotResult]:
        """Similarity search. Optionally filter by media type."""
        where = {"media_type": filter_type} if filter_type else None

        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k,
            where=where,
            include=["metadatas", "distances"],
        )

        shots = []
        for i, meta in enumerate(results["metadatas"][0]):
            distance = results["distances"][0][i]
            score = 1 - distance  # cosine distance → similarity score

            shots.append(ShotResult(
                id=results["ids"][0][i],
                title=meta.get("title", ""),
                description=meta.get("description", ""),
                shot_type=meta.get("shot_type"),
                notes=meta.get("notes"),
                tags=meta.get("tags", "").split(",") if meta.get("tags") else [],
                media_type=meta.get("media_type"),
                file_url=meta.get("file_url"),
                score=round(score, 4),
                created_at=meta.get("created_at"),
            ))

        return shots

    def delete(self, id: str) -> None:
        self.collection.delete(ids=[id])

    def count(self) -> int:
        return self.collection.count()


# ─── Qdrant implementation ─────────────────────────────────────────────────────

class QdrantVectorStore:
    def __init__(self):
        from qdrant_client import QdrantClient
        from qdrant_client.models import Distance, VectorParams

        self.client = QdrantClient(url=settings.qdrant_url)

        # Create collection if it doesn't exist
        existing = [c.name for c in self.client.get_collections().collections]
        if settings.qdrant_collection not in existing:
            self.client.create_collection(
                collection_name=settings.qdrant_collection,
                vectors_config=VectorParams(
                    size=settings.embedding_dim,
                    distance=Distance.COSINE,
                ),
            )
        self.collection = settings.qdrant_collection
        logger.info(f"Qdrant ready — collection: {self.collection}")

    def add(self, id: str, embedding: list[float], metadata: dict) -> None:
        from qdrant_client.models import PointStruct

        self.client.upsert(
            collection_name=self.collection,
            points=[PointStruct(id=id, vector=embedding, payload=metadata)],
        )

    def query(
        self,
        embedding: list[float],
        top_k: int = 5,
        filter_type: str | None = None,
    ) -> list[ShotResult]:
        from qdrant_client.models import Filter, FieldCondition, MatchValue

        query_filter = None
        if filter_type:
            query_filter = Filter(
                must=[FieldCondition(key="media_type", match=MatchValue(value=filter_type))]
            )

        results = self.client.search(
            collection_name=self.collection,
            query_vector=embedding,
            limit=top_k,
            query_filter=query_filter,
            with_payload=True,
        )

        shots = []
        for r in results:
            meta = r.payload
            shots.append(ShotResult(
                id=str(r.id),
                title=meta.get("title", ""),
                description=meta.get("description", ""),
                shot_type=meta.get("shot_type"),
                notes=meta.get("notes"),
                tags=meta.get("tags", []),
                media_type=meta.get("media_type"),
                file_url=meta.get("file_url"),
                score=round(r.score, 4),
                created_at=meta.get("created_at"),
            ))

        return shots

    def delete(self, id: str) -> None:
        from qdrant_client.models import PointIdsList
        self.client.delete(
            collection_name=self.collection,
            points_selector=PointIdsList(points=[id]),
        )

    def count(self) -> int:
        return self.client.count(collection_name=self.collection).count


# ─── Factory — reads VECTOR_DB from .env ──────────────────────────────────────

def get_vector_store():
    """
    Returns the right vector store based on .env setting.
    Change VECTOR_DB=qdrant to switch. No code changes needed.
    """
    if settings.vector_db == "chromadb":
        return ChromaVectorStore()
    elif settings.vector_db == "qdrant":
        return QdrantVectorStore()
    else:
        raise ValueError(f"Unsupported VECTOR_DB: {settings.vector_db}")


# Singleton
vector_store = get_vector_store()