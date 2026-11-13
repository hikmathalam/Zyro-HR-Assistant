import os

# MUST set offline flags BEFORE any huggingface or transformers imports
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

import logging
from typing import Optional
from langchain_huggingface import HuggingFaceEmbeddings
from app.config import settings

logger = logging.getLogger(__name__)

_embeddings_instance: Optional[HuggingFaceEmbeddings] = None

def get_embeddings() -> HuggingFaceEmbeddings:
    """
    Returns a singleton instance of HuggingFaceEmbeddings using
    sentence-transformers/all-MiniLM-L6-v2.
    Matches the exact embedding model used during Kaggle indexing.
    """
    global _embeddings_instance
    if _embeddings_instance is None:
        logger.info(f"Initializing HuggingFaceEmbeddings: {settings.EMBEDDING_MODEL_NAME}")
        try:
            _embeddings_instance = HuggingFaceEmbeddings(
                model_name=settings.EMBEDDING_MODEL_NAME,
                encode_kwargs={"normalize_embeddings": False}
            )
        except Exception as e:
            logger.error(f"Error loading embeddings: {e}")
            raise RuntimeError(f"Could not load HuggingFaceEmbeddings: {e}")
        
        # Verify dimension
        test_vec = _embeddings_instance.embed_query("dimension check")
        if len(test_vec) != settings.EMBEDDING_DIMENSION:
            raise ValueError(
                f"Embedding dimension mismatch: expected {settings.EMBEDDING_DIMENSION}, got {len(test_vec)}"
            )
        logger.info(f"Embeddings loaded successfully (dim={len(test_vec)}).")
    
    return _embeddings_instance
