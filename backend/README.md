# ShotVault — Backend

RAG-based filmmaking shot knowledge base.

## Stack
| Layer | POC | Production |
|---|---|---|
| API | FastAPI | FastAPI |
| Embedding | Qwen3-VL-Embedding-2B (multimodal) | same |
| Vector DB | ChromaDB (local) | Qdrant / pgvector |
| Storage | Local disk | AWS S3 |

## Setup

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure
cp .env .env.local              # edit if needed
# Key settings in .env:
#   EMBEDDING_DEVICE=cpu        # change to cuda if you have GPU
#   VECTOR_DB=chromadb          # chromadb | qdrant
#   STORAGE_BACKEND=local       # local | s3

# 4. Run
uvicorn main:app --reload
```

API docs: http://localhost:8000/docs

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/upload` | Upload shot + media, embed, store |
| POST | `/api/query` | Natural language search |
| GET | `/api/entries/count` | Total entries stored |
| GET | `/api/query/suggestions` | Suggestion chips for UI |
| GET | `/health` | Health check |
| GET | `/files/{filename}` | Serve uploaded media |

## Upload (multipart/form-data)
```
title        string  required
description  string  required
shot_type    string  optional
notes        string  optional
tags         string  optional  comma-separated: "Beach,Night,Aerial"
file         file    optional  image or video
```

## Query (JSON)
```json
{
  "query": "extreme wide shot at beach",
  "top_k": 5,
  "filter_type": "image"   // "image" | "video" | null = both
}
```

## Switching to production

**Embedding** — already using Qwen3-VL-Embedding-2B. Set `EMBEDDING_DEVICE=cuda`.

**Vector DB** — change `.env`:
```
VECTOR_DB=qdrant
QDRANT_URL=http://your-qdrant-server:6333
```
Start Qdrant: `docker run -p 6333:6333 qdrant/qdrant`

**Storage** — change `.env`:
```
STORAGE_BACKEND=s3
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_BUCKET_NAME=shotvault
```

No code changes needed — only `.env`.

## Folder structure
```
shotvault-backend/
├── .env                  ← all config here
├── config.py             ← reads .env, typed settings
├── main.py               ← FastAPI app, routes, CORS
├── requirements.txt
├── models/
│   └── schemas.py        ← Pydantic request/response models
├── routes/
│   ├── upload.py         ← POST /api/upload
│   └── query.py          ← POST /api/query
├── services/
│   ├── embedding.py      ← Qwen3-VL embedding (multimodal)
│   ├── vector_store.py   ← ChromaDB / Qdrant
│   └── storage.py        ← local disk / S3
└── data/                 ← auto-created
    ├── chroma/           ← ChromaDB files
    └── uploads/          ← uploaded media
```