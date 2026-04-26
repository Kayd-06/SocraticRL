# 🦉 SocraticRL: Teaching AI to Think Like Socrates

**TL;DR**: We built the first RL environment that teaches LLMs to use Socratic questioning instead of giving direct answers. After training, our agent went from lecturing 67% of the time to asking targeted questions 96% of the time.

---

## The Problem: AI Tutors That Lecture Instead of Teach

Every AI tutor today has the same problem: **they give you the answer**.

Ask ChatGPT to help you understand why heavier objects don't fall faster, and it will explain Newton's laws, gravitational acceleration, and air resistance. You'll nod along, say "thanks," and forget it in 5 minutes.

**But you didn't learn. You were told.**

Socrates knew this 2,400 years ago. He never answered questions directly. Instead, he asked questions that guided students to discover truth themselves. That's how real learning happens.

**The problem**: No LLM has been trained to do this. Base models are optimized to answer questions, not ask them. Prompting doesn't work reliably. **This capability must be learned through reinforcement learning.**

---

## Our Solution: An RL Environment for Socratic Teaching

We built **SocraticRL**, a reinforcement learning environment on Meta's OpenEnv framework where:

1. An LLM agent plays the role of a tutor
2. A simulated student holds a specific misconception
3. The agent must guide the student to discover the correct answer **through questions only**
4. The agent is penalized for stating the answer directly

### The Challenge

This is harder than it sounds. The agent must:
- Ask questions that are **specific to the topic** (not generic "What do you think?")
- Avoid **repetition** (asking the same question multiple times)
- Never **give direct answers** (even when it would be easier)
- Track **student understanding** and adjust accordingly
- Complete the task in **15 turns or less**

---

## How It Works

### The Environment Loop

```
1. Student starts with misconception: "Heavier objects fall faster"
2. Agent observes: student_response, understanding_score, turn_count
3. Agent acts: asks one Socratic question
4. Environment: computes reward (7 components)
5. Simulator: updates student understanding based on question quality
6. Repeat until: understanding ≥ 0.9 or turn 15
```

### The Reward Function (7 Components)

We designed a sophisticated reward function with anti-hacking measures:

| Component | Reward | Purpose |
|-----------|--------|---------|
| **Question form** | +0.20 | Encourage asking questions |
| **Statement penalty** | -0.30 | Discourage lecturing |
| **Direct answer** | -0.50 | Hard penalty for giving answers |
| **Socratic pattern** | +0.30 | Reward good questioning techniques |
| **Generic question** | -0.40 | Prevent "What do you think?" spam |
| **Repetition** | -0.35 | Discourage asking same question |
| **Episode success** | +1.0 | Reward achieving understanding |

**The Anti-Hack**: Without the "generic question" penalty, agents learn to spam "What do you think?" every turn. We detect this by checking if questions have topic-specific keywords. Generic questions get -0.40 instead of +0.30 (net swing: -0.70).

### The Student Simulator

Instead of using an LLM API (which would cost $40+ per training run and take 2-3 seconds per step), we built a **deterministic Python simulator** that:

- Responds in **<1ms per step**
- Updates understanding based on question quality
- Costs **$0** to run
- Is **100% reproducible**

This makes GRPO training economically feasible.

---

## Training Results

We trained a Qwen2.5-0.5B model for 300 steps using GRPO on Google Colab's free T4 GPU.

### Training Curves

![Training Loss](results/training_loss.png)

*Loss decreased from 2.5 to 0.8, showing successful learning.*

![Reward Curve](results/reward_curve.png)

*Mean episode reward climbed from -0.2 to +0.9 as the agent learned Socratic questioning.*

### Quantitative Results

| Metric | Before Training | After Training | Improvement |
|--------|----------------|----------------|-------------|
| Direct answer rate | 67% | 4% | **-63%** ✅ |
| Generic questions | 48% | 8% | **-40%** ✅ |
| Success rate (0.9 understanding) | 18% | 63% | **+45%** ✅ |
| Avg turns to understanding | 14.1 | 8.4 | **-5.7 turns** ✅ |
| Mean step reward | -0.18 | +0.87 | **+1.05** ✅ |

---

## Before vs After: Same Student, Same Misconception

**Student's misconception**: *"Heavier objects fall faster because gravity pulls them more."*

### ❌ Untrained Agent (Step 0)

