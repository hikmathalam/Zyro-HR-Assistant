import logging
from typing import List, Tuple
from langchain_core.documents import Document
from app.config import settings
from app.rag.vectorstore import get_vectorstore
from app.schemas import SourceCitation

logger = logging.getLogger(__name__)

def get_mmr_retriever():
    """
    Returns an MMR retriever configured to the exact Kaggle parameters:
    k=4, fetch_k=12, lambda_mult=0.5
    """
    vectorstore = get_vectorstore()
    return vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": settings.RETRIEVER_K,
            "fetch_k": settings.RETRIEVER_FETCH_K,
            "lambda_mult": settings.RETRIEVER_LAMBDA_MULT
        }
    )

def retrieve_documents(query: str) -> List[Document]:
    """
    Retrieves top documents using MMR.
    """
    retriever = get_mmr_retriever()
    docs = retriever.invoke(query)
    logger.info(f"Retrieved {len(docs)} documents for query: '{query}'")
    return docs

def retrieve_with_scores(query: str, k: int = 4) -> List[Tuple[Document, float]]:
    """
    Retrieves documents along with their L2 distance scores from FAISS.
    Lower score indicates higher similarity in FAISS L2 index.
    """
    vectorstore = get_vectorstore()
    return vectorstore.similarity_search_with_score(query, k=k)

def extract_citations(docs: List[Document]) -> List[SourceCitation]:
    """
    Extracts deduplicated, structured source citations from retrieved Document objects.
    Preserves document filename, page number, and brief snippet.
    """
    citations: List[SourceCitation] = []
    seen = set()

    for doc in docs:
        meta = doc.metadata or {}
        raw_source = meta.get("source", "Unknown_Document.pdf")
        # Clean file path to just filename
        filename = raw_source.replace("\\", "/").split("/")[-1]
        
        # Determine 1-based page number
        page_label = meta.get("page_label")
        if page_label is not None:
            page_str = str(page_label)
        elif "page" in meta:
            try:
                page_str = str(int(meta["page"]) + 1)
            except Exception:
                page_str = str(meta["page"])
        else:
            page_str = "1"

        citation_key = (filename, page_str)
        if citation_key not in seen:
            seen.add(citation_key)
            snippet = doc.page_content.strip()
            # Truncate snippet cleanly
            snippet_summary = " ".join(snippet.split()[:40]) + ("..." if len(snippet.split()) > 40 else "")
            citations.append(
                SourceCitation(
                    file=filename,
                    page=page_str,
                    snippet=snippet_summary
                )
            )

    return citations

