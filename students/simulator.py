"""
Pure-Python deterministic student simulator.

Replaces LLM API calls during RL training. Each call takes < 1ms.
Behavior is governed by the student's current understanding_score bracket:
  0.00-0.30  confused, defensive, repeats misconception
  0.30-0.60  wavering, starting to question their belief
  0.60-0.90  breakthrough, echoing keywords from question
  0.90-1.00  articulates the correct answer
"""

import random

from students.profiles import StudentProfile

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    _SKLEARN_AVAILABLE = True
except ImportError:
    _SKLEARN_AVAILABLE = False

_CONFUSED = [
    "I still think {misconception_short}. That's just how it seems to me.",
    "I'm not sure I follow. Isn't it obvious that {misconception_short}?",
    "But that doesn't make sense - {misconception_short}, right?",
    "Hmm, I don't know. I've always believed {misconception_short}.",
]

_WAVERING = [
    "Okay, maybe I'm not completely sure. You're making me question {topic_word}.",
    "Wait... so you're saying {misconception_short} might not always hold?",
    "I hadn't thought about it that way. What about {topic_word}?",
    "I'm confused now. I get that {topic_word} matters, but I'm not sure why.",
]

_BREAKTHROUGH = [
    "Oh! So it's about {keyword}. That actually makes sense.",
    "I think I see it now - {keyword} is the key part I was missing.",
    "Wait, if {keyword} is true then my original idea was wrong!",
    "That's a good point about {keyword}. So the real answer involves that?",
]

_CORRECT = [
    "{correct_answer}",
    "I get it now - {correct_answer}",
    "So the actual answer is: {correct_answer}",
]


def simulate_student_response(
    question: str,
    scenario: StudentProfile,
    understanding_score: float,
    rng: random.Random,
) -> str:
    q_lower = question.lower()
    mentioned_keywords = [kw for kw in scenario.progress_keywords if kw.lower() in q_lower]
    keyword = mentioned_keywords[0] if mentioned_keywords else scenario.progress_keywords[0]
    misc_words = scenario.misconception.split()
    misconception_short = " ".join(misc_words[:8]) + ("..." if len(misc_words) > 8 else "")
    topic_word = max(
        (w for w in scenario.topic.split() if len(w) > 4),
        key=len,
        default=scenario.topic.split()[0],
    )
    fmt = dict(
        misconception_short=misconception_short,
        topic_word=topic_word,
        keyword=keyword,
        correct_answer=scenario.correct_answer,
    )

    if understanding_score < 0.30:
        template = rng.choice(_CONFUSED)
    elif understanding_score < 0.60:
        template = rng.choice(_WAVERING)
    elif understanding_score < 0.90:
        template = rng.choice(_BREAKTHROUGH)
    else:
        template = rng.choice(_CORRECT)

    return template.format(**fmt)


def _tfidf_score(student_response: str, correct_answer: str) -> float:
    """
    TF-IDF cosine similarity between student response and correct answer.
    Returns 0.0 if sklearn not installed — graceful fallback.

    Catches paraphrases that keyword matching misses. Example:
      Student says: "the acceleration is identical regardless of weight"
      Keyword score: 0/6 (no exact keywords)
      TF-IDF score:  0.71 (semantically correct)
    """
    if not _SKLEARN_AVAILABLE or not student_response.strip():
        return 0.0
    try:
        vec = TfidfVectorizer(stop_words="english", min_df=1)
        matrix = vec.fit_transform(
            [student_response.lower(), correct_answer.lower()]
        )
        sim = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
        return float(min(sim, 1.0))
    except Exception:
        return 0.0


def evaluate_understanding(
    student_response: str,
    scenario: StudentProfile,
    current_score: float,
    question: str,
) -> float:
    """
    Blended understanding score.

    With sklearn:    55% keyword + 30% TF-IDF cosine + 15% question nudge
    Without sklearn: 70% keyword + 30% question nudge (capped at 0.85)

    Score never decreases — students do not un-learn.
    """
    resp_lower = student_response.lower()
    q_lower = question.lower()

    kw_in_resp = sum(
        1 for kw in scenario.progress_keywords if kw.lower() in resp_lower
    )
    kw_score = kw_in_resp / max(len(scenario.progress_keywords), 1)

    tfidf = _tfidf_score(student_response, scenario.correct_answer)

    kw_in_q = sum(
        1 for kw in scenario.progress_keywords if kw.lower() in q_lower
    )
    nudge = min(kw_in_q * 0.04, 0.12)

    if _SKLEARN_AVAILABLE:
        raw = 0.55 * kw_score + 0.30 * tfidf + 0.15 * nudge
    else:
        raw = 0.70 * kw_score + 0.30 * nudge
        raw = min(raw, 0.85)

    return max(raw, current_score)
