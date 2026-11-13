import os
import sys
import io
import time
from pathlib import Path
import streamlit as st
import pandas as pd
import requests

# 1. Page Configuration
st.set_page_config(
    page_title="Zyro HR Assistant | Zyro Dynamics Pvt. Ltd.",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Path Setup for Independent or Monorepo Execution
APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Ensure Faiss native C++ runtime loads cleanly
try:
    import faiss
except Exception:
    pass

# Read Groq API key from Streamlit secrets if present
try:
    if "GROQ_API_KEY" in st.secrets:
        os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
except Exception:
    pass

DEFAULT_API_URL = os.environ.get("BACKEND_API_URL", "http://localhost:8000")

# 3. Custom CSS Theme
st.markdown("""
<style>
    .main-title {
        font-size: 2rem;
        font-weight: 700;
        color: #1e1b4b;
        letter-spacing: -0.02em;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 0.95rem;
        color: #475569;
        margin-bottom: 1.2rem;
    }
    .badge-rag {
        background-color: #e0e7ff;
        color: #4338ca;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 9999px;
        border: 1px solid #c7d2fe;
        text-transform: uppercase;
        display: inline-block;
        margin-left: 8px;
    }
    .citation-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 10px 14px;
        margin-top: 8px;
        font-size: 0.84rem;
    }
    .citation-page {
        background-color: #4f46e5;
        color: #ffffff;
        font-size: 0.72rem;
        font-weight: 600;
        padding: 2px 7px;
        border-radius: 4px;
        display: inline-block;
        margin-right: 8px;
    }
    .refusal-alert {
        background-color: #fffbeb;
        border: 1px solid #fef3c7;
        color: #92400e;
        border-radius: 8px;
        padding: 12px 16px;
        margin-top: 8px;
        font-size: 0.88rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px 6px 0px 0px;
        padding: 8px 16px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# 4. Helper: Query HR Assistant (Dual Mode: HTTP Backend or In-Process RAG)
def query_hr_assistant(question: str):
    """
    Attempts to query the running FastAPI backend via HTTP.
    If the backend is not running, falls back seamlessly to the internal ChatService.
    Ensures 100% independence on Streamlit Community Cloud.
    """
    # Attempt HTTP query first
    try:
        resp = requests.post(
            f"{DEFAULT_API_URL}/chat",
            json={"question": question},
            timeout=8
        )
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass

    # Direct In-Process Fallback using local chat_service
    try:
        from app.schemas import ChatRequest
        from app.services.chat_service import chat_service
        req = ChatRequest(question=question)
        res = chat_service.process_chat(req)
        return {
            "answer": res.answer,
            "sources": [s.model_dump() for s in res.sources],
            "is_refusal": res.is_refusal
        }
    except Exception as e:
        return {
            "answer": f"System Error: {str(e)}",
            "sources": [],
            "is_refusal": True
        }

# 5. Initialize Chat History Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# 6. Sidebar
with st.sidebar:
    st.markdown("### 🏢 Zyro Dynamics Pvt. Ltd.")
    st.markdown("**Zyro HR Help Desk**")
    st.caption("AI-Powered RAG Policy Assistant")
    
    if st.button("➕ New Conversation", use_container_width=True, type="primary"):
        st.session_state.messages = []
        st.rerun()

    # Dynamic API Key Setting
    with st.expander("🔑 API Key Configuration", expanded=False):
        custom_key = st.text_input(
            "Groq API Key",
            type="password",
            value=os.environ.get("GROQ_API_KEY", ""),
            help="Enter your Groq API key to generate LLM responses in real-time."
        )
        if custom_key:
            os.environ["GROQ_API_KEY"] = custom_key
            try:
                from app.rag.generator import generator
                generator.api_key = custom_key
                from groq import Groq
                generator.client = Groq(api_key=custom_key)
                st.success("Groq API key activated!")
            except Exception as e:
                st.warning(f"Could not reinitialize Groq client: {e}")

    st.markdown("---")
    st.markdown("#### 📋 11 Official HR Policies")
    policies = [
        ("00_Company_Profile.pdf", "ZDL-CORP-001"),
        ("01_Employee_Handbook.pdf", "ADL-HR-001"),
        ("02_Leave_Policy.pdf", "ZDL-HR-002"),
        ("03_Work_From_Home_Policy.pdf", "ZDL-HR-003"),
        ("04_Code_of_Conduct.pdf", "ZDL-HR-004"),
        ("05_Performance_Review_Policy.pdf", "ZDL-HR-005"),
        ("06_Compensation_and_Benefits_Policy.pdf", "ZDL-HR-006"),
        ("07_IT_and_Data_Security_Policy.pdf", "ZDL-HR-007"),
        ("08_Prevention_of_Sexual_Harassment_Policy.pdf", "ZDL-HR-008"),
        ("09_Onboarding_and_Separation_Policy.pdf", "ZDL-HR-008"),
        ("10_Travel_and_Expense_Policy.pdf", "ZDL-HR-010"),
    ]
    for p, code in policies:
        clean = p.replace(".pdf", "").replace("_", " ")
        st.markdown(f"- 📄 **{clean}** (`{code}`)")

    st.markdown("---")
    st.markdown("#### ⚙️ RAG Engine Details")
    st.markdown("✅ **Index:** 91 Document Chunks")
    st.markdown("🧠 **Embeddings:** all-MiniLM-L6-v2 (384-d)")
    st.markdown("🔍 **Retriever:** MMR (k=4, fetch_k=12, λ=0.5)")
    st.markdown("🛡️ **Guardrails:** Groundedness + Scope Filter")

# 7. Main Header
st.markdown("<div class='main-title'>Zyro HR Assistant <span class='badge-rag'>Kaggle RAG Pipeline</span></div>", unsafe_allow_html=True)
st.markdown(
    "<div class='sub-title'>Ask any question about Zyro Dynamics HR policies, leave accruals, salary cycles, and benefits. "
    "Every response is strictly grounded in official policy PDF documents with verified page citations.</div>",
    unsafe_allow_html=True
)

# 8. Navigation Tabs
tab_chat, tab_docs, tab_eval = st.tabs(["💬 HR Chatbot", "📑 Policy Catalog", "🏆 Competition & submission.csv"])

# ==========================================
# TAB 1: Chatbot Interface
# ==========================================
with tab_chat:
    # Suggested Questions when chat is empty
    if len(st.session_state.messages) == 0:
        st.markdown("##### 💡 Suggested HR Questions")
        col1, col2 = st.columns(2)
        
        suggested = [
            ("How does Earned Leave accrue every month?", "Leave Policy"),
            ("When is monthly salary credited?", "Payroll & Compensation"),
            ("What is the annual wellness allowance?", "Benefits & Wellness"),
            ("How many counselling sessions are available?", "EAP Programme"),
            ("Can employees take leave during notice period?", "Leave & Separation"),
            ("How many years of service are required for gratuity?", "Gratuity Benefit")
        ]
        
        for i, (q, cat) in enumerate(suggested):
            target_col = col1 if i % 2 == 0 else col2
            if target_col.button(f"👉 **{q}**\n\n*{cat}*", key=f"sug_{i}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": q})
                with st.spinner("Retrieving official HR policy documents..."):
                    response_data = query_hr_assistant(q)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_data["answer"],
                    "sources": response_data.get("sources", []),
                    "is_refusal": response_data.get("is_refusal", False)
                })
                st.rerun()

    # Display Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg.get("is_refusal") and msg["role"] == "assistant":
                st.markdown(f"<div class='refusal-alert'>⚠️ <strong>Out of Scope / Refusal:</strong> {msg['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(msg["content"])

            # Source Citations
            sources = msg.get("sources", [])
            if sources:
                with st.expander(f"📚 Verified HR Citations ({len(sources)})", expanded=False):
                    for s in sources:
                        clean_file = s["file"].replace(".pdf", "").replace("_", " ")
                        st.markdown(
                            f"<div class='citation-card'>"
                            f"<span class='citation-page'>Page {s['page']}</span>"
                            f"<strong>{clean_file}</strong>"
                            f"<br><small style='color: #475569;'><em>\"{s.get('snippet', '')}\"</em></small>"
                            f"</div>",
                            unsafe_allow_html=True
                        )

    # Input Box
    user_prompt = st.chat_input("Ask a question about Zyro HR policies...")
    if user_prompt:
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        with st.chat_message("assistant"):
            with st.spinner("Searching FAISS index and generating grounded response..."):
                response_data = query_hr_assistant(user_prompt)

            content = response_data["answer"]
            sources = response_data.get("sources", [])
            is_refusal = response_data.get("is_refusal", False)

            if is_refusal:
                st.markdown(f"<div class='refusal-alert'>⚠️ <strong>Out of Scope / Refusal:</strong> {content}</div>", unsafe_allow_html=True)
            else:
                st.markdown(content)

            if sources:
                with st.expander(f"📚 Verified HR Citations ({len(sources)})", expanded=False):
                    for s in sources:
                        clean_file = s["file"].replace(".pdf", "").replace("_", " ")
                        st.markdown(
                            f"<div class='citation-card'>"
                            f"<span class='citation-page'>Page {s['page']}</span>"
                            f"<strong>{clean_file}</strong>"
                            f"<br><small style='color: #475569;'><em>\"{s.get('snippet', '')}\"</em></small>"
                            f"</div>",
                            unsafe_allow_html=True
                        )

            st.session_state.messages.append({
                "role": "assistant",
                "content": content,
                "sources": sources,
                "is_refusal": is_refusal
            })

# ==========================================
# TAB 2: HR Policy Catalog
# ==========================================
with tab_docs:
    st.markdown("#### 📚 Zyro Dynamics Official HR Policy Documents")
    st.markdown("These 11 official PDF policies have been parsed, chunked, and indexed into the 384-dimensional FAISS vectorstore.")
    
    docs_data = [
        {"Code": "ZDL-CORP-001", "Document": "00 Company Profile", "Scope": "Company history, 500+ workforce, organizational structure"},
        {"Code": "ADL-HR-001", "Document": "01 Employee Handbook", "Scope": "Employment categories, 6-month probation, working hours"},
        {"Code": "ZDL-HR-002", "Document": "02 Leave Policy", "Scope": "Earned Leave, Casual Leave, Sick Leave, notice period leave rules"},
        {"Code": "ZDL-HR-003", "Document": "03 Work From Home Policy", "Scope": "Remote eligibility, IT equipment, WFH schedules"},
        {"Code": "ZDL-HR-004", "Document": "04 Code of Conduct", "Scope": "Workplace ethics, integrity, conflict of interest, gift policies"},
        {"Code": "ZDL-HR-005", "Document": "05 Performance Review Policy", "Scope": "Appraisals, performance rating scale, promotion criteria"},
        {"Code": "ZDL-HR-006", "Document": "06 Compensation and Benefits", "Scope": "Salary credit schedule, Rs 12k wellness allowance, 6 EAP sessions, gratuity"},
        {"Code": "ZDL-HR-007", "Document": "07 IT and Data Security", "Scope": "Password complexity, asset security, internet usage guidelines"},
        {"Code": "ZDL-HR-008", "Document": "08 POSH Policy", "Scope": "Prevention of sexual harassment, ICC inquiry timelines"},
        {"Code": "ZDL-HR-008", "Document": "09 Onboarding and Separation", "Scope": "Notice period, resignation process, exit formalities"},
        {"Code": "ZDL-HR-010", "Document": "10 Travel and Expense", "Scope": "Business travel guidelines, per diem, reimbursement limits"},
    ]
    st.dataframe(pd.DataFrame(docs_data), use_container_width=True)

# ==========================================
# TAB 3: Competition Benchmark & submission.csv Generator
# ==========================================
with tab_eval:
    st.markdown("#### 🏆 Competition Benchmark & Submission Generator")
    st.markdown(
        "Generate a competition-compliant `submission.csv` containing predicted answers, "
        "verified source documents, and page numbers."
    )

    benchmark_questions = [
        "How does Earned Leave accrue every month?",
        "When is monthly salary credited?",
        "What is the annual wellness allowance?",
        "How many counselling sessions are available?",
        "Can employees take leave during notice period?",
        "How many years of service are required for gratuity?",
        "What is the probation period for full-time employees?",
        "What is the capital of France?",
        "Who is the CEO of Google?",
        "What is the company office WiFi password?",
        "What is an employee's favorite food?",
        "Write a python script to parse a CSV file"
    ]

    col_btn1, col_btn2 = st.columns([1, 3])
    with col_btn1:
        run_batch = st.button("🚀 Run Benchmark & Generate submission.csv", type="primary")

    if run_batch:
        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for idx, q in enumerate(benchmark_questions, 1):
            status_text.text(f"Processing question {idx}/{len(benchmark_questions)}: \"{q}\"")
            t_start = time.time()
            resp = query_hr_assistant(q)
            latency = time.time() - t_start
            
            first_source = resp["sources"][0] if resp.get("sources") else {}
            results.append({
                "id": idx,
                "question": q,
                "predicted_answer": resp.get("answer", ""),
                "source_file": first_source.get("file", "None"),
                "source_page": first_source.get("page", "None"),
                "is_refusal": resp.get("is_refusal", False),
                "latency_sec": round(latency, 3)
            })
            progress_bar.progress(idx / len(benchmark_questions))

        status_text.success("Benchmark completed! Results preview below:")
        df_results = pd.DataFrame(results)
        st.dataframe(df_results[["id", "question", "source_file", "source_page", "is_refusal", "latency_sec"]], use_container_width=True)

        # Download submission.csv
        csv_buffer = io.StringIO()
        df_results.to_csv(csv_buffer, index=False)
        st.download_button(
            label="📥 Download submission.csv",
            data=csv_buffer.getvalue(),
            file_name="submission.csv",
            mime="text/csv"
        )
