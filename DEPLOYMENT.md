# Deploy PrescribeMe

Get a **defined URL** by hosting the frontend on **Vercel** and the API on **Render** (free tiers available).

---

## 1. Deploy frontend to Vercel

1. **Push your repo to GitHub** (if not already).

2. **Go to [vercel.com](https://vercel.com)** and sign in with GitHub.

3. **Import** your PrescribeMe repository.

4. **Configure the project:**
   - **Root Directory:** Click "Edit" and set to **`frontend`** (so Vercel builds the Next.js app).
   - **Framework Preset:** Next.js (auto-detected).
   - **Build Command:** `npm run build` (default).
   - **Output Directory:** leave default.

5. **Environment variables** (Settings → Environment Variables):
   - **`NEXT_PUBLIC_API_URL`** = your **backend URL** (you’ll get this after deploying the API in step 2).  
     Example: `https://prescribeme-api.onrender.com`  
   - Add it for **Production**, and optionally **Preview** if you use preview deployments.

6. **Deploy.**  
   Your app will be at a URL like:  
   **`https://prescribeme-xxxx.vercel.app`**  
   You can add a custom domain in Vercel (e.g. `prescribeme.yourdomain.com`).

---

## 2. Deploy backend (API) to Render

The Next.js app calls a **FastAPI** backend. Host it on Render so you have a stable API URL.

1. **Go to [render.com](https://render.com)** and sign in with GitHub.

2. **New → Web Service.**

3. **Connect** your PrescribeMe repository.

4. **Settings:**
   - **Name:** e.g. `prescribeme-api`
   - **Region:** choose one (e.g. Oregon).
   - **Root Directory:** leave **empty** (repo root has `api/`, `src/`, `requirements.txt`).
   - **Runtime:** Python 3.
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn api.main:app --host 0.0.0.0 --port $PORT`

5. **Environment variables** (Environment tab):
   - **`OPENAI_API_KEY`** = your OpenAI API key (required).
   - **`CORS_ORIGINS`** = your Vercel frontend URL, e.g.  
     `https://prescribeme-xxxx.vercel.app`  
     (So the browser can call the API from your Vercel app. Add multiple URLs comma-separated if needed.)
   - **Chroma (choose one):**
     - **Option A — Chroma Cloud** (recommended for production):
       - **`CHROMA_API_KEY`** = your Chroma Cloud API key
       - **`CHROMA_TENANT`** = your tenant UUID (e.g. from chroma.cloud dashboard)
       - **`CHROMA_DATABASE`** = database name (e.g. `drugs-database`)
     - **Option B — Local Chroma** (ephemeral, data lost on restart):
       - Leave `CHROMA_TENANT` unset (uses local PersistentClient; data wiped on Render restarts)

6. **Create Web Service.**  
   Render will build and deploy. Your API URL will be like:  
   **`https://prescribeme-api.onrender.com`**

7. **Wire frontend to backend:**  
   In **Vercel** → your project → Settings → Environment Variables, set:  
   **`NEXT_PUBLIC_API_URL`** = `https://prescribeme-api.onrender.com`  
   (use your actual Render URL).  
   Then trigger a **redeploy** so the frontend uses the new value.

---

## 3. Optional: Render Blueprint

If you prefer a single config file, you can use the **Blueprint** in this repo:

- **File:** `render.yaml` at the repo root.
- In Render: **New → Blueprint**, connect the repo, and use the blueprint.  
  You still need to set **OPENAI_API_KEY** and **CORS_ORIGINS** in the Render dashboard for the new service.

---

## Summary

| What        | Where   | URL example                          |
|------------|---------|---------------------------------------|
| Frontend   | Vercel  | `https://prescribeme-xxxx.vercel.app` |
| Backend API| Render  | `https://prescribeme-api.onrender.com`|

- **Vercel env:** `NEXT_PUBLIC_API_URL` = Render API URL.  
- **Render env:** `OPENAI_API_KEY` = your key; `CORS_ORIGINS` = your Vercel URL.

After deployment, open your Vercel URL, click **Initialize knowledge base** once, then use **Analyze prescription** as usual.

**Note:** On Render’s free tier, the API may sleep after inactivity; the first request after sleep can be slow.

**Chroma persistence:** If using **local Chroma** (no `CHROMA_HOST`), data is stored in `./chroma_db` but **wiped on Render restarts**. Re-run “Initialize knowledge base” after each restart. For production, use **Chroma Cloud** (`CHROMA_HOST` + `CHROMA_API_KEY`) for persistent storage.
