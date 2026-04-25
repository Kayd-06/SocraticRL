from dataclasses import dataclass, field
from typing import List

try:
    from openenv_core.models import Action, Observation, State
except ImportError:
    @dataclass
    class Action:
        pass

    @dataclass
    class Observation:
        pass

    @dataclass
    class State:
        pass


@dataclass
class SocraticAction(Action):
    question: str = ""
    reasoning: str = ""  # chain-of-thought, never shown to student


@dataclass
class SocraticObservation(Observation):
    student_response: str = ""
    understanding_score: float = 0.0  # 0.0 to 1.0
    turn_count: int = 0
    done: bool = False
    reward: float = 0.0
    topic: str = ""
    feedback: str = ""  # pipe-separated reward breakdown for logging


@dataclass
class SocraticState(State):
    episode_id: str = ""
    topic: str = ""
    student_profile: str = ""
    misconception: str = ""
    turn_count: int = 0
    understanding_score: float = 0.0
    conversation_history: list = field(default_factory=list)
    max_turns: int = 15
