# FluentUp AI — Architecture & System Design Document

**Product Name:** FluentUp AI  
**Tagline:** Speak Better. Think in English. Grow Every Day.  
**Version:** 1.0.0 (Production-Ready Spec & Architecture)  
**Author:** Senior Full-Stack & AI Engineering Team  

---

## 1. System Overview

FluentUp AI is an intelligent, full-stack, adaptive English-learning web platform engineered to transform language acquisition from passive memorization to an active, personalized feedback loop:

$$\text{SPEAK} \longrightarrow \text{ANALYZE} \longrightarrow \text{CORRECT} \longrightarrow \text{EXPLAIN} \longrightarrow \text{PRACTICE} \longrightarrow \text{RETEST} \longrightarrow \text{IMPROVE}$$

The platform bridges real-time voice and conversational AI with structured pedagogical engines (CEFR-aligned adaptive scoring, Leitner spaced-repetition vocabulary, automated grammar categorization, and weakness-focused mini-tests).

---

## 2. High-Level Architecture Diagram

```
+---------------------------------------------------------------------------------------+
|                                    CLIENT BROWSER                                     |
|  +---------------------------------------------------------------------------------+  |
|  | React 18+ / Vite / TypeScript (Strict) / Tailwind CSS / Lucide React / Recharts   |  |
|  | - Auth & Onboarding Flow (CEFR Baseline, Goals, Hindi/English Toggle)           |  |
|  | - Audio Capture & Speech-to-Text (MediaRecorder / Web Speech / Backend STT API) |  |
|  | - Audio Playback & Text-to-Speech (Web Speech Synthesis / Backend TTS API)     |  |
|  | - Practice & Tests Engine (5, 10, 20, Custom Count, Trusted Backend Scoring)     |  |
|  | - Vocabulary Notebook (Spaced Repetition System / Flashcards)                   |  |
|  | - Listening Practice (Audio passages, Comprehension questions, Transcripts)     |  |
|  | - Mistakes Notebook & Revision Queue                                            |  |
|  | - Real Analytics Dashboard (Time spent, Accuracy, Radar by Skill)               |  |
|  +---------------------------------------------------------------------------------+  |
+------------------------------------------+--------------------------------------------+
                                           | HTTPS / REST / WebSockets / JWT
                                           v
+---------------------------------------------------------------------------------------+
|                                    BACKEND ENGINE                                     |
|  FastAPI (Python 3.12+) / Pydantic v2 / SQLAlchemy ORM / Uvicorn                       |
|                                                                                       |
|  +--------------------+  +---------------------+  +--------------------------------+  |
|  | API Routing Layer  |  | Security & Auth     |  | Adaptive Learning Engine       |  |
|  | - /api/v1/profile  |  | - Supabase/JWT auth |  | - CEFR Estimation Smoother     |  |
|  | - /api/v1/converse |  | - User ownership    |  | - Error Pattern Frequency Rec. |  |
|  | - /api/v1/tests    |  | - Strict Rate limit |  | - Spaced Repetition Scheduler  |  |
|  | - /api/v1/mistakes |  | - Ownership RLS     |  | - Trusted Backend Scorer       |  |
|  | - /api/v1/vocab    |  +---------------------+  +--------------------------------+  |
|  | - /api/v1/speech   |                                                               |
|  +--------------------+                                                               |
|            |                                                                          |
|            +-------------------------+-------------------------+                      |
|                                      |                         |                      |
|                                      v                         v                      |
|  +----------------------------------------+  +-------------------------------------+  |
|  | AI Provider Abstraction                |  | Speech Provider Abstraction         |  |
|  | - Gemini / OpenAI / Anthropic Provider |  | - STT: Whisper / Web Speech API     |  |
|  | - Fallback Deterministic Local Bank    |  | - TTS: ElevenLabs / SpeechSynthesis |  |
|  | - Strict JSON Schema Correction Parser |  | - Pronunciation Acoustic Feedback   |  |
|  +----------------------------------------+  +-------------------------------------+  |
+------------------------------------------+--------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
|                                DATA PERSISTENCE LAYER                                 |
|  Supabase PostgreSQL / SQLite Local Dev                                               |
|  - profiles, learning_preferences, skill_progress                                     |
|  - conversations, conversation_messages, correction_records                           |
|  - grammar_questions, test_attempts, test_responses                                   |
|  - vocabulary_items, vocabulary_reviews, learning_plans                               |
+---------------------------------------------------------------------------------------+
```

---

## 3. Technology Stack & Decision Rationale

### Frontend
- **Framework:** React 18 + Vite (fast HMR, lightweight bundle size, standard ESM).
- **Language:** TypeScript with strict type checking enabled (`strict: true`, `noImplicitAny: true`).
- **Styling:** Tailwind CSS with custom design tokens (Deep Charcoal `#0f172a` / `#1e293b`, Electric Lime `#84cc16` / `#a3e635`, Warm Off-White `#f8fafc`).
- **Routing:** React Router v6.
- **Icons & UI:** Lucide React for consistent, lightweight iconography.
- **Data Visualization:** Recharts for responsive, accessible progress and radar charts.
- **Form Validation:** Zod schemas paired with React Hook Form.

