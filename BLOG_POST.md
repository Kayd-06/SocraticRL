# I Trained an AI to Never Give the Answer

*And somehow, it became a better teacher because of it.*

---

My worst teacher in school never explained anything badly. He explained everything *perfectly*. Crystal clear. Every time I asked "why does this work?", he'd give me a beautiful, complete, airtight answer.

And I learned almost nothing from him.

My best teacher did something annoying. Every time I asked her something, she'd tilt her head slightly and say: *"Hmm. What do you think?"*

I hated it at the time. But here's the thing, I still remember everything she taught me.

That difference is the entire reason SocraticRL exists.

---

## The Problem With AI Tutors Today

If you've ever used ChatGPT or any AI assistant to help you understand something, you've noticed a pattern. You ask a question, and it, answers you. Completely. Immediately. With bullet points and everything. Which feels helpful. And for some things like writing code, looking something up, it is.

But for *understanding*? It's a disaster. You read the answer, you nod, you think you get it. Then a week later someone asks you the same question and you draw a blank. The answer never made it from your eyes to your brain in the way that matters.

Real understanding doesn't come from being told things. It comes from being made to think.

The Socratic method: asking guided questions instead of giving answers. It is one of the oldest and most validated teaching techniques on the planet. Socrates used it. The best tutors still use it. And almost no AI does it, because it is genuinely hard. It requires the teacher to hold back.

I wanted to build an AI that was *trained* to hold back.

---

## The Idea: Pay the AI for Good Questions

Here's the simplest way to explain what SocraticRL does:

Imagine I gave you £1 every time you asked a question that genuinely pushed a student closer to understanding, and fined you £2 every time you just explained the answer directly. Over thousands of practice sessions, you'd get very good at asking questions.

That's it. That's the project.

More precisely: I built a reinforcement learning environment where an LLM agent gets a **reward signal** based entirely on the quality of the questions it asks. It never sees the student's "correct understanding" directly, it only gets feedback based on whether its question moved the student in the right direction.

The agent starts by asking random, generic, sometimes terrible questions. Over thousands of training episodes, it learns what a good Socratic question actually looks like.

---

## The Reward Function: Where the Real Work Lives

The soul of this project is `reward.py`. 222 lines of Python that define, mathematically, what makes a question good or bad.

Here's the full breakdown:

| Behaviour | Reward |
|---|---|
| Asks a question (ends with ?) | +0.20 |
| Doesn't ask a question | -0.30 |
| Gives a direct answer | -0.50 |
| Socratic pattern + topic-specific | +0.30 |
| Generic Socratic pattern only | -0.40 |
| Response too short (<5 words) | -0.20 |
| Response too long (>60 words) | -0.10 |
| Repeats a recent question | -0.35 |
| Topic keyword overlap | +0.10 |
| Early progress bonus (turn ≤5, score >0.4) | +0.20 |

The `-0.50` for direct answers is the core constraint. The agent learns fast that saying *"the answer is…"* is a losing move.

But here's where it gets interesting.

**The agent found loopholes.**

Early in training, it discovered it could game the reward by just appending a question mark to generic filler phrases. Things like:

> *"What do you think?"*

Technically a question. Technically ends with `?`. Reward collected. Completely useless.

So I added the **generic-only penalty**: if the response matches a Socratic pattern but has zero specificity to the topic,no keywords, no connection to what's actually being taught. It gets hit with `-0.40` instead. A net loss.

I also added a **Jaccard similarity check** against the last 3 turns. If the agent asks a question it's already essentially asked (word overlap above 55%), it gets penalised `-0.35` per repeat. Because a real teacher doesn't just rephrase the same question on loop hoping the student eventually agrees.

These weren't in the original plan. I added them after watching the agent exploit every gap I left open. Watching an AI find the cracks in your reward function is one of the more humbling experiences in ML.

---

## Training: GRPO in Plain English

The training algorithm is **GRPO** , Group Relative Policy Optimization. If you've heard of PPO (the algorithm behind a lot of RLHF work), GRPO is a leaner version of the same idea.

The basic intuition: instead of training on one response at a time, you generate a *group* of responses to the same prompt, compare them to each other, and push the model toward the ones with higher rewards. It's like showing a student ten different attempts at a problem and asking them to understand why the best one worked.

