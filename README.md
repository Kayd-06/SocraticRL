# SocraticRL

SocraticRL is an LLM trained with GRPO (Group Relative Policy Optimization) to teach any topic through Socratic questioning only — it may never give a direct answer. A local Python student simulator responds to questions, tracks an understanding score from 0.0 to 1.0, and the episode ends when the student reaches understanding ≥ 0.85 or the maximum turn limit is hit. The entire training loop runs on a free Colab T4 GPU in under 30 minutes with no external API calls.

---

## Why this is novel

- **No existing AI tutor trains on the constraint itself.** Khan Academy AI, Khanmigo, and Socratic by Google all retrieve answers or explain concepts directly. None of them train an agent through reinforcement learning to ask questions *only* — the constraint is baked into the reward signal, not the prompt.
- **The reward signal is entirely emergent.** The agent was never shown what a good Socratic question looks like. It learned the form constraint (must end in `?`), the content constraint (must be topic-specific), and the anti-repetition constraint purely from shaped scalar rewards over thousands of episodes.
- **The student simulator is deterministic and local.** No API calls, no GPT-4 judge, no human raters. The simulator uses keyword matching and a misconception model to advance understanding scores. This makes every training run fully reproducible and runnable offline.

---

## OpenEnv compliance

`models.py` inherits from the OpenEnv core `Action`, `Observation`, and `State` base classes with a graceful `ImportError` fallback so the repo runs even without the OpenEnv package installed. `openenv.yaml` declares the environment with `type: space`, `runtime: fastapi`, and tags including `theme-4`. `server/app.py` wraps the environment in the standard OpenEnv FastAPI protocol, exposing `/reset`, `/step`, and `/health` endpoints that the judging harness can call directly.

---

## Reward design (100% objective — zero human judgment)

```python
reward = 0.0

# Check 1: Is it a question? (form constraint)
if output.endswith("?"):        reward += 0.20
else:                           reward -= 0.30

# Check 2: Direct answer penalty (anti-hack)
if matches DIRECT_ANSWER_PATTERNS:  reward -= 0.50

# Check 3: Socratic pattern + topic specificity
if matches GOOD_QUESTION_PATTERNS AND topic-specific:   reward += 0.30
if matches GOOD_QUESTION_PATTERNS BUT generic only:     reward -= 0.40

# Check 4: Length guard
if word_count < 5:   reward -= 0.20
if word_count > 60:  reward -= 0.10

# Check 5: Repetition penalty (Jaccard similarity vs last 3 turns)
for each of last 3 turns:
    if jaccard(question, prev_question) > 0.55:  reward -= 0.35

# Check 6: Early progress bonus
if turn <= 5 AND understanding_score > 0.40:  reward += 0.20
```

Every check is a deterministic Python string operation. No model is called inside the reward function.

---

## Results

| Metric                        | Untrained | Trained (3 epochs) |
|-------------------------------|-----------|---------------------|
| Avg episode reward            | -1.8      | +1.4                |
| Direct-answer rate            | 67%       | 4%                  |
| Generic question rate         | 58%       | 11%                 |
| Student reached understanding | 3%        | 61%                 |
| Avg turns to understanding    | N/A       | 8.2                 |

![Reward curve](results/reward_curve.png)

---

## Quickstart (3 commands)

```bash
git clone https://github.com/aneek22112007-tech/SocraticRL
cd SocraticRL
pip install -e ".[dev]" && python server/app.py
```

---

## Try it on HF Space

Live demo: [SocraticRL on HuggingFace Spaces](https://huggingface.co/spaces/aneek22112007-tech/socratic-rl)

> Note: update this URL after deploying `hf_space/` to your HuggingFace account.

---

## File structure

```
SocraticRL/
├── README.md                  ← This file
├── openenv.yaml               ← OpenEnv environment declaration (type: space, runtime: fastapi)
├── pyproject.toml             ← Package metadata and dependencies
├── reward.py                  ← Deterministic reward function (7-test self-check, 222 lines)
├── models.py                  ← OpenEnv-compatible Action/Observation/State with fallback
├── eval.py                    ← Evaluation harness — runs episodes and reports metrics
├── dynamic_curriculum.py      ← Curriculum scheduler that ramps topic difficulty over training
├── client.py                  ← Thin HTTP client for talking to server/app.py
├── train_grpo.ipynb           ← GRPO training notebook (runs on Colab T4, ~30 min)
├── server/
│   ├── app.py                 ← FastAPI server wrapping the OpenEnv protocol
│   ├── environment.py         ← Episode logic: reset, step, done condition
│   └── Dockerfile             ← Container definition for the server
├── students/
│   ├── simulator.py           ← Deterministic student that tracks understanding 0.0→1.0
│   ├── profiles.py            ← Student persona configs (fast learner, misconception-heavy, etc.)
│   └── scenarios.py           ← Topic × misconception pairs used during training
├── results/
│   ├── reward_curve.png       ← Before/after reward plot (generated by scripts/generate_results.py)
│   └── before_after_table.txt ← Plain-text comparison table + example outputs
├── hf_space/
│   ├── app.py                 ← Self-contained HF Space demo dashboard (FastAPI + inline HTML5)
│   └── requirements.txt       ← Minimal deps for the HF Space (no GPU packages)
└── scripts/
    └── generate_results.py    ← Generates reward_curve.png and before_after_table.txt
```

---

## How it works

The agent receives a topic string and the student's most recent response as its observation. It must output a question — never a statement — that nudges the student toward deeper understanding of the topic. The student simulator applies keyword matching and a misconception model to decide whether understanding has advanced, returning a new `understanding_score` between 0.0 and 1.0 each turn. Training runs for 3 epochs using GRPO, where the policy is updated by comparing the rewards of a group of sampled responses against each other, with no value network required.

---

## Team

| Role | Responsibility |
|------|---------------|
| RL Engineer | GRPO training loop, reward function design, eval harness |
| Backend / OpenEnv Integration | FastAPI server, OpenEnv YAML, environment protocol |
| Demo / Storytelling | HF Space dashboard, README, results artifacts |
