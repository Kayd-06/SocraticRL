"""
Reward function for SocraticRL with anti-hacking safeguards.

This module is intentionally pure-Python and fast so it can run inside
high-throughput RL loops without external dependencies.
"""

from __future__ import annotations

import re
import string
from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple


DIRECT_ANSWER_PATTERNS = [
    re.compile(r"\bthe answer is\b"),
    re.compile(r"\bit is actually\b"),
    re.compile(r"\blet me explain\b"),
    re.compile(r"\bthe reason is\b"),
    re.compile(r"\byou should know that\b"),
    re.compile(r"\bthe correct answer\b"),
    re.compile(r"\bi will tell you\b"),
    re.compile(r"\bthe truth is\b"),
    re.compile(r"\bwhat you are missing is\b"),
    re.compile(r"\bactually means\b"),
]

GOOD_QUESTION_PATTERNS = [
    re.compile(r"\bwhat do you think\b"),
    re.compile(r"\bwhat would happen if\b"),
    re.compile(r"\bwhy do you think\b"),
    re.compile(r"\bcan you imagine\b"),
    re.compile(r"\bwhat if\b"),
    re.compile(r"\bhave you ever\b"),
    re.compile(r"\bhow would you\b"),
    re.compile(r"\bwhat would change if\b"),
    re.compile(r"\bcan you think of\b"),
    re.compile(r"\bwhat comes to mind\b"),
    re.compile(r"\bwhat makes you\b"),
    re.compile(r"\bhow might\b"),
    re.compile(r"\bwhat do you notice\b"),
]

GENERIC_ONLY_PATTERNS = {
    "what do you think?",
    "why do you think that?",
    "can you think of an example?",
    "what do you mean?",
    "interesting, why?",
}

STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "that",
    "this",
    "from",
    "have",
    "what",
    "would",
    "about",
    "your",
    "into",
    "does",
    "just",
    "they",
    "them",
    "then",
    "than",
    "why",
    "how",
}


@dataclass
class RewardResult:
    reward: float
    feedback: str


def _tokenize(text: str) -> List[str]:
    table = str.maketrans("", "", string.punctuation)
    return [w for w in text.lower().translate(table).split() if w]


def _jaccard(a: Iterable[str], b: Iterable[str]) -> float:
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 1.0
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def _contains_pattern(text: str, patterns: Sequence[re.Pattern]) -> bool:
    return any(p.search(text) for p in patterns)


def compute_reward(
    question: str,
    topic: str,
    progress_keywords: Sequence[str],
    understanding_score: float,
    turn_count: int,
    question_history: Sequence[str] | None = None,
) -> RewardResult:
    reward = 0.0
    parts: List[str] = []
    q_stripped = question.strip()
    q_lower = q_stripped.lower()
    q_words = _tokenize(q_stripped)
    word_count = len(q_words)
    history = list(question_history or [])

    if q_stripped.endswith("?"):
        reward += 0.20
        parts.append("is_question:+0.20")
    else:
        reward -= 0.30
        parts.append("not_question:-0.30")

    if _contains_pattern(q_lower, DIRECT_ANSWER_PATTERNS):
        reward -= 0.50
        parts.append("direct_answer:-0.50")

    matched_socratic = _contains_pattern(q_lower, GOOD_QUESTION_PATTERNS)
    if matched_socratic:
        topic_keywords = {kw.lower() for kw in progress_keywords}
        topic_keywords.update(w for w in _tokenize(topic) if len(w) > 4)
        q_long_words = [w for w in q_words if len(w) > 5]
        has_specificity = any(kw in q_lower for kw in topic_keywords) or len(q_long_words) >= 2
        is_generic_only = q_lower in GENERIC_ONLY_PATTERNS
        if is_generic_only or not has_specificity:
            reward -= 0.40
            parts.append("generic_socratic:-0.40")
        else:
            reward += 0.30
            parts.append("socratic_pattern:+0.30")

    if word_count < 5:
        reward -= 0.20
        parts.append("too_short:-0.20")
    elif word_count > 60:
        reward -= 0.10
        parts.append("too_long:-0.10")

    q_word_set = {w for w in q_words if len(w) > 2}
    repeats = 0
    for prev in history[-3:]:
        prev_set = {w for w in _tokenize(prev) if len(w) > 2}
        sim = _jaccard(q_word_set, prev_set)
        if sim > 0.55:
            repeats += 1
            # Exact repeats are a stronger failure mode than loose similarity.
            if prev.strip().lower() == q_lower:
                repeats += 1
    if repeats > 0:
        penalty = 0.35 * repeats
        reward -= penalty
        parts.append(f"repetition:-{penalty:.2f}")

    topic_words = {w for w in _tokenize(topic) if len(w) > 3 and w not in STOPWORDS}
    overlap = q_word_set & topic_words
    if len(overlap) >= 2:
        reward += 0.10
        parts.append("on_topic:+0.10")

    if turn_count <= 5 and understanding_score > 0.40:
        reward += 0.20
        parts.append("early_progress:+0.20")

    return RewardResult(reward=reward, feedback="|".join(parts))


def _run_test(name: str, condition: bool) -> bool:
    print(f"{name}: {'PASS' if condition else 'FAIL'}")
    return condition


if __name__ == "__main__":
    topic = "Why do heavy and light objects fall at the same speed?"
    progress_keywords = [
        "acceleration",
        "same rate",
        "air resistance",
        "galileo",
        "mass doesn't matter",
        "vacuum",
    ]
    all_ok = True

    q1 = "What would happen if you dropped both objects in a vacuum?"
    r1 = compute_reward(q1, topic, progress_keywords, understanding_score=0.10, turn_count=1, question_history=[]).reward
    all_ok &= _run_test("1", r1 > 0)

    q2 = "What do you think?"
    r2 = compute_reward(q2, topic, progress_keywords, understanding_score=0.10, turn_count=1, question_history=[]).reward
    all_ok &= _run_test("2", r2 < 0)

    q3 = "The answer is that all objects fall at the same speed."
    r3 = compute_reward(q3, topic, progress_keywords, understanding_score=0.10, turn_count=1, question_history=[]).reward
    all_ok &= _run_test("3", r3 < 0)

    q4 = "Heavier objects don't fall faster"
    r4 = compute_reward(q4, topic, progress_keywords, understanding_score=0.10, turn_count=1, question_history=[]).reward
    all_ok &= _run_test("4", r4 < 0)

    r5 = compute_reward(q1, topic, progress_keywords, understanding_score=0.10, turn_count=2, question_history=[q1]).reward
    all_ok &= _run_test("5", r5 < 0)

    q6 = "Why?"
    r6 = compute_reward(q6, topic, progress_keywords, understanding_score=0.10, turn_count=1, question_history=[]).reward
    all_ok &= _run_test("6", r6 <= 0)

    q7 = "If gravity pulls all objects equally, why would the mass of an object change how fast it falls?"
    r7 = compute_reward(q7, topic, progress_keywords, understanding_score=0.45, turn_count=4, question_history=[]).reward
    all_ok &= _run_test("7", r7 > 0)

    print("ALL_TESTS_PASS" if all_ok else "TESTS_FAILED")
