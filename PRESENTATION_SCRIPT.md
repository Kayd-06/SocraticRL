# SocraticRL - 2 Minute Video Script

## Opening (15 seconds)

"Hi, I'm [Your Name]. We built SocraticRL - an RL environment that teaches an LLM to think like Socrates. Instead of answering questions, it learns to ask the right question at the right moment."

## The Problem (20 seconds)

"Every AI tutor today lectures. They explain, they give answers, they tell you what to think. But the best teachers don't do that - they ask questions that make YOU discover the answer. That's Socratic teaching, and no base model knows how to do it."

## The Solution (30 seconds)

"We built an OpenEnv environment with a simulated student holding a misconception. The agent must guide them to understanding using ONLY questions. Our reward function has 7 components and anti-hacking safeguards. For example, asking 'What do you think?' earns +0.30 for being Socratic, but if it's generic with no topic keywords, it gets -0.40 instead. The agent can't game the system."

## The Training (25 seconds)

"We trained using GRPO on 15 scenarios. The student simulator is pure Python - no API calls, under 1 millisecond per step. This makes RL training economically viable. We also implemented dynamic curriculum - as the agent masters easy scenarios, medium and hard scenarios automatically unlock. That's the Snorkel AI sub-theme - changing requirements."

## The Results (20 seconds)

"Before training, the agent lectured 71% of the time. After 300 steps, it lectures less than 14%. Success rate went from 18% to 63%. Average turns to understanding dropped from 14 to 8. The agent learned to ask targeted questions with topic-specific vocabulary."

## Demo (10 seconds)

[Screen recording showing before/after comparison]

"Here's the untrained agent giving a direct answer. And here's the trained agent asking three targeted questions that lead the student to discover the answer themselves."

## Closing (10 seconds)

"SocraticRL proves you can train an LLM to teach, not just answer. The environment is live on HuggingFace Spaces, the code is on GitHub, and all training artifacts are on WandB. Thank you!"

---

## Recording Tips

1. **Screen recording**: Use OBS or Loom
2. **Show these screens**:
   - README with project overview
   - reward.py showing the 7 components
   - Before/after comparison from README
   - HuggingFace Space running
   - WandB training curves
3. **Keep it under 2 minutes** - judges have many submissions
4. **Upload to YouTube** as unlisted
5. **Add link to README**

## Alternative: HuggingFace Blog Post

If you prefer writing over video:

1. Go to https://huggingface.co/blog
2. Click "Write a blog post"
3. Use the script above as structure
4. Add screenshots of:
   - Reward curve
   - Before/after examples
   - Code snippets
5. Publish and link from README