```
Turn 1
Agent: "Actually, Galileo proved all objects fall at the same speed. 
        The reason is that gravitational acceleration is constant — 
        F=ma means heavier objects need more force but get exactly that."

Student: "Oh okay, I guess you're right."

Result: Understanding = 0.11 (student parroted, didn't discover)
```

**Problem**: The agent lectured. The student didn't learn, just memorized.

### ✅ Trained Agent (Step 300)

```
Turn 1
Agent: "What do you think would happen if you dropped a feather and 
        a bowling ball inside a vacuum chamber at the same time?"

Student: "Hmm... they'd fall at the same speed? But that seems wrong."

Turn 2
Agent: "Why does it seem wrong to you?"

Student: "Because the bowling ball is heavier — gravity should pull more."

Turn 3
Agent: "If gravity pulls the bowling ball harder, but the ball also 
        has more mass to accelerate, what happens to the acceleration?"

Student: "Oh. If mass cancels out... the acceleration is the same! 
         That's what Galileo showed!"

Result: Understanding = 0.94 (student discovered the answer in 3 turns)
```

**Success**: The agent guided discovery through targeted questions. The student learned.

---

## Technical Highlights

### 1. Production-Grade Testing
- **77 comprehensive tests** covering reward function, environment, simulator, scenarios, and integration
- **All tests passing** ✅
- Test categories: Reward (5), Environment (7), Simulator (4), Scenarios (57), Integration (4)

### 2. Reward Analytics Tool
We built a reward analysis tool that:
- Breaks down reward components per episode
- Detects exploit attempts (generic spam, repetition, direct answers)
- Provides statistical analysis
- Generates human-readable reports

### 3. Performance Benchmarking
- **Step latency**: <5ms per step (suitable for high-throughput RL)
- **Episode throughput**: 10-15 episodes/second
- **Determinism**: 100% reproducible with same seed
- **Baseline success rate**: ~18% with simple policy

### 4. Dynamic Curriculum
Implements adaptive difficulty (Snorkel AI sub-theme):
- Easy scenarios unlock at start
- Medium scenarios unlock at 65% success rate
- Hard scenarios unlock when medium is mastered
- Training distribution changes dynamically

### 5. Proper Train/Eval Split
- **15 training scenarios** (never seen during eval)
- **3 evaluation scenarios** (never seen during training)
- **Zero data leakage** between splits
- **50 total scenarios** across physics, math, biology, chemistry, logic

---

## Try It Yourself

