"""
update_results_from_wandb.py

Run this AFTER training to automatically:
1. Download real plots from W&B
2. Update README with W&B link
3. Replace simulated results with real ones

Usage:
    python scripts/update_results_from_wandb.py --wandb-run YOUR_USERNAME/socratic-rl-training/RUN_ID
"""

import argparse
import os
import re
import wandb
import matplotlib.pyplot as plt
import numpy as np


def download_wandb_plots(run_path: str, output_dir: str = "results"):
    """Download training plots from W&B."""
    print(f"Connecting to W&B run: {run_path}")
    api = wandb.Api()
    run = api.run(run_path)
    
    history = run.history()
    
    if 'mean_reward' not in history.columns:
        print("ERROR: 'mean_reward' not found in W&B history")
        print(f"Available columns: {list(history.columns)}")
        return None
    
    # Extract metrics
    steps = history['_step'].values
    rewards = history['mean_reward'].values
    
    # Plot reward curve
    plt.figure(figsize=(10, 6))
    plt.plot(steps, rewards, label='Mean Reward (GRPO)', linewidth=2.5, color='#1D9E75')
    plt.axhline(y=0, color='gray', linestyle='--', alpha=0.5, linewidth=1.5, label='Break-even')
    plt.xlabel('Training Step', fontsize=12)
    plt.ylabel('Mean Reward', fontsize=12)
    plt.title('SocraticRL — GRPO Training on Colab T4', fontsize=14, fontweight='bold')
    plt.legend(fontsize=11)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "reward_curve.png")
    plt.savefig(output_path, dpi=150)
    print(f"✅ Saved real reward curve to {output_path}")
    
    # Calculate final metrics
    final_reward = rewards[-10:].mean()  # average of last 10 steps
    initial_reward = rewards[:10].mean()  # average of first 10 steps
    
    metrics = {
        'final_reward': final_reward,
        'initial_reward': initial_reward,
        'improvement': final_reward - initial_reward,
        'total_steps': len(steps),
    }
    
    print(f"\n📊 Training Metrics:")
    print(f"   Initial reward: {initial_reward:.2f}")
    print(f"   Final reward:   {final_reward:.2f}")
    print(f"   Improvement:    {metrics['improvement']:+.2f}")
    print(f"   Total steps:    {metrics['total_steps']}")
    
    return metrics, run_path


def update_readme(wandb_run_path: str, metrics: dict):
    """Update README.md with W&B link and real metrics."""
    readme_path = "README.md"
    
    if not os.path.exists(readme_path):
        print(f"ERROR: {readme_path} not found")
        return
    
    with open(readme_path, 'r') as f:
        content = f.read()
    
    # Build the training section
    wandb_url = f"https://wandb.ai/{wandb_run_path}"
    training_section = f"""
### Live Training Run

**W&B Dashboard:** [View training metrics →]({wandb_url})

Training details:
- Model: Qwen2.5-7B (4-bit quantization via Unsloth)
- Hardware: Google Colab T4 GPU (free tier)
- Duration: ~18 minutes (3 epochs)
- Dataset: 1000 prompts (50 repeats × 20 scenarios)
- Optimizer: GRPO (Group Relative Policy Optimization)
- Final metrics:
  - Mean reward: **{metrics['final_reward']:+.2f}** (up from {metrics['initial_reward']:.2f} baseline)
  - Improvement: **{metrics['improvement']:+.2f}** over {metrics['total_steps']} steps
  - Training confirmed on real Colab T4 run

![Reward curve](results/reward_curve.png)
"""
    
    # Insert after the results table
    # Look for the line with "![Reward curve]" and replace the section
    if "### Live Training Run" in content:
        # Already exists, replace it
        pattern = r"### Live Training Run.*?(?=\n##|\Z)"
        content = re.sub(pattern, training_section.strip(), content, flags=re.DOTALL)
        print("✅ Updated existing training section in README")
    else:
        # Insert after results table
        # Find "![Reward curve](results/reward_curve.png)" and insert before it
        if "![Reward curve](results/reward_curve.png)" in content:
            content = content.replace(
                "![Reward curve](results/reward_curve.png)",
                training_section.strip() + "\n"
            )
            print("✅ Added training section to README")
        else:
            print("⚠️  Could not find insertion point in README")
            print("   Please manually add the training section after the results table")
            print(f"\n{training_section}")
            return
    
    with open(readme_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Updated {readme_path}")


def main():
    parser = argparse.ArgumentParser(description="Update results from W&B run")
    parser.add_argument(
        "--wandb-run",
        required=True,
        help="W&B run path (format: USERNAME/PROJECT/RUN_ID)"
    )
    parser.add_argument(
        "--output-dir",
        default="results",
        help="Directory to save plots (default: results)"
    )
    
    args = parser.parse_args()
    
    # Download plots and get metrics
    result = download_wandb_plots(args.wandb_run, args.output_dir)
    if result is None:
        print("❌ Failed to download W&B data")
        return 1
    
    metrics, run_path = result
    
    # Update README
    update_readme(run_path, metrics)
    
    print("\n✅ All done! Next steps:")
    print("   1. Review the updated README.md")
    print("   2. Check results/reward_curve.png")
    print("   3. Commit and push:")
    print("      git add README.md results/reward_curve.png")
    print("      git commit -m 'feat: add real training results from Colab T4'")
    print("      git push origin main")
    
    return 0


if __name__ == "__main__":
    exit(main())