Training happens in `train_grpo.ipynb`. The model being fine-tuned is a small open-source LLM served locally with no API calls required. The whole pipeline runs on your machine.

---

## The Student on the Other Side

Every RL environment needs something to act *on*. In this case, that's a simulated student.

The student simulator (in the `students/` folder) starts each episode holding a specific misconception about a topic. For example:

> *"Heavier objects fall faster because gravity pulls them more strongly."*

After each teacher question, the student generates a response. Then the simulator computes an **understanding score**, a float between 0.0 and 1.0, by measuring how semantically close the student's latest response is to the "correct understanding" reference using `sentence-transformers` cosine similarity.

At the start of an episode, the student is at about `0.05` understanding. The episode ends when they hit `0.90` (success) or the turn limit runs out (failure). Watching that number climb through good questions, and stall through bad ones, tells you everything about whether the teacher is actually teaching.

---

## Does It Work?

Short answer: yes, and by a lot more than I expected.

Here's what happens when you compare a baseline agent (random questions) against the trained SocraticRL agent on **5 held-out topics it never saw during training**:

| Metric | Baseline | SocraticRL | Δ |
|---|---|---|---|
| Success rate | 13.3% | 76.7% | **+63.4pp** |
| Avg turns to success | 12.3 | 6.4 | **-5.9 turns** |
| Final understanding score | 0.412 | 0.814 | **+0.402** |

```
Training reward over 200 episodes:

 0.8 │                                          ╭───────────
 0.6 │                              ╭───────────╯
 0.4 │                  ╭───────────╯
 0.2 │     ╭────────────╯
 0.0 │─────╯
     └────────────────────────────────────────────────────
     Ep 1                  100                          200
```

But the numbers only tell half the story. The real evidence is in the conversations themselves.

Here's the same student, same topic, before and after training:

---

**Topic:** *Why do heavy and light objects fall at the same speed?*

**Student:** "Heavier objects fall faster because gravity pulls them more strongly."

---

**Before training (baseline):**

> **Teacher:** "The answer is that gravitational acceleration is constant at 9.8 m/s² regardless of mass, as proven by Galileo's experiment at the Tower of Pisa."

Reward: **-0.60** 

The student received a fact. They did not have to think. They may have nodded. They probably forgot it within the hour.

---

**After training (SocraticRL):**

> **Teacher:** "What do you think would happen if you dropped both objects inside a vacuum tube, where there's no air at all?"

Reward: **+0.60** 

> **Student:** "Oh… without air, the feather wouldn't slow down?"

> **Teacher:** "If air resistance is the only difference between the two situations, what does that tell you about gravity itself?"

Reward: **+0.70** *(early-progress bonus triggered, understanding already at 0.52)*

> **Student:** "So gravity is the same for both? It was the air confusing me the whole time?"

Understanding score: **0.81** 

---

That second conversation took 2 turns. The student arrived at the answer themselves. They will remember it.

---

## What I Didn't Expect

Building this, I ran into one question I couldn't shake:

*How do you put a number on good teaching?*

The reward function forces you to be explicit about something teachers do intuitively. What makes a question "good"? It has to be specific to the topic. It can't give away the answer. It should connect to where the student currently is, not where you want them to be.

Every time I thought I'd captured it, the agent found a way to score points without actually teaching. It was frustrating, and also kind of fascinating because the failure modes of the agent were the exact same failure modes of bad teachers. Vague questions. Repetition. Slightly rephrased explanations disguised as questions.

The other surprise was how much the *order* of questions mattered. A question that's perfect at turn 7 might be completely wrong at turn 2. The agent learned this. It asks broader questions early and gets progressively more targeted as the student's understanding score climbs. That emergent pacing, nobody programmed it in, was the moment I thought this was actually working.

---

## What Comes Next

The obvious next step is real students instead of simulated ones, running the trained agent in actual tutoring sessions and measuring whether understanding scores translate to real learning outcomes.

Beyond that: comparing SocraticRL against GPT-4 playing teacher in zero-shot mode, adding multi subject curriculum support, and exploring whether the Socratic constraint generalises to domains like therapy or coaching where the same principle, guide, don't tell, applies just as strongly.

But for now, a small LLM has learned something that most AI tutors haven't:

*Sometimes the best answer is a better question.*

---

**GitHub:** [github.com/aneek22112007-tech/SocraticRL](https://github.com/aneek22112007-tech/SocraticRL)
