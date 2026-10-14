# FluentUp AI

> **Speak Better. Think in English. Grow Every Day.**

FluentUp AI is a production-ready, full-stack, adaptive English learning platform designed to help learners speak English naturally and confidently. It combines interactive AI conversations, real-time voice input and speech synthesis, structured grammar error detection, personal mistake memory, Leitner spaced-repetition vocabulary, and unlimited adaptive mini-tests with trusted backend scoring.

---

## Key Features

1. **AI Conversation Partner (Live Voice & Audio):**
   - 6 Conversational Modes: Instant Correction, Natural Conversation, Fluency Focus, Placement & Job Interview (STAR method), Practical Roleplay (Cafe, Workplace, Travel), and Free Conversation.
   - Live microphone speech input (Web Speech API) with animated audio waves.
   - Spoken AI responses with replay controls and slow playback (0.75x) for non-native learners.
   - Real-time grammar extraction displaying corrected sentences, explanations, and natural alternatives.

2. **Hinglish-to-English Learning Helper:**
   - Dedicated translation drawer for learners who think in Hindi/Hinglish before speaking (e.g. *"Mujhe kal college jana hai"* $\rightarrow$ *"I have to go to college tomorrow"*).

3. **Unlimited Grammar & Mini-Test Engine:**
   - **No artificial daily test limits.**
   - 5-question quick sprint, 10-question standard, 20-question challenge, custom count, and revision tests directly from recorded mistakes.
   - Topics: Verb Tenses, Articles, Prepositions, Subject-Verb Agreement, Vocabulary & Idioms, Mixed Topics.
   - **Trusted Backend Scoring:** Scores and explanations are computed server-side to guarantee integrity.

4. **Personal Mistake Notebook:**
   - Automatically stores all detected grammatical errors.
   - Interactive Practice modal allowing learners to retry target sentences and upgrade mastery from *Learning* $\rightarrow$ *Understood* $\rightarrow$ *Mastered*.
   - Filter by error category, mastery level, or search keywords.

5. **Spaced-Repetition Vocabulary Trainer:**
   - Flashcard review powered by the SuperMemo SM-2 spaced repetition algorithm.
   - Rate words from 1 (Forgot) to 5 (Perfect recall) to dynamically schedule optimal review dates.
   - Includes English definitions, parts of speech, Hindi meanings, and example sentences.

6. **Listening Comprehension Module:**
   - Real-world audio passages spanning CEFR levels A2 to B2 across placements, daily life, and workplace settings.
   - Adjustable playback speeds (0.8x, 1.0x, 1.2x) and revealable transcripts with comprehension questions.

7. **Adaptive Learning Engine & Real Analytics:**
   - Dynamically generated daily curriculum based on user time commitment (10m, 15m, 20m, 30m) and historical weaknesses.
   - Exponential moving average smoothing for CEFR level estimation.
   - Recharts weekly practice minutes bar chart, 5-pillar skill competency radar chart, and error breakdown.

8. **AI Architecture & Zero-Config Offline Fallback:**
   - Pluggable LLM provider abstraction supporting **Google Gemini** (`gemini-2.0-flash`) and **OpenAI** (`gpt-4o-mini`).
   - If API keys are not supplied, the platform automatically activates its **Deterministic Local Pedagogical Engine**, guaranteeing 100% of all features, grammar checks, tests, and conversations work out of the box.

---

## Technology Stack

- **Frontend:** React 19, TypeScript (Strict), Vite, Tailwind CSS, React Router v6, Lucide React, Recharts.
- **Backend:** Python 3.12+, FastAPI, SQLAlchemy ORM, Pydantic v2, Pytest, Uvicorn.
- **AI SDKs:** `google-genai`, `openai`.
- **Database:** SQLite (local dev & tests) / Supabase PostgreSQL with Row Level Security (production).
- **Authentication:** JWT with salted password hashing and Supabase Auth token compatibility.

---

## Quick Start

### 1. Backend Startup (Port 8000)
```powershell
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
- API Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Health Check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

### 2. Frontend Startup (Port 5173)
```powershell
cd frontend
npm install
npm run dev
```
- Web Application: [http://localhost:5173](http://localhost:5173)

### Instant One-Click Demo Access
On the login screen, click **Instant Demo Access (1-Click)** to immediately explore all features with pre-configured mock learner data.

---

## Automated Verification & Tests

### Backend Unit & Integration Tests:
```powershell
cd backend
python -m pytest tests/ -v
```
*Result: 7 passed in 0.7s (100% pass rate).*

### Frontend Production Build:
```powershell
cd frontend
npm run build
```
*Result: `tsc -b && vite build` completed with 0 errors.*

---

## Project Structure

```
fluentup-ai/
  frontend/
    src/
      components/      # Sidebar, Topbar, MobileNav, AppShell
      features/        # Onboarding flow
      hooks/           # useAuth, useTheme, useSpeech
      pages/           # Dashboard, Tutor, Tests, Vocab, Listening, Mistakes, Analytics, Settings, Auth
      services/        # Typed API client
      styles/          # Design tokens & animations
      types/           # TypeScript definitions
    package.json
    vite.config.ts

  backend/
    app/
      api/routes/      # auth, profile, conversations, mistakes, tests, vocabulary, learning, speech, health
      core/            # config, security, database, logging
      models/          # SQLAlchemy ORM models
      schemas/         # Pydantic v2 schemas
      services/        # AI providers, Speech, Scorer, Question bank, Adaptive engine, Orchestrator
    tests/             # Automated Pytest suite
    requirements.txt
    .env.example

  supabase/
    migrations/        # 20261014_initial_schema.sql (PostgreSQL + RLS)
    seed.sql           # Curated seed question curriculum

  docs/
    ARCHITECTURE.md    # System design & architecture
    SETUP.md           # Local setup instructions
    API_REFERENCE.md   # Complete REST endpoint specifications
    TESTING.md         # Automated test reports
    DEPLOYMENT.md      # Vercel, Supabase, Render deployment guide
    AI_BEHAVIOR.md     # Tutor instructional policies & guardrails
  README.md
  .gitignore
```

---

## License
MIT License. Built for English learners worldwide.
