
"""
Embedding Service
─────────────────
POC  : Qwen/Qwen3-VL-Embedding-2B  (multimodal — text + image)
Swap : change EMBEDDING_MODEL in .env — nothing else changes.

Qwen3-VL-Embedding-2B can embed:
  • Pure text  → pass text string
  • Image+text → pass image path + text together
  • Image only → pass image path only

This gives true multimodal retrieval:
  text query → finds relevant images/videos by their visual+text embedding.
"""

import torch
import numpy as np
from pathlib import Path
from PIL import Image
from transformers import AutoProcessor, AutoModel
from config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


class EmbeddingService:
    def __init__(self):
        self.model = None
        self.processor = None
        self._loaded = False

    def _load(self):
        """Lazy load — only loads model on first use."""
        if self._loaded:
            return

        logger.info(f"Loading embedding model: {settings.embedding_model}")
        logger.info(f"Device: {settings.embedding_device}")

        self.processor = AutoProcessor.from_pretrained(
            settings.embedding_model,
            trust_remote_code=True,
        )
        self.model = AutoModel.from_pretrained(
            settings.embedding_model,
            trust_remote_code=True,
        ).to(settings.embedding_device)
        self.model.eval()

        self._loaded = True
        logger.info("Embedding model loaded successfully.")

    def embed_text(self, text: str) -> list[float]:
        """
        Embed a plain text string.
        Used for: query embedding, description-only entries.
        """
        self._load()

        inputs = self.processor(
            text=text,
            return_tensors="pt",
            padding=True,
            truncation=True,
        ).to(settings.embedding_device)

        with torch.no_grad():
            outputs = self.model(**inputs)

        # Mean pool over token embeddings
        embedding = outputs.last_hidden_state.mean(dim=1).squeeze()
        embedding = embedding / embedding.norm()  # L2 normalize

        return embedding.cpu().tolist()

    def embed_multimodal(self, text: str, image_path: str) -> list[float]:
        """
        Embed text + image together (true multimodal).
        Used for: upload entries that have both description and image.

        This is the key advantage of Qwen3-VL-Embedding —
        the image content and text are fused into ONE vector.
        So querying "beach at sunset" can retrieve images
        even if the description doesn't say "beach" explicitly.
        """
        self._load()
        image = Image.open(image_path).convert("RGB")

        # Qwen3-VL requires messages format with vision tokens via chat template
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": text},
                ],
            }
        ]

        # Apply the chat template to get properly formatted text with vision tokens
        prompt = self.processor.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=False,
        )

        inputs = self.processor(
            text=prompt,
            images=[image],
            return_tensors="pt",
            padding=True,
            truncation=True,
        ).to(settings.embedding_device)

        with torch.no_grad():
            outputs = self.model(**inputs)

        embedding = outputs.last_hidden_state.mean(dim=1).squeeze()
        embedding = embedding / embedding.norm()
        return embedding.cpu().tolist()
        

    def embed_entry(self, text: str, image_path: str | None = None) -> list[float]:
        """
        Smart embed — uses multimodal if image exists, text-only otherwise.
        Call this for all upload entries.
        """
        if image_path and Path(image_path).exists():
            logger.info(f"Embedding multimodal: text + image ({image_path})")
            return self.embed_multimodal(text, image_path)
        else:
            logger.info("Embedding text only (no image provided)")
            return self.embed_text(text)


# Singleton — model loads once, reused across all requests
embedding_service = EmbeddingService()
