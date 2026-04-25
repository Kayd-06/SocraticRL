"""
client.py — Remote HTTP client for the SocraticRL HuggingFace Space.

Use this when running training against the deployed remote environment
instead of in-process. Wraps raw dict responses into typed SocraticObservation.
"""

from __future__ import annotations
from typing import Any

from models import SocraticAction, SocraticObservation

try:
    from openenv_core.client import HTTPEnvClient
except ImportError:
    class HTTPEnvClient:
        def __init__(self, base_url: str):
            self.base_url = base_url
        def reset(self): raise NotImplementedError("openenv_core not installed")
        def step(self, action): raise NotImplementedError("openenv_core not installed")


class SocraticClient(HTTPEnvClient):
    """
    Typed HTTP client for the deployed SocraticRL environment.

    Usage:
        client = SocraticClient()
        obs = client.reset()
        obs = client.step(SocraticAction(question="Why do you think mass matters here?"))
        print(obs.understanding_score, obs.reward, obs.feedback)
    """

    DEFAULT_URL = "https://YOUR_USERNAME-socratic-rl.hf.space"

    def __init__(self, base_url: str = DEFAULT_URL):
        super().__init__(base_url=base_url)

    def reset(self) -> SocraticObservation:
        raw = super().reset()
        return self._parse(raw if isinstance(raw, dict) else vars(raw))

    def step(self, action: SocraticAction) -> SocraticObservation:
        raw = super().step(action)
        return self._parse(raw if isinstance(raw, dict) else vars(raw))

    @staticmethod
    def _parse(raw: dict[str, Any]) -> SocraticObservation:
        return SocraticObservation(
            student_response=raw.get("student_response", ""),
            understanding_score=float(raw.get("understanding_score", 0.0)),
            turn_count=int(raw.get("turn_count", 0)),
            done=bool(raw.get("done", False)),
            reward=float(raw.get("reward", 0.0)),
            topic=raw.get("topic", ""),
            feedback=raw.get("feedback", ""),
        )


if __name__ == "__main__":
    import os
    url = os.environ.get("SOCRATIC_RL_URL", SocraticClient.DEFAULT_URL)
    print(f"Connecting to: {url}")
    client = SocraticClient(base_url=url)
    print("Resetting...")
    obs = client.reset()
    print(f"Topic: {obs.topic}")
    print(f"Student: {obs.student_response[:100]}")
    questions = [
        "What would happen if you dropped both objects in a vacuum?",
        "Why do you think mass would affect how fast something falls?",
        "If gravity gives the same acceleration to all objects, what does that mean for fall speed?",
    ]
    for q in questions:
        print(f"\nAgent: {q}")
        obs = client.step(SocraticAction(question=q))
        print(f"Student: {obs.student_response[:100]}")
        print(f"Understanding: {obs.understanding_score:.3f} | Reward: {obs.reward:+.3f}")
        print(f"Feedback: {obs.feedback}")
        if obs.done:
            print("Episode complete.")
            break
