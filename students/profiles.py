from dataclasses import dataclass
from typing import List


@dataclass
class StudentProfile:
    name: str
    topic: str
    target_understanding: str
    misconception: str
    persona: str
    progress_keywords: List[str]
    correct_answer: str
    difficulty: str = "medium"
