import random
from typing import List, Dict, Any

# Curated, validated question bank spanning CEFR levels A1-C2 and essential topics
QUESTION_BANK: List[Dict[str, Any]] = [
    # TENSES (A1-B2)
    {
        "id": "tense-a1-1",
        "topic": "tenses",
        "cefr_level": "A1",
        "question_type": "multiple_choice",
        "prompt": "She ____ to the English academy every morning.",
        "options": ["walk", "walks", "walking", "walked"],
        "correct_answer": "walks",
        "explanation": "With third-person singular subjects ('She', 'He', 'It') in the simple present, add '-s' or '-es' to the verb base.",
    },
    {
        "id": "tense-a2-1",
        "topic": "tenses",
        "cefr_level": "A2",
        "question_type": "multiple_choice",
        "prompt": "Yesterday, we ____ our final group presentation.",
        "options": ["give", "gave", "given", "giving"],
        "correct_answer": "gave",
        "explanation": "Use the simple past tense ('gave') for actions completed at a specific time in the past ('yesterday').",
    },
    {
        "id": "tense-b1-1",
        "topic": "tenses",
        "cefr_level": "B1",
        "question_type": "multiple_choice",
        "prompt": "By the time the manager arrived, the team ____ the proposal.",
        "options": ["already finished", "had already finished", "have already finished", "was finishing"],
        "correct_answer": "had already finished",
        "explanation": "The past perfect tense ('had finished') expresses an action completed before another past event.",
    },
    {
        "id": "tense-b2-1",
        "topic": "tenses",
        "cefr_level": "B2",
        "question_type": "multiple_choice",
        "prompt": "Next month, she ____ at the multinational consulting firm for five years.",
        "options": ["will work", "will have been working", "has been working", "is working"],
        "correct_answer": "will have been working",
        "explanation": "Future perfect continuous ('will have been working') indicates an ongoing action that will continue up to a future point in time.",
    },

    # ARTICLES (A1-B2)
    {
        "id": "art-a1-1",
        "topic": "articles",
        "cefr_level": "A1",
        "question_type": "multiple_choice",
        "prompt": "I bought ____ apple and ____ sandwich for lunch.",
        "options": ["an / a", "a / an", "an / an", "a / a"],
        "correct_answer": "an / a",
        "explanation": "'Apple' begins with a vowel sound, so use 'an'. 'Sandwich' begins with a consonant sound, so use 'a'.",
    },
    {
        "id": "art-a2-1",
        "topic": "articles",
        "cefr_level": "A2",
        "question_type": "multiple_choice",
        "prompt": "Mount Everest is ____ highest mountain in the world.",
        "options": ["a", "an", "the", "no article"],
        "correct_answer": "the",
        "explanation": "Superlative adjectives (e.g., 'highest', 'best', 'most important') require the definite article 'the'.",
    },
    {
        "id": "art-b1-1",
        "topic": "articles",
        "cefr_level": "B1",
        "question_type": "multiple_choice",
        "prompt": "He plays ____ guitar very skillfully, but he doesn't like ____ sports.",
        "options": ["the / no article", "no article / the", "a / no article", "the / the"],
        "correct_answer": "the / no article",
        "explanation": "Musical instruments take 'the' when referring to playing them ('the guitar'), whereas sports in general take no article.",
    },

    # PREPOSITIONS (A1-C1)
    {
        "id": "prep-a1-1",
        "topic": "prepositions",
        "cefr_level": "A1",
        "question_type": "multiple_choice",
        "prompt": "Our English class begins ____ 9:00 AM ____ Monday.",
        "options": ["at / on", "on / at", "in / on", "at / in"],
        "correct_answer": "at / on",
        "explanation": "Use 'at' for precise clock times ('at 9:00 AM') and 'on' for days of the week ('on Monday').",
    },
    {
        "id": "prep-a2-1",
        "topic": "prepositions",
        "cefr_level": "A2",
        "question_type": "multiple_choice",
        "prompt": "She has been interested ____ learning conversational English for years.",
        "options": ["in", "on", "at", "with"],
        "correct_answer": "in",
        "explanation": "The adjective 'interested' is paired with the preposition 'in' ('interested in something').",
    },
    {
        "id": "prep-b1-1",
        "topic": "prepositions",
        "cefr_level": "B1",
        "question_type": "multiple_choice",
        "prompt": "The manager apologized ____ the team ____ the sudden schedule change.",
        "options": ["to / for", "for / to", "with / about", "at / for"],
        "correct_answer": "to / for",
        "explanation": "Standard collocations: apologize TO a person FOR a mistake or circumstance.",
    },
    {
        "id": "prep-b2-1",
        "topic": "prepositions",
        "cefr_level": "B2",
        "question_type": "multiple_choice",
        "prompt": "The new policy complies ____ all international safety standards.",
        "options": ["with", "to", "for", "by"],
        "correct_answer": "with",
        "explanation": "'Comply' strictly takes 'with' ('comply with rules/standards').",
    },

    # SUBJECT-VERB AGREEMENT (A2-B2)
    {
        "id": "sva-a2-1",
        "topic": "subject_verb_agreement",
        "cefr_level": "A2",
        "question_type": "multiple_choice",
        "prompt": "Neither the teacher nor the students ____ aware of the revised schedule.",
        "options": ["were", "was", "is", "be"],
        "correct_answer": "were",
        "explanation": "When subjects are joined by 'neither... nor', the verb agrees with the closer subject ('students' is plural -> 'were').",
    },
    {
        "id": "sva-b1-1",
        "topic": "subject_verb_agreement",
        "cefr_level": "B1",
        "question_type": "multiple_choice",
        "prompt": "Each of the candidates ____ given twenty minutes to present their case.",
        "options": ["is", "are", "have been", "were"],
        "correct_answer": "is",
        "explanation": "'Each of...' takes a singular verb ('is') because 'each' refers to every individual one separately.",
    },
    {
        "id": "sva-b2-1",
        "topic": "subject_verb_agreement",
        "cefr_level": "B2",
        "question_type": "multiple_choice",
        "prompt": "The number of fluent speakers in the department ____ steadily increasing.",
        "options": ["is", "are", "have been", "were"],
        "correct_answer": "is",
        "explanation": "'The number of...' takes a singular verb ('is'), whereas 'A number of...' takes a plural verb.",
    },

    # MODAL VERBS & CONDITIONALS (B1-C1)
    {
        "id": "mod-b1-1",
        "topic": "modal_verbs",
        "cefr_level": "B1",
        "question_type": "multiple_choice",
        "prompt": "You ____ speak so loudly in the quiet study room.",
        "options": ["shouldn't", "must", "don't have to", "might"],
        "correct_answer": "shouldn't",
        "explanation": "'Shouldn't' expresses strong advice against doing something.",
    },
    {
        "id": "cond-b1-1",
        "topic": "conditionals",
        "cefr_level": "B1",
        "question_type": "multiple_choice",
        "prompt": "If I ____ more free time, I would join the debate club.",
        "options": ["had", "have", "will have", "would have"],
        "correct_answer": "had",
        "explanation": "Second conditional (hypothetical present/future): 'If + past simple, would + base verb'.",
    },
    {
        "id": "cond-b2-1",
        "topic": "conditionals",
        "cefr_level": "B2",
        "question_type": "multiple_choice",
        "prompt": "If you had informed me earlier, I ____ the meeting time.",
        "options": ["would have rescheduled", "would reschedule", "will reschedule", "had rescheduled"],
        "correct_answer": "would have rescheduled",
        "explanation": "Third conditional (unreal past): 'If + past perfect, would have + past participle'.",
    },

    # VOCABULARY & IDIOMS (B1-C2)
    {
        "id": "voc-b1-1",
        "topic": "vocabulary",
        "cefr_level": "B1",
        "question_type": "multiple_choice",
        "prompt": "Choose the synonym for 'Candid':",
        "options": ["Frank and honest", "Secretive", "Complicated", "Aggressive"],
        "correct_answer": "Frank and honest",
        "explanation": "'Candid' means truthful, straightforward, and sincere in expression.",
    },
    {
        "id": "voc-b2-1",
        "topic": "vocabulary",
        "cefr_level": "B2",
        "question_type": "multiple_choice",
        "prompt": "What does the idiom 'Cut corners' mean in a professional context?",
        "options": [
            "Do something poorly or cheaply to save time/money",
            "Change directions suddenly in a project",
            "Work overtime on the weekend",
            "Negotiate a higher salary",
        ],
        "correct_answer": "Do something poorly or cheaply to save time/money",
        "explanation": "'To cut corners' means doing something in the quickest or cheapest way, often compromising quality.",
    },
    {
        "id": "voc-c1-1",
        "topic": "vocabulary",
        "cefr_level": "C1",
        "question_type": "multiple_choice",
        "prompt": "Which word describes someone who expresses themselves clearly and persuasively?",
        "options": ["Eloquent", "Ambiguous", "Reticent", "Verbose"],
        "correct_answer": "Eloquent",
        "explanation": "'Eloquent' means fluent or persuasive in speaking or writing.",
    },

    # PROFESSIONAL & INTERVIEW COMMUNICATION (B1-B2)
    {
        "id": "comm-b1-1",
        "topic": "professional_communication",
        "cefr_level": "B1",
        "question_type": "multiple_choice",
        "prompt": "Which opening is most polite and professional for an email to a senior interviewer?",
        "options": [
            "Dear Ms. Sharma, I hope this email finds you well.",
            "Hey Sharma, what's up with the interview?",
            "Hi there, tell me my result.",
            "Respected Madam/Sir, myself Rahul writing to you.",
        ],
        "correct_answer": "Dear Ms. Sharma, I hope this email finds you well.",
        "explanation": "Use a polite salutation ('Dear [Title] [Last Name]') followed by a professional opening inquiry.",
    },
    {
        "id": "comm-b2-1",
        "topic": "professional_communication",
        "cefr_level": "B2",
        "question_type": "multiple_choice",
        "prompt": "During a job interview, how should you structure your response using the STAR method?",
        "options": [
            "Situation, Task, Action, Result",
            "Story, Topic, Analysis, Review",
            "Summary, Theory, Application, Report",
            "Skill, Talent, Attitude, Reliability",
        ],
        "correct_answer": "Situation, Task, Action, Result",
        "explanation": "The STAR framework is the standard structure for behavioral interview responses.",
    },
]


