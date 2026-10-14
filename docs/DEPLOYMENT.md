# FluentUp AI — Deployment & Production Guide

## 1. Hosting Architecture Overview

FluentUp AI is architected for modern decoupled cloud deployment:

- **Frontend:** Suitable for Vercel, Netlify, or Cloudflare Pages.
- **Backend:** Suitable for Render, Railway, AWS ECS / App Runner, or Fly.io.
- **Database:** Supabase PostgreSQL with Row Level Security (RLS) enabled.

---

## 2. Frontend Deployment (Vercel)

1. Connect the GitHub repository to Vercel.
2. Set **Root Directory** to `frontend`.
3. Build Settings:
   - Framework Preset: `Vite`
   - Build Command: `npm run build`
   - Output Directory: `dist`
4. Set Environment Variables:
   - `VITE_API_BASE_URL`: `https://your-backend-api.onrender.com/api/v1`
5. Deploy.

---

## 3. Backend Deployment (Render / Railway / Fly.io)

1. Set **Root Directory** to `backend`.
2. Runtime: `Python 3.12+`
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Configure Environment Variables:
   - `APP_ENV`: `production`
   - `SECRET_KEY`: `<Generate a 32+ character random secret>`
   - `DATABASE_URL`: `postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres` (Supabase connection URI)
   - `CORS_ORIGINS`: `https://your-frontend-domain.vercel.app`
   - `LLM_PROVIDER`: `gemini` (or `openai`)
   - `GEMINI_API_KEY`: `<Your Gemini Key>`
   - `GEMINI_MODEL`: `gemini-2.0-flash`
   - `PORT`: `8000`

---

## 4. Supabase Database Migration

1. In your Supabase project dashboard, navigate to **SQL Editor**.
2. Run the script located in `supabase/migrations/20261014_initial_schema.sql`.
3. (Optional) Run `supabase/seed.sql` to populate baseline questions and test curriculum.
4. Verify Row Level Security (RLS) policies are active for user data isolation.
