from pathlib import Path
from typing import List, Union
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directory for backend
BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Zyro HR Assistant API"
    APP_VERSION: str = "1.0.0"
    DEBUG: Union[bool, str] = False
    ENVIRONMENT: str = "development"
    
    # Server & CORS
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://localhost:8501",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8501",
        "https://*.vercel.app"
    ]
    
    # Groq LLM
    GROQ_API_KEY: str = Field(default="", description="Groq API key")
    GROQ_MODEL: str = Field(default="llama-3.3-70b-versatile", description="Default Groq LLM model")
    GROQ_FALLBACK_MODEL: str = "llama-3.1-8b-instant"
    GROQ_TEMPERATURE: float = 0.1
    GROQ_MAX_TOKENS: int = 1024
    
    # Embeddings & FAISS
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    FAISS_INDEX_DIR: str = str(BASE_DIR / "data" / "hr_faiss_index")
    EMBEDDING_DIMENSION: int = 384
    
    # Retrieval Configuration (Matching Kaggle setup)
    RETRIEVER_K: int = 4
    RETRIEVER_FETCH_K: int = 12
    RETRIEVER_LAMBDA_MULT: float = 0.5
    
    # Guardrails and Relevance
    SIMILARITY_DISTANCE_THRESHOLD: float = 1.35  # L2 distance threshold for FAISS
    
    # Admin Protection
    ADMIN_API_KEY: str = Field(default="zyro-admin-secret-token", description="Key to protect admin endpoints")

    model_config = SettingsConfigDict(
        env_file=(str(BASE_DIR / ".env"), str(PROJECT_ROOT / ".env")),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def get_cors_origins(self) -> List[str]:
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
        return self.CORS_ORIGINS

settings = Settings()
