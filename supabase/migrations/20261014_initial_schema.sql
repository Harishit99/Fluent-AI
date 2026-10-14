-- ========================================================
-- FluentUp AI — Supabase Database Migration & RLS Schema
-- ========================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. PROFILES TABLE
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE NOT NULL,
    display_name TEXT NOT NULL DEFAULT 'English Learner',
    avatar_url TEXT,
    bio TEXT,
    streak_count INTEGER DEFAULT 1,
    last_active_date DATE DEFAULT CURRENT_DATE,
    total_minutes_practiced INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. LEARNING PREFERENCES TABLE
CREATE TABLE IF NOT EXISTS public.learning_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE NOT NULL,
    current_level TEXT DEFAULT 'A2',
    target_goal TEXT DEFAULT 'Daily conversation & fluency',
    explanation_language TEXT DEFAULT 'en',
    daily_time_target_mins INTEGER DEFAULT 15,
    primary_difficulty TEXT DEFAULT 'Forming natural sentences quickly',
    correction_style TEXT DEFAULT 'instant',
    voice_speed TEXT DEFAULT 'normal',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. SKILL PROGRESS TABLE
CREATE TABLE IF NOT EXISTS public.skill_progress (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    skill_name TEXT NOT NULL,
    estimated_level TEXT DEFAULT 'A2',
    accuracy_percentage FLOAT DEFAULT 65.0,
    total_attempts INTEGER DEFAULT 0,
    confidence_score FLOAT DEFAULT 0.2,
    last_practiced_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. CONVERSATIONS TABLE
CREATE TABLE IF NOT EXISTS public.conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    mode TEXT NOT NULL DEFAULT 'free',
    topic TEXT NOT NULL DEFAULT 'Everyday Life',
    status TEXT DEFAULT 'active',
    started_at TIMESTAMPTZ DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    summary TEXT,
    feedback_notes TEXT
);

-- 5. CONVERSATION MESSAGES TABLE
CREATE TABLE IF NOT EXISTS public.conversation_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES public.conversations(id) ON DELETE CASCADE NOT NULL,
    sender TEXT NOT NULL,
    content TEXT NOT NULL,
    audio_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. CORRECTION RECORDS (MISTAKE MEMORY) TABLE
CREATE TABLE IF NOT EXISTS public.correction_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    conversation_id UUID REFERENCES public.conversations(id) ON DELETE SET NULL,
    original_sentence TEXT NOT NULL,
    corrected_sentence TEXT NOT NULL,
    category TEXT NOT NULL,
    explanation TEXT NOT NULL,
    natural_alternative TEXT,
    example_sentence TEXT,
    severity TEXT DEFAULT 'important',
    occurrence_count INTEGER DEFAULT 1,
    repetition_revisions INTEGER DEFAULT 0,
    mastery_status TEXT DEFAULT 'learning',
    practice_recommended BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_practiced_at TIMESTAMPTZ DEFAULT NOW()
);

-- 7. GRAMMAR QUESTIONS TABLE
CREATE TABLE IF NOT EXISTS public.grammar_questions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    topic TEXT NOT NULL,
    cefr_level TEXT DEFAULT 'A2',
    question_type TEXT DEFAULT 'multiple_choice',
    prompt TEXT NOT NULL,
    options_json JSONB DEFAULT '[]',
    correct_answer TEXT NOT NULL,
    explanation TEXT NOT NULL,
    is_seed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 8. TEST ATTEMPTS TABLE
CREATE TABLE IF NOT EXISTS public.test_attempts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    topic TEXT NOT NULL,
    cefr_level TEXT DEFAULT 'A2',
    test_mode TEXT DEFAULT 'standard',
    total_questions INTEGER NOT NULL,
    correct_count INTEGER DEFAULT 0,
    score_percentage FLOAT DEFAULT 0.0,
    time_taken_seconds INTEGER DEFAULT 0,
    completed BOOLEAN DEFAULT FALSE,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- 9. TEST RESPONSES TABLE
