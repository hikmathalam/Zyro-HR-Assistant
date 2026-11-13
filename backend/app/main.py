import json
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
from fastapi import FastAPI, HTTPException, Header, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from app.config import settings
from app.schemas import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    AdminReindexRequest,
    AdminReindexResponse
)
from app.rag.vectorstore import get_vectorstore
from app.rag.generator import generator, format_context, build_user_prompt, SYSTEM_PROMPT
from app.rag.retriever import retrieve_documents, retrieve_with_scores, extract_citations
from app.rag.guardrails import assess_relevance_and_guard, UNSUPPORTED_INFO_MESSAGE
from app.services.chat_service import chat_service

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("zyro_api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Zyro HR Assistant API...")
    yield
    logger.info("Shutting down Zyro HR Assistant API.")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Intelligent RAG HR Assistant API for Zyro Dynamics Pvt. Ltd."
)

# CORS configuration
origins = settings.get_cors_origins()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["General"])
def root():
    return {
        "message": "Welcome to Zyro HR Assistant API",
        "company": "Zyro Dynamics Pvt. Ltd.",
        "status": "operational",
        "docs_url": "/docs"
    }

@app.get("/health", response_model=HealthResponse, tags=["Monitoring"])
def health():
    try:
        vs = get_vectorstore()
        index_loaded = True
        total_chunks = vs.index.ntotal
    except Exception as e:
        logger.warning(f"Health check vectorstore warning: {e}")
        index_loaded = False
        total_chunks = 0

    return HealthResponse(
        status="healthy" if index_loaded else "degraded",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        index_loaded=index_loaded,
        total_indexed_chunks=total_chunks,
        groq_configured=generator.is_configured(),
        model=settings.GROQ_MODEL
    )

@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
def chat(request: ChatRequest):
    """
    Standard RAG Chat Endpoint:
    Processes employee question, evaluates guardrails, retrieves relevant chunks,
    and returns grounded answer with source citations.
    """
    try:
        response = chat_service.process_chat(request)
        return response
    except Exception as e:
        logger.error(f"Error processing chat request: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request. Please try again."
        )

@app.post("/chat/stream", tags=["Chat"])
async def chat_stream(request: ChatRequest):
    """
    Streaming Chat Endpoint (Server-Sent Events):
    Streams generated tokens progressively to frontend UI.
    """
    question = request.question.strip()
    
    # 1. Guardrail check
    docs_with_scores = retrieve_with_scores(question, k=4)
    is_allowed, st, guard_msg = assess_relevance_and_guard(question, docs_with_scores)
    
    if not is_allowed:
        async def refusal_stream() -> AsyncGenerator[str, None]:
            yield f"data: {json.dumps({'token': guard_msg})}\n\n"
            yield f"data: {json.dumps({'done': True, 'sources': [], 'is_refusal': True})}\n\n"
        return StreamingResponse(refusal_stream(), media_type="text/event-stream")

    # 2. Retrieve MMR docs
    mmr_docs = retrieve_documents(question)
    citations = extract_citations(mmr_docs)

    # 3. Stream Groq completion if configured
    async def token_generator() -> AsyncGenerator[str, None]:
        if not generator.is_configured():
            fallback_answer = generator._fallback_extract_answer(question, mmr_docs)
            yield f"data: {json.dumps({'token': fallback_answer})}\n\n"
            yield f"data: {json.dumps({'done': True, 'sources': [c.model_dump() for c in citations], 'is_refusal': False})}\n\n"
            return

        try:
            context_text = format_context(mmr_docs)
            user_prompt = build_user_prompt(question, context_text)
            
            stream = generator.client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=settings.GROQ_TEMPERATURE,
                max_tokens=settings.GROQ_MAX_TOKENS,
                stream=True
            )
            
            collected_text = []
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    token = chunk.choices[0].delta.content
                    collected_text.append(token)
                    yield f"data: {json.dumps({'token': token})}\n\n"
            
            full_text = "".join(collected_text)
            is_refusal = (
                UNSUPPORTED_INFO_MESSAGE.lower() in full_text.lower()
                or "only assist with questions regarding zyro dynamics" in full_text.lower()
            )
            final_citations = [] if is_refusal else [c.model_dump() for c in citations]
            yield f"data: {json.dumps({'done': True, 'sources': final_citations, 'is_refusal': is_refusal})}\n\n"
            
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(token_generator(), media_type="text/event-stream")

@app.post("/admin/reindex", response_model=AdminReindexResponse, tags=["Admin"])
def admin_reindex(
    req: AdminReindexRequest,
    x_admin_key: Optional[str] = Header(None, alias="X-Admin-Key")
):
    """
    Protected Administrative Endpoint:
    Reloads the FAISS index from disk.
    Requires authentication via X-Admin-Key header or admin_key in request body.
    """
    header_val = x_admin_key if isinstance(x_admin_key, str) else None
    provided_key = header_val or req.admin_key
    if not provided_key or provided_key != settings.ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Invalid admin credentials."
        )

    try:
        vs = get_vectorstore(force_reload=True)
        return AdminReindexResponse(
            status="success",
            message="FAISS vector index reloaded successfully.",
            total_chunks=vs.index.ntotal
        )
    except Exception as e:
        logger.error(f"Reindex failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Reindex error: {str(e)}"
        )

