"""
dynamic_curriculum.py - Adaptive curriculum for SocraticRL.

Snorkel AI sub-theme: "simulated environments with subject matter experts
with changing requirements/preferences."

As the agent improves, the curriculum automatically shifts toward harder
scenarios. This models the real-world dynamic where a subject matter expert
raises the bar as the student (agent) demonstrates mastery.

The scheduler tracks per-difficulty success rates over a rolling window.
When success rate on 'easy' scenarios exceeds the PROMOTION_THRESHOLD,
the scheduler stops sampling easy scenarios and adds 'medium' ones.
When 'medium' exceeds PROMOTION_THRESHOLD, 'hard' scenarios are unlocked.

This means the agent's training distribution CHANGES over time -
exactly what the Snorkel AI sub-theme is asking for.
"""

from dataclasses import dataclass, field
from typing import Dict, List
import random

from students.profiles import StudentProfile
from students.scenarios import TRAINING_SCENARIOS

PROMOTION_THRESHOLD = 0.65  # success rate needed to unlock next difficulty
WINDOW_SIZE = 20  # rolling window for success rate calculation


@dataclass
class DifficultyTracker:
    difficulty: str
    results: List[bool] = field(default_factory=list)  # True = success (understanding >= 0.9)

    def record(self, success: bool):
        self.results.append(success)
        if len(self.results) > WINDOW_SIZE:
            self.results.pop(0)

    @property
    def success_rate(self) -> float:
        if not self.results:
            return 0.0
        return sum(self.results) / len(self.results)

    @property
    def is_ready_to_promote(self) -> bool:
        return (
            len(self.results) >= WINDOW_SIZE // 2  # need enough data
            and self.success_rate >= PROMOTION_THRESHOLD
        )


class CurriculumScheduler:
    """
    Manages which scenarios are sampled during training.
    Starts with easy scenarios only.
    Promotes to medium when easy success rate >= PROMOTION_THRESHOLD.
    Promotes to hard when medium success rate >= PROMOTION_THRESHOLD.
    """

    DIFFICULTY_ORDER = ["easy", "medium", "hard"]

    def __init__(self, scenarios: List[StudentProfile] = TRAINING_SCENARIOS, seed: int | None = None):
        self._rng = random.Random(seed)
        self._all = scenarios
        self._by_difficulty: Dict[str, List[StudentProfile]] = {}
        for s in scenarios:
            self._by_difficulty.setdefault(s.difficulty, []).append(s)

        self._trackers: Dict[str, DifficultyTracker] = {
            d: DifficultyTracker(difficulty=d)
            for d in self.DIFFICULTY_ORDER
        }
        self._unlocked = ["easy"]  # start with easy only

    def sample(self) -> StudentProfile:
        """Sample a scenario from the currently unlocked difficulties."""
        pool = []
        for d in self._unlocked:
            pool.extend(self._by_difficulty.get(d, []))
        if not pool:
            pool = self._all  # fallback: use everything
        return self._rng.choice(pool)

    def record_episode(self, difficulty: str, success: bool):
        """
        Call after each training episode with the scenario difficulty and outcome.
        Automatically promotes difficulty level when threshold is met.
        """
        if difficulty in self._trackers:
            self._trackers[difficulty].record(success)
        self._maybe_promote()

    def _maybe_promote(self):
        for i, d in enumerate(self.DIFFICULTY_ORDER[:-1]):
            next_d = self.DIFFICULTY_ORDER[i + 1]
            if (
                d in self._unlocked
                and next_d not in self._unlocked
                and self._trackers[d].is_ready_to_promote
            ):
                self._unlocked.append(next_d)
                print(
                    f"[curriculum] Promoted to '{next_d}' "
                    f"('{d}' success rate: {self._trackers[d].success_rate:.0%})"
                )

    def status(self) -> Dict:
        return {
            "unlocked_difficulties": self._unlocked,
            "trackers": {
                d: {
                    "success_rate": round(t.success_rate, 3),
                    "n_episodes": len(t.results),
                    "ready_to_promote": t.is_ready_to_promote,
                }
                for d, t in self._trackers.items()
            },
        }


if __name__ == "__main__":
    import json

    scheduler = CurriculumScheduler(seed=42)
    print("Initial status:", json.dumps(scheduler.status(), indent=2))

    # Simulate 60 episodes: first 30 are easy successes, then mix
    for i in range(30):
        s = scheduler.sample()
        scheduler.record_episode(s.difficulty, success=True)

    print("\nAfter 30 easy successes:")
    print(json.dumps(scheduler.status(), indent=2))

    for i in range(30):
        s = scheduler.sample()
        scheduler.record_episode(s.difficulty, success=(i % 3 != 0))

    print("\nAfter 30 more mixed episodes:")
    print(json.dumps(scheduler.status(), indent=2))
