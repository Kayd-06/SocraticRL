# SocraticRL Hackathon Submission Checklist

## ✅ CRITICAL (Must Have - Non-Negotiable)

### 1. HuggingFace Space Deployment
- [ ] Create Space at https://huggingface.co/new-space
- [ ] Push code to Space
- [ ] Verify Space builds successfully
- [ ] Test API endpoint works
- [ ] Update README with correct Space URL

### 2. Training Evidence
- [ ] Training completed successfully
- [ ] Download loss curve from WandB
- [ ] Download reward curve from WandB
- [ ] Save plots as PNG files
- [ ] Add plots to `results/` folder
- [ ] Update README with real plots (not mock)
- [ ] Add WandB run link to README

### 3. Trained Model
- [ ] Model pushed to HuggingFace Hub
- [ ] Verify model page exists
- [ ] Update README with correct model URL

### 4. Presentation (30% of score!)
- [ ] Record 2-minute video OR write blog post
- [ ] Upload video to YouTube (unlisted is fine)
- [ ] Add presentation link to README
- [ ] Verify link works

### 5. README Quality
- [ ] Problem motivation clear
- [ ] Environment explanation clear
- [ ] Results section has real data
- [ ] All links work (no YOUR_USERNAME placeholders)
- [ ] Plots embedded and visible
- [ ] Quick start instructions work

## ✅ IMPORTANT (Strongly Recommended)

### 6. Code Quality
- [ ] All tests pass (`python reward.py`)
- [ ] Environment smoke test works (`python server/environment.py`)
- [ ] No broken imports
- [ ] requirements.txt complete

### 7. Documentation
- [ ] openenv.yaml valid
- [ ] Dockerfile exists (if using Docker SDK)
- [ ] Training notebook runs end-to-end
- [ ] eval.py works on held-out scenarios

### 8. Repository Cleanup
- [ ] Remove .kiro/ folder (already done ✅)
- [ ] Remove old broken notebooks (already done ✅)
- [ ] Exclude PDF from commits (already done ✅)
- [ ] No large files (videos should be YouTube links)

## ✅ NICE TO HAVE (Bonus Points)

### 9. Advanced Features
- [ ] Dynamic curriculum working
- [ ] Eval script shows before/after comparison
- [ ] Multiple training runs documented
- [ ] Ablation studies (optional)

### 10. Presentation Quality
- [ ] Video has screen recording
- [ ] Video shows before/after demo
- [ ] Video shows training curves
- [ ] Clear audio quality

## 🚨 FINAL CHECKS BEFORE SUBMISSION

- [ ] Space URL submitted to hackathon form
- [ ] All links in README work
- [ ] Training plots are REAL (not mock)
- [ ] Video/blog post linked in README
- [ ] Submission before deadline: **April 26, 5 PM IST**

## Current Status

### ✅ Completed
- [x] Environment built
- [x] Reward function with anti-hacking
- [x] Student simulator
- [x] Training notebook created
- [x] README written
- [x] Eval script
- [x] Dynamic curriculum
- [x] requirements.txt
- [x] Deployment guide
- [x] Presentation script

### ⏳ In Progress
- [ ] Training running (wait for completion)

### ❌ Not Started
- [ ] HuggingFace Space deployment
- [ ] Video/blog post creation
- [ ] Update README with real results

## Time Estimate

- Deploy to HF Space: **10 minutes**
- Wait for training: **15-20 minutes** (already running)
- Download plots, update README: **5 minutes**
- Record video OR write blog: **30-45 minutes**
- Final testing: **10 minutes**

**Total: ~1.5 hours after training completes**

## Priority Order

1. **Deploy HF Space NOW** (while training runs)
2. **Wait for training to complete**
3. **Download plots, update README**
4. **Create video/blog post**
5. **Final submission**
