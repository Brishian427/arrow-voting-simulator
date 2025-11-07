# Push to GitHub - Quick Guide

## Step 1: Create Repository on GitHub

1. Go to: https://github.com/new
2. Repository name: **arrow-voting-simulator**
3. Description: "Progressive election simulation with multiple voting rules (Plurality, Borda, Condorcet, IRV)"
4. Choose **Public** or **Private**
5. **IMPORTANT**: Do NOT check "Initialize with README" or add .gitignore/license (we already have these)
6. Click **"Create repository"**

## Step 2: Push Your Code

After creating the repository, run these commands:

```bash
cd "D:\Desktop\Nucleus\Universal Voting Dictator"
git push -u origin main
```

If prompted for credentials:
- Username: `Brishian427`
- Password: Use a **Personal Access Token** (not your GitHub password)
  - Create one at: https://github.com/settings/tokens
  - Select scopes: `repo` (full control)

## Step 3: Verify

Check your repository at:
**https://github.com/Brishian427/arrow-voting-simulator**

You should see:
- ✅ Source code (`uvpd/` folder)
- ✅ Documentation (`docs/` folder)
- ✅ README.md
- ✅ requirements.txt
- ✅ All configuration files

## Repository Info

- **Name**: arrow-voting-simulator
- **URL**: https://github.com/Brishian427/arrow-voting-simulator
- **Remote**: Already configured ✓
- **Branch**: main ✓