def get_bank_questions(topic: str = "all", cefr_level: str = "A2", count: int = 5) -> List[Dict[str, Any]]:
    filtered = QUESTION_BANK

    if topic and topic.lower() != "all" and topic.lower() != "revision":
        topic_match = [q for q in QUESTION_BANK if q["topic"].lower() == topic.lower()]
        if topic_match:
            filtered = topic_match

    # Try level matching first, expand if fewer than count
    level_match = [q for q in filtered if q["cefr_level"].upper() == cefr_level.upper()]
    if len(level_match) >= count:
        sample = random.sample(level_match, count)
    else:
        # Fall back to whole filtered set
        if len(filtered) >= count:
            sample = random.sample(filtered, count)
        else:
            # Backfill from the full question bank so count is always fulfilled
            sample = list(filtered)
            remaining = [q for q in QUESTION_BANK if q not in sample]
            while len(sample) < count and remaining:
                sample.append(remaining.pop(0))
            # If still short, sample with replacement
            while len(sample) < count:
                sample.append(random.choice(QUESTION_BANK))

    # Shuffle options for fairness
    result = []
    for item in sample:
        copy_item = item.copy()
        opts = list(copy_item["options"])
        random.shuffle(opts)
        copy_item["options"] = opts
        result.append(copy_item)

    return result
