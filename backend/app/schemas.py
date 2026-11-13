from typing import List, Optional
from pydantic import BaseModel, Field

class SourceCitation(BaseModel):
    file: str = Field(..., description="PDF document filename")
    page: str = Field(..., description="Page number or label in the document")
    snippet: Optional[str] = Field(None, description="Relevant excerpt from document chunk")

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=2000, description="Employee question about Zyro HR policies")
    session_id: Optional[str] = Field(None, description="Optional conversation session identifier")

class ChatResponse(BaseModel):
    answer: str = Field(..., description="Answer grounded strictly in Zyro HR policy documents")
    sources: List[SourceCitation] = Field(default_factory=list, description="Document sources used for the response")
    is_refusal: bool = Field(default=False, description="Whether the request was refused as out-of-scope or ungrounded")

class HealthResponse(BaseModel):
    status: str = Field(..., description="API operational status")
    app_name: str
    version: str
    index_loaded: bool
    total_indexed_chunks: int
    groq_configured: bool
    model: str

class AdminReindexRequest(BaseModel):
    admin_key: str = Field(..., description="Admin authorization key")

class AdminReindexResponse(BaseModel):
    status: str
    message: str
    total_chunks: int

