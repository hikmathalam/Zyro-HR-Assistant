# Zyro HR Assistant — Deployment Guide

This document provides complete, production-ready deployment instructions for:
- **FastAPI Backend:** Deployed to [Render](https://render.com/)
- **Next.js Frontend:** Deployed to [Vercel](https://vercel.com/)
- **Streamlit Alternative Interface:** Deployed to [Streamlit Community Cloud](https://streamlit.io/cloud)

---

## 🔒 Security Notice
- Never commit actual API keys (`GROQ_API_KEY`) or production admin secrets to GitHub.
- All secrets must be configured via environment variables in the respective hosting provider dashboards.

---

## 1. Prerequisites & Git Setup

1. Initialize git in your local project root if not already done:
   ```bash
   cd c:\Users\DELL\Desktop\Zyro-HR-Assistant
   git init
   git add .
   git commit -m "feat: complete Zyro HR Assistant full-stack RAG application"
   ```

2. Push to your private or public GitHub repository:
   ```bash
   git remote add origin https://github.com/<your-username>/zyro-hr-assistant.git
   git branch -M main
   git push -u origin main
   ```

---

## 2. Deploy Backend to Render

### Option A: Using the Render Blueprint (`render.yaml`)
1. Log in to [Render](https://dashboard.render.com/).
2. Click **New +** $\rightarrow$ **Blueprint**.
3. Connect your GitHub repository.
4. Render will automatically detect `render.yaml` and configure the service.
5. In the configuration screen:
   - Provide your `GROQ_API_KEY` (secret).
6. Click **Apply**.

### Option B: Manual Web Service Setup
1. On the Render Dashboard, click **New +** $\rightarrow$ **Web Service**.
2. Connect your GitHub repository.
3. Configure settings:
   - **Name:** `zyro-hr-backend`
   - **Root Directory:** `backend`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Free
4. Add **Environment Variables** in the Render settings:
   | Key | Value | Notes |
   |---|---|---|
   | `PYTHON_VERSION` | `3.11.9` | Recommended Python version |
   | `GROQ_API_KEY` | `gsk_your_groq_api_key` | Secret from console.groq.com |
   | `GROQ_MODEL` | `llama-3.3-70b-versatile` | Production model |
   | `GROQ_FALLBACK_MODEL` | `llama-3.1-8b-instant` | Automatic fallback |
   | `CORS_ORIGINS` | `https://<your-vercel-domain>.vercel.app,http://localhost:3000` | Allowed origins |
   | `EMBEDDING_MODEL_NAME` | `sentence-transformers/all-MiniLM-L6-v2` | Embedding model |
   | `FAISS_INDEX_DIR` | `data/hr_faiss_index` | Pre-built FAISS index |
   | `ADMIN_API_KEY` | `<your-chosen-admin-secret>` | Protects `/admin/reindex` |
5. Click **Create Web Service**.
6. Note down the assigned public URL (e.g., `https://zyro-hr-backend.onrender.com`).

---

## 3. Deploy Frontend to Vercel

1. Log in to [Vercel](https://vercel.com/).
2. Click **Add New...** $\rightarrow$ **Project**.
3. Import your GitHub repository.
4. In the Project Configuration:
   - **Framework Preset:** `Next.js`
   - **Root Directory:** Click `Edit` and select `frontend`.
   - **Build Command:** `npm run build`
   - **Output Directory:** `.next`
5. Under **Environment Variables**, add:
   | Key | Value |
   |---|---|
   | `NEXT_PUBLIC_API_URL` | `https://zyro-hr-backend.onrender.com` (Your Render Backend URL) |
6. Click **Deploy**.
7. Once deployed, note your Vercel production domain (e.g., `https://zyro-hr-assistant.vercel.app`).
8. **Important:** Copy your Vercel URL and update the `CORS_ORIGINS` environment variable in your Render backend settings so the browser can make requests without CORS blocks.

---

## 4. Deploy Alternative Interface to Streamlit Community Cloud

1. Log in to [Streamlit Community Cloud](https://share.streamlit.io/).
2. Click **New app**.
3. Select your GitHub repository:
   - **Branch:** `main`
   - **Main file path:** `streamlit_app/app.py`
4. Expand **Advanced settings** $\rightarrow$ **Secrets**:
   ```toml
   GROQ_API_KEY = "gsk_your_groq_api_key_here"
   BACKEND_API_URL = "https://zyro-hr-backend.onrender.com"
   ```
5. Click **Deploy**.
6. The Streamlit app will build using `streamlit_app/requirements.txt` and launch. It operates in dual-mode: connecting to the Render backend over HTTP or executing the RAG pipeline directly in-process.

---

## 5. Post-Deployment Verification Checklist

After deploying, verify the live deployment:

1. **Backend Health Check:**
   Visit: `https://zyro-hr-backend.onrender.com/health`
   Expected response:
   ```json
   {
     "status": "healthy",
     "app_name": "Zyro HR Assistant API",
     "version": "1.0.0",
     "index_loaded": true,
     "total_indexed_chunks": 91,
     "groq_configured": true,
     "model": "llama-3.3-70b-versatile"
   }
   ```

2. **Frontend Test:**
   - Open your Vercel URL (`https://zyro-hr-assistant.vercel.app`).
   - Click one of the suggested HR questions (e.g., *"How does Earned Leave accrue every month?"*).
   - Verify that the answer renders with source citations (`02_Leave_Policy.pdf`, `Page 2`).
   - Test an out-of-scope question (e.g., *"What is the capital of France?"*) and verify polite refusal.

3. **Streamlit Test:**
   - Open your Streamlit Cloud URL.
   - Navigate to Tab 3 (**Competition & submission.csv**).
   - Click **Run Benchmark & Generate submission.csv** to verify batch execution.
   - Click **Download submission.csv**.

