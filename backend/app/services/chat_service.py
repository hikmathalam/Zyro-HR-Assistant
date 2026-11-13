import logging
from typing import List
from app.schemas import ChatRequest, ChatResponse, SourceCitation
from app.rag.retriever import retrieve_documents, retrieve_with_scores, extract_citations
from app.rag.guardrails import assess_relevance_and_guard, UNSUPPORTED_INFO_MESSAGE, UNRELATED_TOPIC_MESSAGE
from app.rag.generator import generator

logger = logging.getLogger(__name__)

class ChatService:
    @staticmethod
    def process_chat(request: ChatRequest) -> ChatResponse:
        question = request.question.strip()
        logger.info(f"Processing question: '{question}'")

        # 1. Retrieve candidates with distances for guardrail evaluation
        docs_with_scores = retrieve_with_scores(question, k=4)
        
        # 2. Evaluate Guardrails
        is_allowed, status, guard_message = assess_relevance_and_guard(question, docs_with_scores)
        
        if not is_allowed:
            logger.info(f"Guardrail triggered. Status: {status}")
            return ChatResponse(
                answer=guard_message,
                sources=[],
                is_refusal=True
            )

        # 3. Use MMR retrieval to get top diverse document chunks
        mmr_docs = retrieve_documents(question)
        if not mmr_docs:
            return ChatResponse(
                answer=UNSUPPORTED_INFO_MESSAGE,
                sources=[],
                is_refusal=True
            )

        # 4. Generate answer using Groq
        answer = generator.generate_answer(question, mmr_docs)

        # 5. Check if LLM refused or indicated missing info
        is_refusal = (
            UNSUPPORTED_INFO_MESSAGE.lower() in answer.lower()
            or "only assist with questions regarding zyro dynamics" in answer.lower()
        )

        # 6. Extract source citations actually retrieved and used
        citations = [] if is_refusal else extract_citations(mmr_docs)

        return ChatResponse(
            answer=answer,
            sources=citations,
            is_refusal=is_refusal
        )

chat_service = ChatService()

