# How to Train SocraticRL

## What you need
- A Google account (for Colab)
- A HuggingFace account (free) — to save the model
- A Weights & Biases account (free) — to watch training live
- ~30 minutes on a free Colab T4 GPU

---

## Step 1 — Open the notebook in Colab

Go to: https://colab.research.google.com  
File → Upload notebook → select `train_grpo.ipynb`

Then: Runtime → Change runtime type → **T4 GPU** → Save

---

## Step 2 — Set your secrets (one time)

In Colab, click the 🔑 key icon on the left sidebar and add:

| Secret name     | Value                          |
|-----------------|-------------------------------|
| `HF_TOKEN`      | Your HuggingFace write token  |
| `WANDB_API_KEY` | Your W&B API key              |
| `HF_USERNAME`   | Your HuggingFace username     |

Then add this at the top of Cell 1 (before the pip install):
```python
from google.colab import userdata
import os
os.environ["HF_TOKEN"]      = userdata.get("HF_TOKEN")
os.environ["WANDB_API_KEY"] = userdata.get("WANDB_API_KEY")
os.environ["HF_USERNAME"]   = userdata.get("HF_USERNAME")

from huggingface_hub import login
login(token=os.environ["HF_TOKEN"])
```

---

## Step 3 — Clone the repo inside Colab

Run this in a new cell at the very top:
```python
!git clone https://github.com/aneek22112007-tech/SocraticRL
%cd SocraticRL
```

---

## Step 4 — Run all cells in order

| Cell | What it does | Time |
|------|-------------|------|
| 1 | Install packages | ~3 min |
| 2 | Load Qwen2.5-7B in 4-bit (Unsloth) | ~4 min |
| 3 | Sanity-check reward function | <5 sec |
| 4 | Build training dataset (~1000 prompts) | <10 sec |
| 5 | Wire up reward function + GRPO trainer | <10 sec |
| 6 | **Run training — 3 epochs** | ~20 min |
| 7 | Save + push to HuggingFace Hub | ~3 min |

---

## Step 5 — Watch training on W&B

Go to https://wandb.ai → your project `socratic-rl-training`

You should see:
- `mean_reward` climbing from ~-1.8 toward ~+1.4
- `success_rate` climbing from ~3% toward ~60%

If `mean_reward` is stuck below -1.0 after 50 steps, the model is still
giving direct answers. This is normal — it usually breaks through around
step 80-120.

---

## Step 6 — Run evaluation

After training finishes, run in Colab:
```bash
python eval.py --model_path ./socratic-agent-final --n_episodes 30
```

Expected output:
```
Baseline
  success_rate: 0.033
  avg_final_understanding: 0.210

Trained Model
  success_rate: 0.610
  avg_final_understanding: 0.871

Delta (model - baseline)
  success_rate             +0.577
  avg_final_understanding  +0.661
```

---

## Step 7 — Connect the trained model to the HF Space

In your HuggingFace Space settings, add these secrets:

| Variable        | Value                                    |
|-----------------|------------------------------------------|
| `OPENAI_API_KEY`| Your OpenAI key (or use HF Inference)   |
| `LLM_MODEL`     | `your-username/socratic-rl-agent`        |
| `OPENAI_BASE_URL`| `https://api-inference.huggingface.co/v1`|

The demo will now use your trained model instead of fallback templates.

---

## Troubleshooting

**Out of memory on T4**
- Reduce `per_device_train_batch_size` to 1
- Reduce `max_completion_length` to 64

**`ModuleNotFoundError: reward`**
- Make sure you ran `%cd SocraticRL` before the training cells

**Training reward not improving after 200 steps**
- Try lowering `learning_rate` to `2e-6`
- Check W&B — if `direct_answer_rate` is still high, the model needs more steps

**Push to Hub fails**
- Run `huggingface-cli login` and paste your write token