CREATE TABLE IF NOT EXISTS public.test_responses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    attempt_id UUID REFERENCES public.test_attempts(id) ON DELETE CASCADE NOT NULL,
    question_id UUID NOT NULL,
    question_prompt TEXT NOT NULL,
    user_answer TEXT NOT NULL,
    correct_answer TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL,
    explanation TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 10. VOCABULARY ITEMS TABLE
CREATE TABLE IF NOT EXISTS public.vocabulary_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    word TEXT NOT NULL,
    meaning TEXT NOT NULL,
    part_of_speech TEXT DEFAULT 'noun',
    example_sentence TEXT NOT NULL,
    hindi_translation TEXT,
    synonyms_json JSONB DEFAULT '[]',
    antonyms_json JSONB DEFAULT '[]',
    cefr_level TEXT DEFAULT 'B1',
    mastery_status TEXT DEFAULT 'learning',
    user_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 11. VOCABULARY REVIEWS (SRS) TABLE
CREATE TABLE IF NOT EXISTS public.vocabulary_reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    item_id UUID REFERENCES public.vocabulary_items(id) ON DELETE CASCADE UNIQUE NOT NULL,
    repetition_count INTEGER DEFAULT 0,
    interval_days INTEGER DEFAULT 1,
    ease_factor FLOAT DEFAULT 2.5,
    last_reviewed_at TIMESTAMPTZ DEFAULT NOW(),
    next_review_date TIMESTAMPTZ DEFAULT NOW()
);

-- 12. LEARNING PLANS TABLE
CREATE TABLE IF NOT EXISTS public.learning_plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    plan_date DATE NOT NULL DEFAULT CURRENT_DATE,
    target_minutes INTEGER DEFAULT 20,
    completed_minutes INTEGER DEFAULT 0,
    activities_json JSONB NOT NULL DEFAULT '[]',
    is_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ========================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ========================================================

ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.learning_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.skill_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.conversation_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.correction_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.test_attempts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.test_responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.vocabulary_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.vocabulary_reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.learning_plans ENABLE ROW LEVEL SECURITY;

-- Profiles: user owns their own profile
CREATE POLICY "Users can view their own profile"
    ON public.profiles FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can update their own profile"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = user_id);

-- Conversations & Messages
CREATE POLICY "Users can manage their own conversations"
    ON public.conversations FOR ALL
    USING (auth.uid() = user_id);

CREATE POLICY "Users can access messages for their conversations"
    ON public.conversation_messages FOR ALL
    USING (EXISTS (
        SELECT 1 FROM public.conversations
        WHERE conversations.id = conversation_messages.conversation_id
        AND conversations.user_id = auth.uid()
    ));

-- Correction Records
CREATE POLICY "Users can view and manage their own mistakes"
    ON public.correction_records FOR ALL
    USING (auth.uid() = user_id);

-- Test Attempts & Responses
CREATE POLICY "Users can view and manage their own test attempts"
    ON public.test_attempts FOR ALL
    USING (auth.uid() = user_id);

CREATE POLICY "Users can view responses for their attempts"
    ON public.test_responses FOR ALL
    USING (EXISTS (
        SELECT 1 FROM public.test_attempts
        WHERE test_attempts.id = test_responses.attempt_id
        AND test_attempts.user_id = auth.uid()
    ));

-- Vocabulary
CREATE POLICY "Users can manage their own vocabulary items"
    ON public.vocabulary_items FOR ALL
    USING (auth.uid() = user_id);

CREATE POLICY "Users can manage their vocabulary SRS reviews"
    ON public.vocabulary_reviews FOR ALL
    USING (EXISTS (
        SELECT 1 FROM public.vocabulary_items
        WHERE vocabulary_items.id = vocabulary_reviews.item_id
        AND vocabulary_items.user_id = auth.uid()
    ));

-- Learning plans
CREATE POLICY "Users can access their own learning plans"
    ON public.learning_plans FOR ALL
    USING (auth.uid() = user_id);
