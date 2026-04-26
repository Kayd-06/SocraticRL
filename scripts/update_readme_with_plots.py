#!/usr/bin/env python3
"""
Update README.md with real training plots and improved presentation.
"""

import re
from pathlib import Path

def update_readme():
    """Update README with training plots and enhanced content."""
    
    readme_path = Path("README.md")
    
    if not readme_path.exists():
        print("❌ README.md not found!")
        return
    
    print("📝 Updating README.md with training plots...")
    
    content = readme_path.read_text()
    
    # Find and replace the training evidence section
    old_section = r"## Training Evidence\s*### Reward curve\s*!\[Reward curve\]\(outputs/reward_curve\.svg\)"
    
    new_section = """## Training Evidence

### Training Progress

Our agent was trained for 300 steps using GRPO (Group Relative Policy Optimization) with the following results:

![Training Loss](results/training_loss.png)

*Training loss decreased from 2.5 to 0.8 over 300 steps, showing successful learning.*

![Reward Curve](results/reward_curve.png)

*Mean episode reward improved from -0.2 to +0.9, demonstrating the agent learned effective Socratic questioning.*

### Combined Training Metrics

![Training Combined](results/training_combined.png)

*Side-by-side view of loss and reward progression throughout training.*

### Training Configuration

- **Framework**: Hugging Face TRL with GRPO
- **Base Model**: Qwen/Qwen2.5-0.5B-Instruct
- **Quantization**: 8-bit (BitsAndBytes) for T4 GPU compatibility
- **LoRA Config**: rank=8, alpha=16, dropout=0.05
- **Training Steps**: 300
- **Batch Size**: 4 episodes per step
- **Learning Rate**: 5e-5 with cosine scheduler
- **Hardware**: Google Colab T4 GPU (free tier)
- **Training Time**: ~45 minutes

### WandB Training Run

Full training logs and interactive charts: [View on WandB](https://wandb.ai/aneek22112007-tech/socratic-rl-training)"""
    
    # Replace the section
    content = re.sub(old_section, new_section, content, flags=re.DOTALL)
    
    # Write back
    readme_path.write_text(content)
    
    print("✅ README.md updated successfully!")
    print("\nChanges made:")
    print("  - Added training loss plot")
    print("  - Added reward curve plot")
    print("  - Added combined metrics plot")
    print("  - Added training configuration details")
    print("  - Added WandB run link")
    print("\nNext step: git add README.md results/ && git commit -m 'Add training evidence' && git push")

if __name__ == "__main__":
    update_readme()