### Backend
- **Framework:** FastAPI (asynchronous, high performance, automatic OpenAPI documentation).
- **Validation & Serialization:** Pydantic v2 schemas for all request/response models.
- **ORM & Migrations:** SQLAlchemy 2.0 with Alembic. Database driver abstraction supports both local SQLite (instant dev/test) and Supabase PostgreSQL.
- **Authentication:** JWT verification compatible with Supabase Auth tokens; user data isolated per `user_id`.

### AI & Speech Service Architecture
- **Provider Pattern:** Decoupled `LLMProvider` interface with concrete implementations:
  - `GeminiProvider` (Google Gemini 1.5/2.0 / `google-genai`)
  - `OpenAIProvider` (OpenAI GPT-4o / GPT-4o-mini)
  - `DeterministicLocalProvider` (High-quality built-in curriculum, grammar rules, and question bank for offline/unconfigured environments).
- **Speech Pipeline:**
  - Client-side Web Speech API + audio recorder streaming to backend Whisper-compatible endpoint.
  - Text-to-speech fallback with speech synthesis pitch/rate control for learners.
  - Pronunciation analysis differentiating transcription confidence vs phonemic/word-stress accuracy.

---

## 4. Database Schema Design

### Key Tables & Relationships
1. **profiles**: `id` (UUID PK), `email`, `display_name`, `avatar_url`, `created_at`, `updated_at`.
2. **learning_preferences**: `id`, `user_id` (FK), `current_level` (CEFR A1-C2), `goal`, `explanation_language` ('en' | 'hi'), `daily_time_target_mins`, `correction_style`.
3. **skill_progress**: `id`, `user_id` (FK), `skill_name` ('grammar', 'vocabulary', 'speaking', 'listening', 'pronunciation'), `estimated_level`, `accuracy_score`, `attempts_count`, `last_practiced_at`.
4. **conversations**: `id` (UUID), `user_id` (FK), `mode` ('instant', 'natural', 'fluency', 'interview', 'roleplay', 'free'), `topic`, `status`, `started_at`, `ended_at`, `summary`.
5. **conversation_messages**: `id`, `conversation_id` (FK), `sender` ('user' | 'assistant'), `content`, `audio_url`, `created_at`.
6. **correction_records** (Mistake Memory): `id`, `user_id` (FK), `conversation_id` (FK nullable), `original_sentence`, `corrected_sentence`, `category` (tense, agreement, preposition, etc.), `explanation`, `natural_alternative`, `occurrence_count`, `mastery_status` ('new' | 'learning' | 'mastered'), `last_tested_at`.
7. **grammar_questions**: `id`, `topic`, `cefr_level`, `question_type`, `prompt`, `options` (JSON), `correct_answer`, `explanation`.
8. **test_attempts**: `id`, `user_id` (FK), `topic`, `test_type`, `total_questions`, `score`, `percentage`, `started_at`, `completed_at`.
9. **test_responses**: `id`, `attempt_id` (FK), `question_id` (FK), `user_answer`, `is_correct`, `time_spent_seconds`.
10. **vocabulary_items**: `id`, `user_id` (FK), `word`, `meaning`, `part_of_speech`, `example_sentence`, `source`, `cefr_level`, `mastery_status`.
11. **vocabulary_reviews** (SRS): `id`, `item_id` (FK), `interval_days`, `repetition_count`, `ease_factor`, `next_review_date`, `last_reviewed_at`.
12. **learning_plans**: `id`, `user_id` (FK), `plan_date`, `time_target_mins`, `activities` (JSONB), `completed`.

---

## 5. Security & Isolation Strategy

1. **No Client-Supplied Identity Trust:** All routes require a valid JWT header (`Authorization: Bearer <token>`). The server derives `user_id` directly from the token payload.
2. **Row Level Security (RLS) & Query Scoping:** Every SQL query explicitly scopes by `user_id == current_user.id`.
3. **Secret Isolation:** API keys (Gemini, OpenAI, Supabase Service Role) reside strictly in server environment variables and are never bundled into frontend distributions.
4. **Input Sanitization & Length Limits:** Requests pass through strict Pydantic models with maximum character lengths to guard against buffer overruns and prompt injection attacks.
5. **Rate Limiting:** Costly LLM calls are throttled per user to prevent denial-of-wallet and quota exhaustion.

---

## 6. Execution Milestones & Acceptance Criteria

- [x] **Milestone 1:** Architecture specification & Monorepo scaffolding.
- [ ] **Milestone 2:** Backend database schema, models, Alembic migrations, and REST APIs.
- [ ] **Milestone 3:** AI Provider abstraction, deterministic question bank, and correction engines.
- [ ] **Milestone 4:** Frontend design system, responsive shell, routing, and theme engine.
- [ ] **Milestone 5:** Conversation workspace with live speech capture, correction modes, and audio playback.
- [ ] **Milestone 6:** Unlimited Practice & Tests engine with trusted backend scoring.
- [ ] **Milestone 7:** Mistake notebook, Leitner SRS vocabulary trainer, and Listening module.
- [ ] **Milestone 8:** Real analytics, weekly reports, and adaptive learning recommendations.
- [ ] **Milestone 9:** Automated test suite (Pytest + TypeScript/Vitest), production build verification, and deployment guides.
