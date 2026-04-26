# HuggingFace Space Deployment Guide

## Quick Deploy (5 minutes)

### Step 1: Create HuggingFace Space

1. Go to https://huggingface.co/new-space
2. Fill in:
   - **Space name**: `socratic-rl`
   - **License**: MIT
   - **Space SDK**: Docker
   - **Visibility**: Public

### Step 2: Push Code to Space

```bash
# Clone your Space repo
git clone https://huggingface.co/spaces/aneek22112007-tech/socratic-rl
cd socratic-rl

# Copy all files from SocraticRL repo
cp -r ../SocraticRL/* .

# Add, commit, push
git add .
git commit -m "Initial deployment"
git push
```

### Step 3: Verify Deployment

- Space will build automatically (takes 2-3 minutes)
- Check logs at: https://huggingface.co/spaces/aneek22112007-tech/socratic-rl/logs
- Test API at: https://aneek22112007-tech-socratic-rl.hf.space/docs

## Alternative: Use OpenEnv CLI

```bash
# Install OpenEnv CLI
pip install openenv

# Login to HuggingFace
huggingface-cli login

# Push environment
openenv push --name socratic-rl --org aneek22112007-tech
```

## Verify It Works

```bash
# Test locally first
python server/app.py

# Test remote Space
curl https://aneek22112007-tech-socratic-rl.hf.space/health
```

## Update README After Deployment

Replace in README.md:
- Space URL: https://huggingface.co/spaces/aneek22112007-tech/socratic-rl
- Model URL: https://huggingface.co/aneek22112007-tech/socratic-rl-agent
- WandB URL: (get from your training run)

## Troubleshooting

**Build fails?**
- Check Dockerfile exists
- Check requirements.txt has all dependencies
- Check server/app.py imports work

**API not responding?**
- Check port 8000 in openenv.yaml
- Check FastAPI app is created correctly
- Check logs for errors
