-- ========================================================
-- FluentUp AI — Seed Questions and Learning Content
-- ========================================================

INSERT INTO public.grammar_questions (topic, cefr_level, question_type, prompt, options_json, correct_answer, explanation, is_seed)
VALUES
(
    'tenses',
    'A1',
    'multiple_choice',
    'She ____ to the English academy every morning.',
    '["walk", "walks", "walking", "walked"]'::jsonb,
    'walks',
    'With third-person singular subjects (She, He, It) in the simple present, add -s or -es to the verb base.',
    TRUE
),
(
    'tenses',
    'A2',
    'multiple_choice',
    'Yesterday, we ____ our final group presentation.',
    '["give", "gave", "given", "giving"]'::jsonb,
    'gave',
    'Use the simple past tense (gave) for actions completed at a specific time in the past.',
    TRUE
),
(
    'articles',
    'A1',
    'multiple_choice',
    'I bought ____ apple and ____ sandwich for lunch.',
    '["an / a", "a / an", "an / an", "a / a"]'::jsonb,
    'an / a',
    'Apple begins with a vowel sound (use an). Sandwich begins with a consonant sound (use a).',
    TRUE
),
(
    'prepositions',
    'B1',
    'multiple_choice',
    'The manager apologized ____ the team ____ the sudden schedule change.',
    '["to / for", "for / to", "with / about", "at / for"]'::jsonb,
    'to / for',
    'Standard collocations: apologize TO a person FOR an action or event.',
    TRUE
),
(
    'subject_verb_agreement',
    'B1',
    'multiple_choice',
    'Neither the teacher nor the students ____ aware of the revised schedule.',
    '["were", "was", "is", "be"]'::jsonb,
    'were',
    'When subjects are joined by neither... nor, the verb agrees with the closer subject (students -> were).',
    TRUE
),
(
    'vocabulary',
    'B2',
    'multiple_choice',
    'What does the idiom "Cut corners" mean in a professional context?',
    '["Do something poorly or cheaply to save time/money", "Change directions suddenly in a project", "Work overtime on the weekend", "Negotiate a higher salary"]'::jsonb,
    'Do something poorly or cheaply to save time/money',
    'To cut corners means executing a task in the quickest, cheapest way, often reducing quality.',
    TRUE
);
