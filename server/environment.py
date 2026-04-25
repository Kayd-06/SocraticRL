import json
import os
import random
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from openenv_core import Environment
except ImportError:
    class Environment:
        pass

from models import SocraticAction, SocraticObservation, SocraticState
from reward import compute_reward
from students.scenarios import TRAINING_SCENARIOS
from students.simulator import evaluate_understanding, simulate_student_response


class SocraticEnvironment(Environment):
    def __init__(self, seed=None):
        self._rng = random.Random(seed)
        self._scenario = None
        self._history = []
        self._understanding = 0.0
        self._turn = 0
        self.MAX_TURNS = 15
        self._state = SocraticState()

    def reset(self) -> SocraticObservation:
        self._scenario = self._rng.choice(TRAINING_SCENARIOS)
        self._history = []
        self._understanding = 0.0
        self._turn = 0
        self._state = SocraticState(
            episode_id=str(uuid.uuid4()),
            topic=self._scenario.topic,
            student_profile=self._scenario.name,
            misconception=self._scenario.misconception,
            turn_count=0,
            understanding_score=0.0,
            conversation_history=[],
            max_turns=self.MAX_TURNS,
        )
        # Snorkel-aligned curriculum state hint for adaptive schedulers.
        self._state.difficulty_level = getattr(self._scenario, "difficulty", "medium")
        opening = (
            f"I'm stuck on this: {self._scenario.misconception} "
            "Can you help me think it through?"
        )
        return SocraticObservation(
            student_response=opening,
            understanding_score=self._understanding,
            turn_count=self._turn,
            done=False,
            reward=0.0,
            topic=self._scenario.topic,
            feedback="episode_start",
        )

    def step(self, action: SocraticAction) -> SocraticObservation:
        self._turn += 1
        question = (action.question or "").strip()

        reward_result = compute_reward(
            question=question,
            topic=self._scenario.topic,
            progress_keywords=self._scenario.progress_keywords,
            understanding_score=self._understanding,
            turn_count=self._turn,
            question_history=[h["question"] for h in self._history],
        )
        reward = reward_result.reward
        feedback_parts = [reward_result.feedback] if reward_result.feedback else []

        student_response = simulate_student_response(
            question=question,
            scenario=self._scenario,
            understanding_score=self._understanding,
            rng=self._rng,
        )
        new_understanding = self._blend_understanding_scores(
            student_response=student_response,
            question=question,
            current_score=self._understanding,
        )
        delta = max(new_understanding - self._understanding, 0.0)
        if delta > 0:
            progress_bonus = delta * 2.0
            reward += progress_bonus
            feedback_parts.append(f"understanding_delta:+{progress_bonus:.3f}")
        self._understanding = min(new_understanding, 1.0)

        self._history.append(
            {
                "turn": self._turn,
                "question": question,
                "student_response": student_response,
                "understanding_score": self._understanding,
            }
        )

        done = self._understanding >= 0.90 or self._turn >= self.MAX_TURNS
        if done:
            if self._understanding >= 0.90:
                efficiency_bonus = max((self.MAX_TURNS - self._turn) / self.MAX_TURNS, 0.0)
                terminal_bonus = 1.0 + efficiency_bonus
                reward += terminal_bonus
                feedback_parts.append(f"terminal_success:+{terminal_bonus:.3f}")
            elif self._understanding < 0.50:
                reward -= 0.50
                feedback_parts.append("terminal_low_understanding:-0.50")

        self._state.turn_count = self._turn
        self._state.understanding_score = self._understanding
        self._state.conversation_history = list(self._history)

        return SocraticObservation(
            student_response=student_response,
            understanding_score=self._understanding,
            turn_count=self._turn,
            done=done,
            reward=reward,
            topic=self._scenario.topic,
            feedback="|".join(feedback_parts),
        )

    def _score_understanding_keyword(
        self,
        student_response: str,
        question: str,
        current_score: float,
    ) -> float:
        """Existing keyword scorer from simulator logic."""
        return evaluate_understanding(
            student_response=student_response,
            scenario=self._scenario,
            current_score=current_score,
            question=question,
        )

    def _score_understanding_semantic(self, student_response: str) -> float:
        """
        Lightweight semantic scorer via TF-IDF cosine similarity.
        Falls back to 0.0 when sklearn is unavailable.
        """
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
        except ImportError:
            if not getattr(self, "_warned_no_sklearn", False):
                print(
                    "[warning] sklearn not installed; falling back to keyword-only understanding score."
                )
                self._warned_no_sklearn = True
            return 0.0

        docs = [student_response or "", self._scenario.correct_answer or ""]
        matrix = TfidfVectorizer().fit_transform(docs)
        similarity = float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0])
        return max(0.0, min(similarity, 1.0))

    def _blend_understanding_scores(
        self,
        student_response: str,
        question: str,
        current_score: float,
    ) -> float:
        keyword_score = self._score_understanding_keyword(
            student_response=student_response,
            question=question,
            current_score=current_score,
        )
        tfidf_score = self._score_understanding_semantic(student_response)
        if tfidf_score == 0.0 and not getattr(self, "_warned_no_sklearn", False):
            # If semantic channel is truly 0, still preserve keyword signal.
            blended = keyword_score
        else:
            blended = 0.60 * keyword_score + 0.40 * tfidf_score
        return max(current_score, min(blended, 1.0))

    def get_state(self) -> SocraticState:
        return self._state

    @property
    def state(self) -> SocraticState:
        """Compatibility property for openenv_core abstract interface."""
        return self._state

    def run_episode(self, questions: list) -> dict:
        """Scripted episode for smoke-testing. Returns episode summary dict."""
        obs = self.reset()
        trajectory = [
            {
                "turn": 0,
                "question": None,
                "student_response": obs.student_response,
                "reward": obs.reward,
                "understanding_score": obs.understanding_score,
                "done": obs.done,
                "feedback": obs.feedback,
            }
        ]

        for q in questions:
            obs = self.step(SocraticAction(question=q))
            trajectory.append(
                {
                    "turn": obs.turn_count,
                    "question": q,
                    "student_response": obs.student_response,
                    "reward": obs.reward,
                    "understanding_score": obs.understanding_score,
                    "done": obs.done,
                    "feedback": obs.feedback,
                }
            )
            if obs.done:
                break

        return {
            "episode_id": self._state.episode_id,
            "topic": self._state.topic,
            "student_profile": self._state.student_profile,
            "final_understanding": self._understanding,
            "turns_used": self._turn,
            "success": self._understanding >= 0.90,
            "trajectory": trajectory,
        }


if __name__ == "__main__":
    scripted_questions = [
        "What do you think causes this effect?",
        "What would happen in a vacuum?",
        "How might acceleration relate to mass here?",
        "Can you think of what Galileo tested?",
        "What would change if air resistance were removed?",
        "How would you explain this in your own words?",
        "What is the key idea you discovered?",
    ]
    env = SocraticEnvironment(seed=7)
    result = env.run_episode(scripted_questions)
    print(json.dumps(result, indent=2))
