import os
import logging
from pathlib import Path
from typing import Optional

# Ensure faiss native C++ runtime is imported before other thread pools
try:
    import faiss
except Exception as e:
    faiss = None

from langchain_community.vectorstores import FAISS
from app.config import settings
from app.rag.embeddings import get_embeddings

logger = logging.getLogger(__name__)

_vectorstore_instance: Optional[FAISS] = None

def get_vectorstore(force_reload: bool = False) -> FAISS:
    """
    Loads and returns the FAISS vectorstore instance.
    Inspects index presence, dimensionality, and total chunk count.
    """
    global _vectorstore_instance
    if _vectorstore_instance is not None and not force_reload:
        return _vectorstore_instance

    index_dir = Path(settings.FAISS_INDEX_DIR)
    if not (index_dir / "index.faiss").exists():
        # Fallback check relative to backend BASE_DIR
        from app.config import BASE_DIR
        candidate = BASE_DIR / settings.FAISS_INDEX_DIR
        if (candidate / "index.faiss").exists():
            index_dir = candidate

    faiss_file = index_dir / "index.faiss"
    pkl_file = index_dir / "index.pkl"

    if not faiss_file.exists() or not pkl_file.exists():
        err_msg = (
            f"FAISS index files missing in directory '{index_dir}'. "
            f"Expected 'index.faiss' and 'index.pkl'. "
            "Please copy the exported Kaggle index to backend/data/hr_faiss_index/."
        )
        logger.error(err_msg)
        raise FileNotFoundError(err_msg)

    logger.info(f"Loading FAISS index from: {index_dir}")
    embeddings = get_embeddings()

    try:
        # Load local FAISS index (pickle deserialization is required for LangChain's InMemoryDocstore)
        vectorstore = FAISS.load_local(
            folder_path=str(index_dir),
            embeddings=embeddings,
            allow_dangerous_deserialization=True
        )
    except Exception as e:
        logger.error(f"Failed to load FAISS index: {e}")
        raise RuntimeError(f"Error loading FAISS vectorstore: {e}")

    # Dimensionality and health check
    total_chunks = vectorstore.index.ntotal
    dim = vectorstore.index.d

    if dim != settings.EMBEDDING_DIMENSION:
        raise ValueError(
            f"Index dimension mismatch: FAISS has dimension {dim}, but {settings.EMBEDDING_DIMENSION} was expected."
        )

    logger.info(f"FAISS index loaded successfully: {total_chunks} chunks, {dim} dimensions.")
    _vectorstore_instance = vectorstore
    return _vectorstore_instance

