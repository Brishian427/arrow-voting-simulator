# GitHub Setup Instructions

## Repository Initialized

Git repository has been initialized. To connect to GitHub:

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `voting-simulator` (or your preferred name)
3. Description: "Progressive election simulation with multiple voting rules"
4. Choose Public or Private
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

## Step 2: Connect Local Repository to GitHub

After creating the repository, GitHub will show you commands. Use these:

```bash
cd "D:\Desktop\Nucleus\Universal Voting Dictator"
git remote add origin https://github.com/YOUR_USERNAME/voting-simulator.git
git branch -M main
git push -u origin main
```

Or if using SSH:
```bash
git remote add origin git@github.com:YOUR_USERNAME/voting-simulator.git
git branch -M main
git push -u origin main
```

## Step 3: Verify

Check that files are on GitHub:
- Source code (`uvpd/`)
- Documentation (`docs/`)
- README.md
- requirements.txt
- .gitignore

**Note**: Large data files (1000 JSON runs, visualizations) are excluded via `.gitignore` to keep the repository lightweight. These can be regenerated using the simulation commands.

## What's Included in Git

✅ Source code (`uvpd/`)
✅ Documentation (`docs/`)
✅ README and requirements
✅ CI workflow (`.github/workflows/ci.yml`)

## What's Excluded (via .gitignore)

❌ Generated data files (`data/raw/*.json`, `data/processed/*.npy`)
❌ Analysis outputs (can be regenerated)
❌ Visualizations (can be regenerated)
❌ Python cache files
❌ IDE files

## Future Commits

After making changes:
```bash
git add .
git commit -m "Description of changes"
git push
```

