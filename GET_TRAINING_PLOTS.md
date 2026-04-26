# 📊 How to Get Your Training Plots (5 Minutes)

## Method 1: From WandB (Recommended)

### Step 1: Find Your WandB Run

1. **Go to**: https://wandb.ai/
2. **Login** with your account
3. **Look for project**: `socratic-rl-training`
4. **Click on run**: `simple-training-run`

### Step 2: Download Charts

1. **Click on "Charts" tab** (left sidebar)
2. **Find the "loss" chart**
3. **Click the download icon** (⬇️) in the top right of the chart
4. **Save as**: `training_loss.png`
5. **If there's a "reward" chart**, download it too as `reward_curve.png`

### Step 3: Add to Your Repo

```bash
# In your terminal:
cd ~/Desktop/SocraticRL

# Create results folder if it doesn't exist
mkdir -p results

# Move your downloaded plots there
mv ~/Downloads/training_loss.png results/
mv ~/Downloads/reward_curve.png results/  # if you have it

# Commit and push
git add results/
git commit -m "Add real training plots from WandB"
git push origin main
```

---

## Method 2: From Colab (If WandB doesn't work)

### Add this as Cell 8 in your Colab:

```python
# ═══════════════════════════════════════════════════════════════
# CELL 8: Download Training Plots
# ═══════════════════════════════════════════════════════════════

import matplotlib.pyplot as plt
import wandb

print("Fetching training data from WandB...")

# Get the current run
run = wandb.run

# Get training history
history = run.history()

# Plot 1: Training Loss
if 'loss' in history.columns:
    plt.figure(figsize=(10, 6))
    plt.plot(history['step'], history['loss'], linewidth=2.5, color='#1D9E75')
    plt.xlabel('Training Step', fontsize=12)
    plt.ylabel('Loss', fontsize=12)
    plt.title('SocraticRL - Training Loss', fontsize=14, fontweight='bold')
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig('training_loss.png', dpi=150, bbox_inches='tight')
    print("✅ Saved training_loss.png")
    plt.show()
    
    # Download the file
    from google.colab import files
    files.download('training_loss.png')

# Plot 2: Reward Curve (if available)
if 'reward' in history.columns:
    plt.figure(figsize=(10, 6))
    plt.plot(history['step'], history['reward'], linewidth=2.5, color='#FF6B6B')
    plt.xlabel('Training Step', fontsize=12)
    plt.ylabel('Mean Reward', fontsize=12)
    plt.title('SocraticRL - Reward Curve', fontsize=14, fontweight='bold')
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig('reward_curve.png', dpi=150, bbox_inches='tight')
    print("✅ Saved reward_curve.png")
    plt.show()
    
    # Download the file
    files.download('reward_curve.png')

print(f"\n📊 WandB Run URL: {run.url}")
print("\n✅ Download complete! Add these plots to your repo.")
```

**Then run this cell and it will download the plots for you!**

---

## Method 3: Quick Screenshot (Fastest - 2 minutes)

If you're really short on time:

1. **Go to your WandB run**: https://wandb.ai/
2. **Take a screenshot** of the loss chart
3. **Save as**: `training_loss.png`
4. **Add to repo**:
   ```bash
   cd ~/Desktop/SocraticRL
   mkdir -p results
   # Move your screenshot to results/
   git add results/training_loss.png
   git commit -m "Add training loss screenshot"
   git push origin main
   ```

---

## What to Do After You Have the Plots

### Update README.md

Find this section in your README:

```markdown
### Reward curve

![Reward curve](outputs/reward_curve.svg)
```

**Replace with**:

```markdown
### Training Loss

![Training Loss](results/training_loss.png)

*Training loss over 300 steps using GRPO with 50 scenarios.*

### WandB Run

Full training logs: [View on WandB](YOUR_WANDB_URL_HERE)
```

### Commit and Push

```bash
git add README.md
git commit -m "Update README with real training plots"
git push origin main
```

---

## 🎯 This Will Give You:

**Training Evidence: 18/20** (instead of 10/20)

**Total Score: 64/100** (instead of 56/100)

**Time Required: 5 minutes**

---

## ⚡ FASTEST PATH (Right Now):

1. **In your Colab**: Add Cell 8 code above and run it
2. **Download** the plots that appear
3. **Move to** `~/Desktop/SocraticRL/results/`
4. **Run**:
   ```bash
   cd ~/Desktop/SocraticRL
   git add results/
   git commit -m "Add training plots"
   git push origin main
   ```

**DONE!** ✅

---

## 📝 Your WandB URL

Look in your Colab output for a line like:
```
📊 W&B Dashboard: https://wandb.ai/YOUR_USERNAME/socratic-rl-training/runs/...
```

Copy that URL and add it to your README!
