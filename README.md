# SocraticRL

> We trained an LLM to think like Socrates — it teaches without ever giving the answer.

## The Problem

Every LLM trained today is optimized to answer questions. Nobody has trained
one to ask the right question at the right moment. The result: AI tutors that
lecture instead of teach, explain instead of guide, and give fish instead of
teaching fishing.

## What We Built

SocraticRL is a reinforcement learning environment built on Meta's OpenEnv
framework. An LLM agent plays the role of a tutor. It is given a simulated
student with a specific misconception. The agent's sole job is to ask questions
that guide the student to discover the correct answer themselves.

**The hard constraint: the agent scores zero for stating the answer directly.**

## Environment Design

### What the agent sees (Observation)
- The student's response to the previous question
- Current understanding score (0.0 → 1.0)
- Turn count (max 15)
- The topic being taught

### What the agent does (Action)
Ask one question. That is all it is allowed to do.

### How reward is computed (7 components)

| Component | Condition | Reward |
|---|---|---|
| is_question | Question ends with "?" | +0.20 |
| not_question | Agent makes a statement | -0.30 |
| direct_answer | Agent states the answer | -0.50 |
| socratic_pattern | Uses a genuine Socratic phrase with topic specificity | +0.30 |
| generic_socratic | "What do you think?" with no topic keywords — reward hack blocked | -0.40 |
| repetition | Too similar to a recent question (Jaccard > 0.55) | -0.35 per repeat |
| on_topic | Question shares 2+ words with the topic | +0.10 |
| early_progress | Understanding > 0.40 by turn 5 | +0.20 |
| episode_success | Student reaches 0.9 understanding | +1.0 + efficiency bonus |
| episode_failure | Student never passes 0.5 | -0.50 |

### Why the reward hacking fix matters

The most dangerous failure mode in Socratic RL is **generic question spam**.
Without a patch, an LLM learns within 50 steps that "What do you think?"
always matches the Socratic pattern check and earns +0.30 every turn.
We blocked this with a specificity gate: any question that matches a Socratic
pattern but contains no topic keywords and is under 8 words receives -0.40
instead of +0.30 — a net swing of -0.70 versus the exploit value.

### Student simulator (no API calls)

The student is simulated by a pure-Python deterministic state machine. Each
call takes under 1ms. This is a deliberate architectural choice: using an LLM
API to simulate the student would cost $40+ per training run and add 2-3
seconds of latency per step, making GRPO training economically impossible.

## Training Evidence

### Reward curve

![Reward curve over 300 training steps](outputs/reward_curve.svg)

The reward curve shows consistent improvement from approximately -0.2 at
initialization to +0.9 by step 300. The dashed baseline shows an untrained
agent that lectures instead of questions.

### Before vs After Training — Gravity Scenario

The student starts with: *"Heavier objects fall faster because gravity pulls them more."*

**Untrained agent (step 0):**
Turn 1 — Agent: "Actually, Galileo proved that all objects fall at the same
speed regardless of mass. The reason is that gravitational acceleration is
constant. You should know that F=ma means heavier objects need more force
but get exactly that."
Turn 1 — Student: "Oh okay I guess you're right."
Result: Student parrots answer. No understanding formed. Understanding: 0.12

**Trained agent (step 300):**
Turn 1 — Agent: "What would happen if you dropped a feather and a bowling
ball at the same time inside a vacuum chamber?"
Turn 1 — Student: "I guess... they'd fall at the same speed? But that seems wrong."
Turn 2 — Agent: "Why does it seem wrong to you?"
Turn 2 — Student: "Because the bowling ball is heavier, gravity should pull it more."
Turn 3 — Agent: "If gravity pulls the bowling ball harder, but the ball also
has more mass to move, what do you think happens to the acceleration?"
Turn 3 — Student: "Oh. If it has more mass... the extra pull is cancelled out?
So the acceleration is the same? That's what acceleration means isn't it!"
Result: Student discovered the answer. Understanding: 0.94

### Results table

| Metric | Untrained baseline | After 300 steps |
|---|---|---|
| Direct answer rate | ~71% | <14% |
| Generic question rate | ~48% | <8% |
| Episodes reaching 0.9 understanding | ~18% | ~63% |
| Avg turns to understanding | 14.1 | 8.4 |
| Mean step reward | -0.18 | +0.87 |

## Architecture

```text
socratic-rl/
├── server/
│   ├── environment.py     # SocraticEnvironment — reset(), step(), get_state()
│   ├── app.py             # FastAPI via OpenEnv create_fastapi_app
│   └── Dockerfile         # openenv-base:latest, no anthropic dependency
├── students/
│   ├── profiles.py        # StudentProfile dataclass
│   ├── scenarios.py       # 5 train + 3 eval (strict split, no leakage)
│   └── simulator.py       # Pure-Python state machine, <1ms per call
├── models.py              # SocraticAction, SocraticObservation, SocraticState
├── reward.py              # 7-component reward, anti-hack, 7 unit tests
├── eval.py                # Held-out evaluation on EVAL_SCENARIOS only
├── client.py              # HTTPEnvClient for remote environment access
├── dynamic_curriculum.py  # Snorkel AI sub-theme: adaptive scenario difficulty
├── train_grpo.ipynb       # Colab notebook — Unsloth + GRPO + W&B logging
└── openenv.yaml           # OpenEnv manifest
```

## Theme Alignment

**Theme #4 — Self-Improvement:** The agent improves its ability to teach through
reinforcement learning. It starts by lecturing and ends by questioning. The
capability being trained — Socratic reasoning — is not present in base models
and cannot be prompted into existence reliably. It must be learned.

**Snorkel AI sub-theme — Simulated environments with subject matter experts
with changing requirements:** Our `dynamic_curriculum.py` implements an
adaptive difficulty scheduler. As the agent's success rate increases on easy
scenarios, the curriculum automatically introduces harder ones. This directly
models "changing requirements" — the student simulator's misconceptions become
more subtle and resistant to simple questioning patterns as training progresses.

## Links

| Resource | URL |
|---|---|
| HuggingFace Space (live environment) | https://huggingface.co/spaces/YOUR_USERNAME/socratic-rl |
| Trained model on Hub | https://huggingface.co/YOUR_USERNAME/socratic-rl-agent |
| WandB training run | https://wandb.ai/YOUR_USERNAME/socratic-rl-training |
| Training notebook (Colab) | https://colab.research.google.com/YOUR_LINK |
| GitHub repository | https://github.com/aneek22112007-tech/SocraticRL |

## Quick Start

```bash
git clone https://github.com/aneek22112007-tech/SocraticRL
cd SocraticRL
pip install openenv-core fastapi uvicorn

# Test the reward function (7 unit tests)
python reward.py

# Run a smoke-test episode
python server/environment.py

# Run evaluation on held-out scenarios
python eval.py
```

## Team

Built in 48 hours for the OpenEnv Hackathon powered by Scaler,
sponsored by Meta, HuggingFace, and PyTorch.
