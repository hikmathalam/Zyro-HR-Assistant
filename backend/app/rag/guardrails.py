import re
import logging
from typing import List, Tuple
from langchain_core.documents import Document
from app.config import settings

logger = logging.getLogger(__name__)

# Standard refusal messages specified in requirements
UNSUPPORTED_INFO_MESSAGE = "I could not find this information in the HR documents."

UNRELATED_TOPIC_MESSAGE = (
    "I am the Zyro HR Assistant. I can only assist with questions regarding "
    "Zyro Dynamics Pvt. Ltd. HR policies, employee benefits, and workplace rules. "
    "For other topics, please consult the appropriate external resources or company departments."
)

# Common general knowledge / programming / out-of-scope triggers
GENERAL_KNOWLEDGE_PATTERNS = [
    r"\bcapital of\b",
    r"\bwho is (the )?ceo of (google|apple|microsoft|amazon|facebook|meta|tesla|twitter)\b",
    r"\bwrite (a |some )?(python|javascript|code|script|sql|html|css|program)\b",
    r"\bweather in\b",
    r"\bpresident of\b",
    r"\bprime minister of\b",
    r"\btell me a joke\b",
    r"\bwho won the\b",
    r"\bhow to cook\b",
    r"\bfavorite (food|movie|song|color|actor)\b",
    r"\b(wifi|wi-fi) password\b",
]

# Zyro HR policy domains / keywords that indicate valid HR scope
HR_RELEVANT_KEYWORDS = {
    "leave", "vacation", "earned leave", "casual leave", "sick leave", "maternity", "paternity",
    "bereavement", "compensatory", "compoff", "salary", "payroll", "allowance", "wellness",
    "gratuity", "provident fund", "pf", "epfo", "notice period", "probation", "resignation",
    "separation", "onboarding", "appraisal", "performance", "bonus", "esop", "insurance",
    "health", "medical", "harassment", "posh", "icc", "code of conduct", "wfh", "work from home",
    "remote", "travel", "expense", "reimbursement", "working hours", "attendance", "counselling",
    "eap", "benefits", "policy", "zyro", "employment", "termination", "disciplinary", "security",
    "confidentiality", "asset", "laptop"
}

def is_strictly_unrelated(question: str) -> bool:
    """
    Fast rule-based filter for obvious out-of-scope general knowledge,
    coding questions, or non-HR queries.
    """
    q_lower = question.lower().strip()
    
    # Check general knowledge patterns
    for pattern in GENERAL_KNOWLEDGE_PATTERNS:
        if re.search(pattern, q_lower):
            return True
            
    # Check if prompt injection is attempted
    injection_patterns = [
        r"ignore (all )?previous instructions",
        r"disregard (all )?instructions",
        r"reveal (your |the )?(api key|secret|system prompt)",
        r"system prompt",
        r"you are now a",
        r"dan mode",
    ]
    for pattern in injection_patterns:
        if re.search(pattern, q_lower):
            return True
            
    return False

def assess_relevance_and_guard(
    question: str,
    retrieved_docs_with_scores: List[Tuple[Document, float]]
) -> Tuple[bool, str, str]:
    """
    Validates question scope and retrieved context relevance.
    Returns:
      (is_allowed: bool, status: 'ok' | 'unrelated' | 'unsupported', message: str)
    """
    # 1. Obvious out-of-scope check
    if is_strictly_unrelated(question):
        return False, "unrelated", UNRELATED_TOPIC_MESSAGE

    if not retrieved_docs_with_scores:
        return False, "unsupported", UNSUPPORTED_INFO_MESSAGE

    best_doc, best_score = retrieved_docs_with_scores[0]
    q_words = set(re.findall(r"\w+", question.lower()))
    has_hr_keyword = bool(q_words.intersection(HR_RELEVANT_KEYWORDS))

    # FAISS distance threshold check:
    # Highly distant queries (> 1.65 L2 distance) with no HR domain terms are unrelated
    if best_score > 1.60 and not has_hr_keyword:
        logger.info(f"Question rejected due to high distance score ({best_score:.4f}) and no HR keywords: '{question}'")
        return False, "unrelated", UNRELATED_TOPIC_MESSAGE

    # If the distance is borderline (> 1.45) and no chunk content matches key terms in question
    if best_score > 1.45:
        # Check if any retrieved document actually contains words from the question
        significant_words = [w for w in q_words if len(w) > 3 and w not in {"what", "when", "where", "which", "does", "have", "many", "much"}]
        found_in_docs = any(
            any(w in doc.page_content.lower() for w in significant_words)
            for doc, _ in retrieved_docs_with_scores
        )
        if not found_in_docs:
            logger.info(f"Question rejected: score {best_score:.4f} and zero query terms in retrieved documents.")
            return False, "unsupported", UNSUPPORTED_INFO_MESSAGE

    return True, "ok", ""

