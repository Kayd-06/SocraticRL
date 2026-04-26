# 🚀 Teammate Training Guide — Train SocraticRL Model

This guide allows any teammate to train the SocraticRL model on Google Colab in **30 minutes**.

---

## 📋 Prerequisites

You need:
- Google account (for Colab)
- HuggingFace account (https://huggingface.co/signup)
- Weights & Biases account (https://wandb.ai/signup)

---

## 🎯 Quick Start (3 steps)

### **Step 1: Open Colab**
```
https://colab.research.google.com
```

### **Step 2: Upload notebook**
- Click **File → Upload notebook**
- Select **`train_improved_colab.ipynb`** from this repo
- This notebook has everything pre-configured

### **Step 3: Run all cells**
- Click **Runtime → Run all** (or Ctrl+F9)
- When prompted:
  - Paste HF token from https://huggingface.co/settings/tokens
  - Paste W&B API key from https://wandb.ai/authorize
- Wait ~25 minutes for training to complete
- Download `reward_curve_real.png`

---

## 📊 What the Notebook Does

**Cell 1:** Setup (clone repo, install packages, login)  
**Cell 2:** Load Qwen2.5-7B in 4-bit quantization  
**Cell 3:** Test reward function  
**Cell 4:** Build dataset (150 samples from 50 scenarios)  
**Cell 5:** Define GRPO reward function  
**Cell 6:** Train for 3 epochs  
**Cell 7:** Save model & push to HF Hub  
**Cell 8:** Download reward curve from W&B  

---

## 🔑 Getting Your Credentials

### HuggingFace Token
1. Go to https://huggingface.co/settings/tokens
2. Click **New token**
3. Name: `colab-training`
4. Type: **Write**
5. Copy the token

### W&B API Key
1. Go to https://wandb.ai/authorize
2. Copy your API key
3. Paste when prompted in Colab

---

## 📈 Expected Results

**Training should show:**
```
Step 5: mean_reward = -1.23
Step 20: mean_reward = -0.45
Step 50: mean_reward = +0.12
Step 100: mean_reward = +0.68
Step 150: mean_reward = +1.15 ✅
```

**Final metrics:**
- Initial mean_reward: ~-1.5
- Final mean_reward: ~+1.0 to +1.2
- Training time: ~20 minutes
- Total time: ~30 minutes

---

## 📁 Files You Need

These files are already in the repo:

```
train_improved_colab.ipynb          ← Upload this to Colab
students/scenarios_expanded.py      ← 50 training scenarios
reward.py                           ← Reward function
models.py                           ← Data models
students/simulator.py               ← Student simulator
```

---

## 🎓 What Gets Trained

The model learns to:
- ✅ Ask questions instead of statements
- ✅ Avoid direct answers
- ✅ Use topic-specific keywords
- ✅ Vary question structure
- ✅ Guide students Socratically

**Training data:** 150 samples across 50 scenarios (physics, math, biology, chemistry, logic)

---

## 🆘 Troubleshooting

### "ModuleNotFoundError: reward"
- Make sure Cell 1 ran successfully
- Check: `!pwd` should show `/content/SocraticRL`

### "Out of memory"
- In Cell 6, change:
  ```python
  per_device_train_batch_size=1,  # was 1, keep it
  gradient_accumulation_steps=2,  # reduce from 4
  ```

### "W&B not logging"
- Run this before Cell 5:
  ```python
  import wandb
  wandb.login(key="YOUR_API_KEY")
  ```

### Training is very slow
- Normal on free Colab T4
- Takes ~20 minutes for 3 epochs
- Don't interrupt

---

## 📊 After Training

### Download the plot
- Colab will auto-download `reward_curve_real.png`
- This shows your training progress

### Update the repo
```bash
cd SocraticRL
mv ~/Downloads/reward_curve_real.png results/reward_curve.png
git add results/reward_curve.png
git commit -m "feat: training run by [YOUR_NAME]"
git push origin main
```

### View W&B dashboard
- W&B link will print at the end
- Shows real-time metrics
- Share with team

---

## 🏆 Success Criteria

You're done when:
- ✅ Training completes without errors
- ✅ `reward_curve_real.png` is downloaded
- ✅ W&B dashboard shows reward climbing
- ✅ Model is pushed to HF Hub

---

## 💡 Pro Tips

1. **Run during off-peak hours** — Colab is faster at night
2. **Keep Colab tab open** — Don't close it during training
3. **Monitor W&B dashboard** — Watch metrics in real-time
4. **Save the W&B link** — Share with team for comparison
5. **Try different seeds** — Run multiple times for ensemble

---

## 📞 Questions?

If something breaks:
1. Check the error message
2. Look at troubleshooting section above
3. Restart runtime: **Runtime → Restart runtime**
4. Try again

---

## 🚀 Ready?

1. Open Colab: https://colab.research.google.com
2. Upload: `train_improved_colab.ipynb`
3. Run all cells
4. Wait 30 minutes
5. Download plot
6. Update repo

**Let's go! 🎯**
