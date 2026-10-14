# FluentUp AI — API Reference

Base URL: `http://localhost:8000/api/v1`  
All protected routes require an `Authorization: Bearer <JWT>` header.

---

## 1. Authentication & Profile
- `POST /auth/register` — Register a new learner account with email, password, and display name.
- `POST /auth/login` — Login with credentials and receive access token.
- `POST /auth/demo` — One-click instant guest access for trial and evaluation.
- `GET /auth/me` — Retrieve current authenticated user profile.
- `GET /profile` — Retrieve learner profile, streak count, minutes practiced.
- `PATCH /profile` — Update display name, bio, or avatar.
- `GET /profile/preferences` — Get CEFR level, target goal, explanation language, practice target.
- `PATCH /profile/preferences` — Update learning preferences.

## 2. Conversation Partner & Voice
- `POST /conversations` — Start new AI speaking session with `mode` (instant, natural, fluency, interview, roleplay, free) and `topic`.
- `GET /conversations` — List conversation history.
- `GET /conversations/{id}` — Retrieve session detail and message transcript.
- `POST /conversations/{id}/messages` — Send user message (text or audio transcription). Returns tutor response and auto-detected grammar errors.
- `POST /conversations/{id}/finish` — Conclude session and generate pedagogical summary.

## 3. Practice & Tests Engine
- `POST /tests/generate` — Generate adaptive mini-test (5, 10, 20 questions or revision mode).
- `POST /tests/{id}/submit` — Submit answers to trusted backend scoring. Returns percentage, explanations, and level recommendation.
- `GET /tests/history` — List past test attempts and scores.
- `GET /tests/{id}/results` — Detailed question-by-question review of test attempt.

## 4. Mistake Notebook
- `GET /mistakes` — List captured errors with category, search, and mastery filters.
- `GET /mistakes/{id}` — Get mistake record details.
- `PATCH /mistakes/{id}` — Update mastery status (`learning`, `understood`, `mastered`).
- `POST /mistakes/{id}/practice` — Test repetition against corrected form.
- `DELETE /mistakes/{id}` — Dismiss mistake from notebook.

## 5. Vocabulary Trainer (SRS)
- `GET /vocabulary` — Search and filter saved words by mastery and due date.
- `POST /vocabulary` — Add new word with part of speech, Hindi translation, and example sentence.
- `POST /vocabulary/review` — Submit SuperMemo SM-2 rating (1 to 5) to update spaced repetition intervals.
- `DELETE /vocabulary/{id}` — Remove word from notebook.

## 6. Adaptive Learning & Analytics
- `GET /learning-plan` — Retrieve personalized daily plan.
- `POST /learning-plan/generate` — Force re-calculation of daily plan based on recent weaknesses.
- `GET /reports/weekly` — Real weekly calculated metrics (daily minutes, test counts, average accuracy, skill breakdown).
- `GET /progress` — Overview of radar competencies and CEFR level.
- `POST /learning/hinglish` — Translate Hindi/Hinglish phrase into natural English with explanation.

## 7. Speech & Pronunciation
- `POST /speech/pronunciation` — Acoustic and rhythm comprehensibility analysis.
- `GET /speech/status` — STT & TTS provider readiness.
- `GET /health` — Application health check.
- `GET /ready` — Database connection readiness.
- `GET /api/v1/status` — Active AI provider status.