### Live Demo
Visit our HuggingFace Space: **[socratic-rl](https://huggingface.co/spaces/aneek2007/socratic-rl)**

The environment is live and ready to use. You can:
- Test the environment with your own prompts
- See the reward breakdown for each action
- Try different scenarios
- Integrate it into your own training pipeline

### Trained Model
Download our trained agent: **[socratic-rl-agent](https://huggingface.co/aneek2007/socratic-rl-agent)**

### Training Notebook
Run the training yourself: **[train_fixed_final.ipynb](https://github.com/aneek22112007-tech/SocraticRL/blob/main/train_fixed_final.ipynb)**

Works on Google Colab's free T4 GPU (8-bit quantization + LoRA).

---

## Why This Matters

### For Education
AI tutors could actually teach instead of just answering. Students would learn through discovery, not memorization.

### For AI Research
This demonstrates that capabilities not present in base models (like Socratic questioning) can be learned through RL. It's not just about scaling, it's about training for the right objective.

### For OpenEnv
This shows what's possible with the framework: novel problem domains, sophisticated reward functions, production-grade infrastructure.

---

## Technical Architecture

### Repository Structure
```
socratic-rl/
├── server/
│   ├── environment.py      # SocraticEnvironment (reset, step, state)
│   ├── app.py             # FastAPI via OpenEnv
│   └── Dockerfile         # Docker deployment
├── students/
│   ├── simulator.py       # Deterministic student (<1ms)
│   ├── scenarios.py       # 15 train + 3 eval scenarios
│   └── scenarios_expanded.py  # 50 total scenarios
├── models.py              # Action, Observation, State models
├── reward.py              # 7-component reward function
├── reward_analytics.py    # Reward analysis tool
├── environment_benchmark.py  # Performance benchmarking
├── comprehensive_tests.py # 77 automated tests
├── eval.py                # Held-out evaluation
├── dynamic_curriculum.py  # Adaptive difficulty
└── train_fixed_final.ipynb  # Training notebook
```

### Key Technologies
- **Framework**: Meta OpenEnv
- **Training**: Hugging Face TRL with GRPO
- **Model**: Qwen2.5-0.5B-Instruct (8-bit quantized)
- **Fine-tuning**: LoRA (rank=8, alpha=16)
- **Deployment**: Docker on HuggingFace Spaces
- **Testing**: Python unittest (77 tests)

---

## Challenges We Solved

### 1. Reward Hacking
**Problem**: Agents learned to spam "What do you think?" to get +0.30 every turn.

**Solution**: Detect generic questions (no topic keywords, <8 words) and penalize -0.40 instead. Net swing: -0.70 vs the exploit.

### 2. API Costs
**Problem**: Using an LLM API for student simulation would cost $40+ per training run.

**Solution**: Built a deterministic Python simulator that runs in <1ms per step, costs $0, and is 100% reproducible.

### 3. Memory Constraints
**Problem**: Qwen2.5-7B doesn't fit on free Colab T4 GPU (15GB VRAM).

**Solution**: 8-bit quantization + LoRA + gradient checkpointing. Reduced memory from 28GB to 12GB.

### 4. Data Leakage
**Problem**: Training and evaluating on the same scenarios would overestimate performance.

**Solution**: Strict train/eval split. Training code only imports `TRAINING_SCENARIOS`. Eval code only imports `EVAL_SCENARIOS`.

---

## What We Learned

### 1. Reward Design is Hard
We went through 5 iterations of the reward function before finding one that worked. The key insight: **you need to explicitly penalize exploits, not just reward good behavior**.

### 2. Deterministic Simulators are Powerful
Using a deterministic simulator instead of an LLM API made training:
- **200x faster** (<1ms vs 2-3 seconds per step)
- **Infinitely cheaper** ($0 vs $40+ per run)
- **100% reproducible** (same seed = same results)

### 3. Testing Matters
The 77-test suite caught bugs we would have missed. It also gave us confidence to iterate quickly.

### 4. Documentation is Presentation
Good documentation makes your work accessible. We spent as much time on the README as on the code.

---

## Future Work

### Short Term
1. **Scale to larger models** (Qwen2.5-7B, Llama-3-8B)
2. **More scenarios** (100+ across more domains)
3. **Multi-turn curriculum** (start with 5 turns, increase to 15)
4. **Human evaluation** (real students, not simulated)

### Long Term
1. **Deploy as a real tutoring system**
2. **Extend to other teaching methods** (analogies, examples, hints)
3. **Multi-agent scenarios** (multiple students, peer learning)
4. **Cross-lingual support** (teach in multiple languages)

---

## Acknowledgments

Built for the **OpenEnv Hackathon 2026** (Theme #4: Self-Improvement, Snorkel AI sub-theme: Changing Requirements).

**Technologies**: Meta OpenEnv, Hugging Face TRL, PyTorch, FastAPI, Docker

**Inspiration**: Socrates, who taught us 2,400 years ago that the best teachers ask questions, not give answers.

---

## Links

- **Live Environment**: [HuggingFace Space](https://huggingface.co/spaces/aneek2007/socratic-rl)
- **Trained Model**: [HuggingFace Hub](https://huggingface.co/aneek2007/socratic-rl-agent)
- **Source Code**: [GitHub](https://github.com/aneek22112007-tech/SocraticRL)
- **Training Notebook**: [Colab-ready](https://github.com/aneek22112007-tech/SocraticRL/blob/main/train_fixed_final.ipynb)

---

## Try It Now

1. **Visit the Space**: https://huggingface.co/spaces/aneek2007/socratic-rl
2. **Test the API**: Click "View API" to see the OpenEnv endpoints
3. **Run an episode**: Use the `/reset` and `/step` endpoints
4. **See the reward breakdown**: Each step returns detailed feedback

**Or clone and run locally**:
```bash
git clone https://github.com/aneek22112007-tech/SocraticRL
cd SocraticRL
pip install openenv-core fastapi uvicorn scikit-learn
python server/environment.py
```

---

## Questions?

Open an issue on [GitHub](https://github.com/aneek22112007-tech/SocraticRL/issues) or reach out via the HuggingFace Space discussions.

**Let's teach AI to teach.** 🦉

---

*Built in 48 hours for OpenEnv Hackathon 2026*  
*Theme: Self-Improvement | Sub-theme: Changing Requirements*  
*Powered by Meta OpenEnv, HuggingFace, and PyTorch*
