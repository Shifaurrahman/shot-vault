"""
Storage Service
────────────────
POC  : Local disk  (./data/uploads)
Prod : AWS S3      (change STORAGE_BACKEND=s3 in .env)
"""

import shutil
import uuid
from pathlib import Path
from fastapi import UploadFile
from config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


# ─── Local Storage ─────────────────────────────────────────────────────────────

class LocalStorage:
    def __init__(self):
        self.base_dir = Path(settings.local_storage_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Local storage ready at: {self.base_dir}")

    async def save(self, file: UploadFile, entry_id: str) -> tuple[str, str]:
        """
        Save uploaded file to disk.
        Returns (file_path, file_url).
        """
        suffix = Path(file.filename).suffix.lower()
        filename = f"{entry_id}{suffix}"
        file_path = self.base_dir / filename

        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # URL that FastAPI serves via /files static mount
        file_url = f"/files/{filename}"

        logger.info(f"Saved file: {file_path}")
        return str(file_path), file_url

    def delete(self, file_url: str) -> None:
        filename = file_url.split("/files/")[-1]
        file_path = self.base_dir / filename
        if file_path.exists():
            file_path.unlink()
            logger.info(f"Deleted file: {file_path}")


# ─── S3 Storage ────────────────────────────────────────────────────────────────

class S3Storage:
    def __init__(self):
        import boto3
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region,
        )
        self.bucket = settings.aws_bucket_name
        logger.info(f"S3 storage ready — bucket: {self.bucket}")

    async def save(self, file: UploadFile, entry_id: str) -> tuple[str, str]:
        suffix = Path(file.filename).suffix.lower()
        key = f"uploads/{entry_id}{suffix}"

        self.s3.upload_fileobj(
            file.file,
            self.bucket,
            key,
            ExtraArgs={"ContentType": file.content_type},
        )

        file_url = f"https://{self.bucket}.s3.{settings.aws_region}.amazonaws.com/{key}"
        logger.info(f"Uploaded to S3: {key}")
        return key, file_url

    def delete(self, file_url: str) -> None:
        key = file_url.split(".amazonaws.com/")[-1]
        self.s3.delete_object(Bucket=self.bucket, Key=key)


# ─── Factory ───────────────────────────────────────────────────────────────────

def get_storage():
    if settings.storage_backend == "local":
        return LocalStorage()
    elif settings.storage_backend == "s3":
        return S3Storage()
    else:
        raise ValueError(f"Unsupported STORAGE_BACKEND: {settings.storage_backend}")


# Singleton
storage_service = get_storage()