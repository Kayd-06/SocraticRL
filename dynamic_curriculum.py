"""
dynamic_curriculum.py — Adaptive difficulty scheduler for SocraticRL.

Snorkel AI sub-theme: the training distribution changes as the agent improves.

Easy scenarios dominate early training. As success rate on easy scenarios
exceeds PROMOTION_THRESHOLD over a rolling window, medium scenarios unlock.
When medium exceeds threshold, hard scenarios unlock.

This models a subject matter expert who raises the bar as the student
demonstrates mastery — exactly "changing requirements/preferences."
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List
import random

from students.profiles import StudentProfile
from students.scenarios import TRAINING_SCENARIOS

try:
    from students.scenarios_extended import EXTENDED_SCENARIOS
    ALL_TRAINING = TRAINING_SCENARIOS + EXTENDED_SCENARIOS
except ImportError:
    ALL_TRAINING = TRAINING_SCENARIOS

PROMOTION_THRESHOLD = 0.65
WINDOW_SIZE = 20


@dataclass
class DifficultyTracker:
    difficulty: str
    results: List[bool] = field(default_factory=list)

    def record(self, success: bool) -> None:
        self.results.append(success)
        if len(self.results) > WINDOW_SIZE:
            self.results.pop(0)

    @property
    def success_rate(self) -> float:
        return sum(self.results) / len(self.results) if self.results else 0.0

    @property
    def n_episodes(self) -> int:
        return len(self.results)

    @property
    def is_ready_to_promote(self) -> bool:
        return self.n_episodes >= WINDOW_SIZE // 2 and self.success_rate >= PROMOTION_THRESHOLD


class CurriculumScheduler:
    """
    Manages scenario sampling with automatic difficulty promotion.

    Starts with easy only. Promotes to medium when easy success rate
    exceeds PROMOTION_THRESHOLD. Promotes to hard when medium does.
    The training distribution changes dynamically — changing requirements.
    """

    DIFFICULTY_ORDER = ["easy", "medium", "hard"]

    def __init__(self, scenarios: List[StudentProfile] = ALL_TRAINING, seed: int | None = None):
        self._rng = random.Random(seed)
        self._by_difficulty: Dict[str, List[StudentProfile]] = {}
        for s in scenarios:
            self._by_difficulty.setdefault(s.difficulty, []).append(s)
        self._trackers = {d: DifficultyTracker(difficulty=d) for d in self.DIFFICULTY_ORDER}
        self._unlocked: List[str] = ["easy"]

    def sample(self) -> StudentProfile:
        pool: List[StudentProfile] = []
        for d in self._unlocked:
            pool.extend(self._by_difficulty.get(d, []))
        if not pool:
            pool = list(self._by_difficulty.get("easy", []))
        return self._rng.choice(pool)

    def record_episode(self, difficulty: str, success: bool) -> None:
        if difficulty in self._trackers:
            self._trackers[difficulty].record(success)
        self._maybe_promote()

    def _maybe_promote(self) -> None:
        for i, d in enumerate(self.DIFFICULTY_ORDER[:-1]):
            next_d = self.DIFFICULTY_ORDER[i + 1]
            if (
                d in self._unlocked
                and next_d not in self._unlocked
                and self._trackers[d].is_ready_to_promote
                and self._by_difficulty.get(next_d)
            ):
                self._unlocked.append(next_d)
                print(
                    f"[curriculum] Unlocked '{next_d}' scenarios "
                    f"('{d}' success rate: {self._trackers[d].success_rate:.0%} "
                    f"over {self._trackers[d].n_episodes} episodes)"
                )

    def status(self) -> Dict:
        return {
            "unlocked": self._unlocked,
            "available_scenarios": sum(len(self._by_difficulty.get(d, [])) for d in self._unlocked),
            "trackers": {
                d: {
                    "success_rate": round(self._trackers[d].success_rate, 3),
                    "n_episodes": self._trackers[d].n_episodes,
                    "ready_to_promote": self._trackers[d].is_ready_to_promote,
                }
                for d in self.DIFFICULTY_ORDER
            },
        }


if __name__ == "__main__":
    import json
    scheduler = CurriculumScheduler(seed=0)
    print("Initial status:")
    print(json.dumps(scheduler.status(), indent=2))

    print("\nSimulating 25 easy successes...")
    for _ in range(25):
        s = scheduler.sample()
        scheduler.record_episode(s.difficulty, success=True)

    print("\nAfter 25 easy successes:")
    print(json.dumps(scheduler.status(), indent=2))

    print("\nSimulating 25 mixed episodes...")
    for i in range(25):
        s = scheduler.sample()
        scheduler.record_episode(s.difficulty, success=(i % 3 != 0))

    print("\nFinal status:")
    print(json.dumps(scheduler.status(), indent=2))
