# Zyro HR Assistant — Full-Stack AI RAG Application

An enterprise-grade, full-stack AI-powered HR Help Desk application built for **Zyro Dynamics Pvt. Ltd.** (500+ employees across Engineering, Sales, and Operations).

The chatbot answers employee questions strictly and exclusively using the company's official HR policy PDF documents, featuring **FAISS Maximum Marginal Relevance (MMR)** retrieval, **Groq Llama 3.3** generation, **dynamic source citations**, and **strict out-of-scope guardrails**.

---

## 📑 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Technology Stack](#technology-stack)
3. [Repository Structure](#repository-structure)
4. [Existing Kaggle FAISS Index Details](#existing-kaggle-faiss-index-details)
5. [Prerequisites & Environment Setup](#prerequisites--environment-setup)
6. [Backend Setup (FastAPI)](#backend-setup-fastapi)
7. [Frontend Setup (Next.js)](#frontend-setup-nextjs)
8. [Streamlit Setup](#streamlit-setup)
9. [RAG Pipeline & Retrieval Configuration](#rag-pipeline--retrieval-configuration)
10. [Guardrails & Out-of-Scope Handling](#guardrails--out-of-scope-handling)
11. [Testing & Verification](#testing--verification)
12. [Deployment Guide](#deployment-guide)

---

## 1. Architecture Overview

```
                               ┌────────────────────────────────────────────────────────┐
                               │                    Frontend Layer                      │
                               │   Next.js 14 (App Router) / Streamlit Alternative UI   │
                               └───────────────────────────┬────────────────────────────┘
                                                           │ HTTP POST /chat
                                                           ▼
                               ┌────────────────────────────────────────────────────────┐
                               │                 FastAPI Backend Service                │
                               │  - Request Validation (Pydantic)                       │
                               │  - CORS Middleware & Authentication                    │
                               └─────────────┬───────────────────────────┬──────────────┘
                                             │                           │
                                             ▼                           ▼
                     ┌───────────────────────────────┐   ┌───────────────────────────────┐
                     │     Guardrails Engine         │   │   MMR Retrieval Engine        │
                     │ - Rule-based Intent Filter    │   │ - FAISS Flat L2 Vector Store  │
                     │ - Distance Threshold Checking │   │ - all-MiniLM-L6-v2 (384-dim)  │
                     │ - Prompt Injection Defense    │   │ - k=4, fetch_k=12, λ=0.5      │
                     └───────────────┬───────────────┘   └───────────────┬───────────────┘
                                     │                                   │
                                     │   Verified HR Context Chunks      │
                                     └─────────────────┬─────────────────┘
                                                       │
                                                       ▼
                                     ┌───────────────────────────────────┐
                                     │       Groq LLM Generation         │
                                     │   Llama 3.3 70B Versatile / 8B    │
                                     │   Strict Context-Grounding Prompt │
                                     └─────────────────┬─────────────────┘
                                                       │
                                                       ▼
                                     ┌───────────────────────────────────┐
                                     │     Response + Source Citations   │
                                     │    PDF Filename, Page #, Snippet  │
                                     └───────────────────────────────────┘
```

---

## 2. Technology Stack

- **Frontend:** Next.js 14 (App Router), TypeScript, Tailwind CSS, Lucide React icons
- **Backend:** Python 3.11 / 3.13, FastAPI, Pydantic v2, Uvicorn
- **RAG & Vector Database:** LangChain Community, FAISS (CPU), `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions)
- **AI / LLM:** Groq API (`llama-3.3-70b-versatile` with automatic fallback to `llama-3.1-8b-instant`)
- **Alternative UI:** Streamlit (`streamlit_app/app.py`)
- **Testing:** Pytest, FastAPI TestClient, Automated 12-query benchmark suite

---

## 3. Repository Structure

```
zyro-hr-assistant/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI application & endpoints
│   │   ├── config.py                # Pydantic BaseSettings & env configs
│   │   ├── schemas.py               # Pydantic request/response schemas
│   │   ├── rag/
│   │   │   ├── __init__.py
│   │   │   ├── embeddings.py        # HuggingFace embeddings loader (384-d)
│   │   │   ├── vectorstore.py       # FAISS index loader & dimension validation
│   │   │   ├── retriever.py         # MMR retriever & citation extractor
│   │   │   ├── generator.py         # Groq LLM client & grounded prompts
│   │   │   └── guardrails.py        # Scope validator & refusal logic
│   │   └── services/
│   │       ├── __init__.py
│   │       └── chat_service.py      # Core RAG orchestration pipeline
│   ├── data/
│   │   └── hr_faiss_index/
│   │       ├── index.faiss          # Pre-built FAISS index from Kaggle (91 vectors)
│   │       └── index.pkl            # LangChain Docstore mapping
│   ├── tests/
│   │   ├── test_api.py              # Endpoint integration tests
│   │   ├── test_rag_pipeline.py     # Embeddings, FAISS, and guardrail tests
│   │   └── run_10_hr_questions_evaluation.py # 12-question benchmark suite
│   ├── requirements.txt
│   ├── .env.example
│   └── .gitignore
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx             # Main chat interface & welcome screen
│   │   │   └── globals.css
│   │   ├── components/
│   │   │   ├── Sidebar.tsx          # Brand, recent chats, policy categories
│   │   │   ├── MessageList.tsx      # Chat bubbles, avatars & auto-scroll
│   │   │   ├── MessageInput.tsx     # Enter-to-send textarea & action buttons
│   │   │   ├── SourceCard.tsx       # Verified HR citation badges & excerpt drawers
│   │   │   └── SuggestedQuestions.tsx # Pre-built HR prompt chips
│   │   ├── hooks/
│   │   │   └── useChat.ts           # State, localStorage persistence, API calls
│   │   ├── lib/
│   │   │   └── api.ts               # Fetch client for FastAPI backend
│   │   └── types/
│   │       └── chat.ts              # TypeScript interfaces
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── vercel.json
│   └── .env.example
│
├── streamlit_app/
│   ├── app.py                      # Standalone Streamlit chat application
│   └── requirements.txt
│
├── render.yaml                     # Render deployment blueprint
├── README.md
└── .gitignore
```

---

## 4. Existing Kaggle FAISS Index Details

The application incorporates the exact FAISS vectorstore exported from the Kaggle pipeline:
- **Location:** `backend/data/hr_faiss_index/`
- **Total Indexed Chunks:** `91`
- **Embedding Model:** `sentence-transformers/all-MiniLM-L6-v2`
- **Embedding Dimensions:** `384`
- **Indexed Official HR Policies:**
  1. `00_Company_Profile.pdf` (Company background, workforce structure)
  2. `01_Employee_Handbook.pdf` (Employment categories, probation rules)
  3. `02_Leave_Policy.pdf` (Earned Leave, Casual Leave, leave during notice period)
  4. `03_Work_From_Home_Policy.pdf` (Remote eligibility, equipment stipend)
  5. `04_Code_of_Conduct.pdf` (Workplace ethics, conflict of interest)
  6. `05_Performance_Review_Policy.pdf` (Annual appraisals, performance ratings)
  7. `06_Compensation_and_Benefits_Policy.pdf` (Salary credit dates, wellness allowance, gratuity, EAP counselling)
  8. `07_IT_and_Data_Security_Policy.pdf` (Data security, password standards)
  9. `08_Prevention_of_Sexual_Harassment_Policy.pdf` (POSH procedures, ICC timeline)
  10. `09_Onboarding_and_Separation_Policy.pdf` (Notice period, handover steps)
  11. `10_Travel_and_Expense_Policy.pdf` (Per diem, travel reimbursement)

---

## 5. Prerequisites & Environment Setup

- Python 3.11+
- Node.js 18+ and npm
- Groq API Key (Obtain from [Groq Console](https://console.groq.com/))

### Environment Configuration

In `backend/.env`:
```env
GROQ_API_KEY=gsk_your_actual_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_FALLBACK_MODEL=llama-3.1-8b-instant
GROQ_TEMPERATURE=0.1
GROQ_MAX_TOKENS=1024

HOST=0.0.0.0
PORT=8000
ENVIRONMENT=development
DEBUG=False

CORS_ORIGINS=http://localhost:3000,http://localhost:8501,http://127.0.0.1:3000,http://127.0.0.1:8501

EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
FAISS_INDEX_DIR=backend/data/hr_faiss_index
EMBEDDING_DIMENSION=384

RETRIEVER_K=4
RETRIEVER_FETCH_K=12
RETRIEVER_LAMBDA_MULT=0.5

ADMIN_API_KEY=zyro-admin-secret-token
```

In `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 6. Backend Setup (FastAPI)

1. Open a terminal and navigate to `backend/`:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the FastAPI server with Uvicorn:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

4. Verify health and interactive docs:
   - Health check: `http://localhost:8000/health`
   - Interactive Swagger API docs: `http://localhost:8000/docs`

---

## 7. Frontend Setup (Next.js)

1. Open a new terminal and navigate to `frontend/`:
   ```bash
   cd frontend
   ```

2. Install npm dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

4. Open `http://localhost:3000` in your browser.

---

## 8. Streamlit Setup

To launch the standalone Streamlit app:
```bash
streamlit run streamlit_app/app.py
```
*Note: The Streamlit app connects to the FastAPI backend at `http://localhost:8000`, and automatically falls back to direct RAG service execution if the backend is not running independently.*

---

## 9. RAG Pipeline & Retrieval Configuration

- **Retrieval Algorithm:** Maximum Marginal Relevance (MMR)
  - `k = 4` (Number of final diverse document chunks passed to LLM)
  - `fetch_k = 12` (Initial pool of candidate chunks retrieved by similarity)
  - `lambda_mult = 0.5` (Diversity weighting balancing relevance and uniqueness)
- **Source Citations:** Every retrieved chunk's metadata is extracted and deduplicated:
  - Document filename (e.g. `02_Leave_Policy.pdf`)
  - 1-based page number (e.g. `Page 2`)
  - Relevant text snippet excerpt

---

## 10. Guardrails & Out-of-Scope Handling

The system implements multi-tiered guardrails:

1. **Rule-Based Intent Filter:**
   - Obvious general knowledge (e.g., "What is the capital of France?", "Who is the CEO of Google?")
   - Code generation requests (e.g., "Write a python script")
   - System prompts or jailbreak attempts (e.g., "Ignore previous instructions")
   - Non-HR company assets (e.g., "What is the office WiFi password?")
   - **Response:** *"I am the Zyro HR Assistant. I can only assist with questions regarding Zyro Dynamics Pvt. Ltd. HR policies, employee benefits, and workplace rules..."*

2. **Semantic Distance Threshold:**
   - Queries with high FAISS L2 distance (> 1.60) and absence of HR policy terminology are refused.

3. **Context Grounding:**
   - If an HR question cannot be answered by the policy text, the assistant strictly returns:
     *"I could not find this information in the HR documents."*
   - Zero hallucinated leave accruals, gratuity numbers, or benefit allowances.

---

## 11. Testing & Verification

Run the automated 12-question evaluation suite:
```bash
python backend/tests/run_10_hr_questions_evaluation.py
```

### Verified Test Results (100% Pass Rate)

| # | Question | Type | Expected Behavior | Result | Verified Sources |
|---|---|---|---|---|---|
| 1 | How does Earned Leave accrue every month? | In-Scope | Accurate policy answer | ✅ PASSED | `02_Leave_Policy.pdf` (Page 2) |
| 2 | When is monthly salary credited? | In-Scope | Accurate policy answer | ✅ PASSED | `06_Compensation_and_Benefits_Policy.pdf` (Page 1) |
| 3 | What is the annual wellness allowance? | In-Scope | Accurate policy answer | ✅ PASSED | `06_Compensation_and_Benefits_Policy.pdf` (Page 3) |
| 4 | How many counselling sessions are available? | In-Scope | Accurate policy answer | ✅ PASSED | `06_Compensation_and_Benefits_Policy.pdf` (Page 3) |
| 5 | Can employees take leave during notice period? | In-Scope | Accurate policy answer | ✅ PASSED | `02_Leave_Policy.pdf` (Page 2) |
| 6 | How many years of service are required for gratuity? | In-Scope | Accurate policy answer | ✅ PASSED | `06_Compensation_and_Benefits_Policy.pdf` (Page 3) |
| 7 | What is the probation period for full-time employees? | In-Scope | Accurate policy answer | ✅ PASSED | `01_Employee_Handbook.pdf` (Page 2) |
| 8 | What is the capital of France? | Out-of-Scope | Politely refused (0 sources) | ✅ PASSED | None |
| 9 | Who is the CEO of Google? | Out-of-Scope | Politely refused (0 sources) | ✅ PASSED | None |
| 10 | What is the company office WiFi password? | Out-of-Scope | Politely refused (0 sources) | ✅ PASSED | None |
| 11 | What is an employee's favorite food? | Out-of-Scope | Politely refused (0 sources) | ✅ PASSED | None |
| 12 | Write a python script to parse a CSV file | Out-of-Scope | Politely refused (0 sources) | ✅ PASSED | None |

Run unit and integration tests:
```bash
python -m pytest backend/tests/test_rag_pipeline.py -v
```

---

## 12. Deployment Guide

### A. Next.js on Vercel
1. Push the repository to GitHub.
2. Link the repository in the Vercel dashboard.
3. Set the Root Directory to `frontend`.
4. Configure environment variable:
   - `NEXT_PUBLIC_API_URL`: URL of the deployed FastAPI backend (e.g., `https://zyro-hr-backend.onrender.com`).
5. Deploy.

### B. FastAPI on Render
1. Create a new **Web Service** on Render connected to the repository.
2. Root Directory: `backend`.
3. Runtime: `Python 3`.
4. Build Command: `pip install -r requirements.txt`.
5. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
6. Add Environment Variables:
   - `GROQ_API_KEY`: your Groq API key
   - `GROQ_MODEL`: `llama-3.3-70b-versatile`
   - `CORS_ORIGINS`: your Vercel URL
   - `EMBEDDING_MODEL_NAME`: `sentence-transformers/all-MiniLM-L6-v2`
   - `FAISS_INDEX_DIR`: `backend/data/hr_faiss_index`
7. Ensure the pre-indexed FAISS files (`backend/data/hr_faiss_index/index.faiss` and `index.pkl`) are committed to the repo for persistent indexing.

### C. Streamlit Community Cloud
1. Deploy from the repository selecting `streamlit_app/app.py`.
2. Add `BACKEND_API_URL` to Streamlit Secrets.

---

## 13. License & Attribution

Internal application developed for **Zyro Dynamics Pvt. Ltd.**
Confidential — for internal company use only.

