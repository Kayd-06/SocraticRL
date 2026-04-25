"""
client.py - Remote environment client for SocraticRL.

Use this when the environment is deployed to HuggingFace Spaces and you
want to run training from a local machine or Colab against the remote env.
"""

try:
    from openenv_core.client import HTTPEnvClient
except ImportError:
    class HTTPEnvClient:
        pass

from models import SocraticAction, SocraticObservation


class SocraticClient(HTTPEnvClient):
    """
    HTTP client that connects to the deployed SocraticRL HuggingFace Space.
    Wraps raw dict responses into typed SocraticObservation objects.
    """

    DEFAULT_URL = "https://YOUR_USERNAME-socratic-rl.hf.space"

    def __init__(self, base_url: str = DEFAULT_URL):
        super().__init__(base_url=base_url)

    def reset(self) -> SocraticObservation:
        raw = super().reset()
        return self._parse(raw)

    def step(self, action: SocraticAction) -> SocraticObservation:
        payload = {"question": action.question, "reasoning": action.reasoning}
        raw = super().step(payload)
        return self._parse(raw)

    @staticmethod
    def _parse(raw: dict) -> SocraticObservation:
        if not isinstance(raw, dict):
            raw = {}
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
    # Quick connectivity test
    # Instantiate client, reset, take 3 steps with a test question
    # Print each observation
    # This lets you verify the HF Space is live before running training
    client = SocraticClient()
    print("Connecting to:", client.DEFAULT_URL)
    obs = client.reset()
    print("RESET:", obs)

    test_question = "What would happen if you tested this in a controlled setup?"
    for i in range(3):
        obs = client.step(SocraticAction(question=test_question))
        print(f"STEP {i + 1}:", obs)
        if obs.done:
            break
