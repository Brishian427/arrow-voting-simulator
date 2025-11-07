# Data Directory

This directory stores simulation data and processed outputs.

## Structure

- `raw/` - Individual simulation run JSON files (created when running `python simulate.py full`)
  - Files: `run_0001.json`, `run_0002.json`, ... `run_1000.json`
  - Each file contains progressive election states from 1 to N voters

- `processed/` - ML-ready processed data (created when running `python simulate.py post`)
  - `features.npy` - Input features for machine learning
  - `labels.npy` - Target labels (winners)
  - `metadata.json` - Data format documentation

## Generation

These directories and files are automatically created when you run:
- `python simulate.py small` or `python simulate.py full` → Creates `data/raw/`
- `python simulate.py post` → Creates `data/processed/`

**Note**: Raw data files are excluded from git via `.gitignore` as they are large and can be regenerated.

