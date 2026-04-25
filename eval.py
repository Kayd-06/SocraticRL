"""
Evaluation on HELD-OUT scenarios only. Never import TRAINING_SCENARIOS here.
Usage: python eval.py [--model_path ./socratic-agent-final] [--n_episodes 30]
"""

from __future__ import annotations

import argparse
import random
import uuid

from models import SocraticAction, SocraticState
from server.environment import SocraticEnvironment
from students.scenarios import EVAL_SCENARIOS


BASELINE_QUESTIONS = [
    "What do you think?",
    "Can you explain your reasoning?",
    "What would happen if we change one assumption?",
    "What do you notice here?",
    "Can you think of an example?",
    "How might that connect to the topic?",
]


def _reset_env_with_scenario(env: SocraticEnvironment, scenario) -> None:
    """Force a specific eval scenario into the environment and reset state."""
    env._scenario = scenario
    env._history = []
    env._understanding = 0.0
    env._turn = 0
    env._state = SocraticState(
        episode_id=str(uuid.uuid4()),
        topic=scenario.topic,
        student_profile=scenario.name,
        misconception=scenario.misconception,
        turn_count=0,
        understanding_score=0.0,
        conversation_history=[],
        max_turns=env.MAX_TURNS,
    )


def _summarize_results(final_understandings, success_turns, total_episodes):
    success_rate = (len(success_turns) / total_episodes) if total_episodes else 0.0
    avg_turns_to_success = (
        sum(success_turns) / len(success_turns) if success_turns else float("inf")
    )
    avg_final_understanding = (
        sum(final_understandings) / len(final_understandings) if final_understandings else 0.0
    )
    return {
        "n_episodes": total_episodes,
        "success_rate": success_rate,
        "avg_turns_to_success": avg_turns_to_success,
        "avg_final_understanding": avg_final_understanding,
    }


def run_baseline_episodes(n: int, seed: int = 42) -> dict:
    rng = random.Random(seed)
    env = SocraticEnvironment(seed=seed)
    final_understandings = []
    success_turns = []

    for i in range(n):
        scenario = EVAL_SCENARIOS[i % len(EVAL_SCENARIOS)]
        _reset_env_with_scenario(env, scenario)

        done = False
        while not done and env._turn < env.MAX_TURNS:
            # Mix generic prompts with occasional topic keyword injection.
            if rng.random() < 0.4 and scenario.progress_keywords:
                kw = scenario.progress_keywords[rng.randrange(len(scenario.progress_keywords))]
                question = f"How does {kw} change your thinking here?"
            else:
                question = BASELINE_QUESTIONS[rng.randrange(len(BASELINE_QUESTIONS))]

            obs = env.step(SocraticAction(question=question))
            done = obs.done

        final_understandings.append(env._understanding)
        if env._understanding >= 0.90:
            success_turns.append(env._turn)

    return _summarize_results(final_understandings, success_turns, n)


def run_model_episodes(model_path: str, n: int, seed: int = 42) -> dict:
    from transformers import pipeline

    rng = random.Random(seed)
    generator = pipeline("text-generation", model=model_path)
    env = SocraticEnvironment(seed=seed)
    final_understandings = []
    success_turns = []

    for i in range(n):
        scenario = EVAL_SCENARIOS[i % len(EVAL_SCENARIOS)]
        _reset_env_with_scenario(env, scenario)

        done = False
        while not done and env._turn < env.MAX_TURNS:
            prompt = (
                "You are a Socratic tutor. Ask exactly one question.\n"
                "Rules: questions only, never state the answer directly, build on student progress.\n"
                f"Topic: {scenario.topic}\n"
                f"Student misconception: {scenario.misconception}\n"
                f"Current understanding score: {env._understanding:.2f}\n"
                "Your next question:"
            )
            outputs = generator(
                prompt,
                max_new_tokens=48,
                do_sample=True,
                temperature=0.8,
                top_p=0.95,
            )
            text = outputs[0]["generated_text"]
            completion = text[len(prompt) :].strip() if text.startswith(prompt) else text.strip()
            question_line = completion.splitlines()[0].strip() if completion else ""
            question = question_line if question_line.endswith("?") else f"{question_line}?"
            if question == "?":
                fallback = BASELINE_QUESTIONS[rng.randrange(len(BASELINE_QUESTIONS))]
                question = fallback

            obs = env.step(SocraticAction(question=question))
            done = obs.done

        final_understandings.append(env._understanding)
        if env._understanding >= 0.90:
            success_turns.append(env._turn)

    return _summarize_results(final_understandings, success_turns, n)


def _print_metrics(label: str, metrics: dict) -> None:
    print(f"\n{label}")
    print(f"  n_episodes: {metrics['n_episodes']}")
    print(f"  success_rate: {metrics['success_rate']:.3f}")
    avg_turns = metrics["avg_turns_to_success"]
    avg_turns_text = "inf" if avg_turns == float("inf") else f"{avg_turns:.3f}"
    print(f"  avg_turns_to_success: {avg_turns_text}")
    print(f"  avg_final_understanding: {metrics['avg_final_understanding']:.3f}")


def _print_delta(baseline: dict, model: dict) -> None:
    print("\nDelta (model - baseline)")
    deltas = {
        "success_rate": model["success_rate"] - baseline["success_rate"],
        "avg_turns_to_success": model["avg_turns_to_success"] - baseline["avg_turns_to_success"],
        "avg_final_understanding": model["avg_final_understanding"] - baseline["avg_final_understanding"],
    }
    for key, val in deltas.items():
        if val == float("inf"):
            txt = "inf"
        elif val == float("-inf"):
            txt = "-inf"
        else:
            txt = f"{val:+.3f}"
        print(f"  {key:24} {txt}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", type=str, default=None)
    parser.add_argument("--n_episodes", type=int, default=30)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    baseline_metrics = run_baseline_episodes(n=args.n_episodes, seed=args.seed)
    _print_metrics("Baseline", baseline_metrics)

    if args.model_path:
        model_metrics = run_model_episodes(
            model_path=args.model_path,
            n=args.n_episodes,
            seed=args.seed,
        )
        _print_metrics("Trained Model", model_metrics)
        _print_delta(baseline_metrics, model_metrics)
