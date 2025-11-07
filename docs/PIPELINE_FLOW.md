# Data Generation Pipeline Flow

This document explains the complete simulation pipeline and how files are organized.

## Pipeline Stages

### Stage 1: Validation (`python simulate.py validate`)
**Purpose**: Verify the preference generator produces truly random, unbiased data

**Outputs**:
- `analysis/validation/uniform_10k.json` - Chi-square test on 10,000 samples
- `analysis/validation/uniform_1M.json` - Chi-square test on 1,000,000 samples  
- `analysis/validation/pairwise.json` - Pairwise candidate preference balance
- `analysis/validation/independence.json` - Independence across runs

**What it tests**:
- All 120 rankings appear equally often (uniformity)
- Each candidate pair has ~50/50 preference split (balance)
- Consecutive runs are independent (no correlation)

---

### Stage 2: Small Test (`python simulate.py small`)
**Purpose**: Quick sanity check before full generation

**Outputs**:
- `data/raw/run_0001.json` through `run_0010.json`
- Each file contains 50 steps (50 voters per run)

**Use case**: Verify the simulation works correctly before running the full dataset

---

### Stage 3: Full Generation (`python simulate.py full`)
**Purpose**: Generate the complete dataset for ML training

**Outputs**:
- `data/raw/run_0001.json` through `run_1000.json`
- Each file contains 500 steps (500 voters per run)
- Total: 500,000 election states (1000 runs × 500 steps)

**File structure**: Each `run_XXXX.json` is a JSON array:
```json
[
  {"run_id": 1, "step": 1, "voter_preferences": [...], "winners": {...}},
  {"run_id": 1, "step": 2, "voter_preferences": [...], "winners": {...}},
  ...
  {"run_id": 1, "step": 500, "voter_preferences": [...], "winners": {...}}
]
```

**Features**:
- Resume capability: Skips existing runs if interrupted
- Progressive recording: Records after each voter addition
- Memory efficient: Writes incrementally to disk

---

### Stage 4: Post-Processing (`python simulate.py post`)
**Purpose**: Compute aggregate statistics and extract ML features

**Outputs**:
- `analysis/aggregate_stats.json` - Summary statistics:
  - Condorcet winner rate by voter count
  - Rule agreement frequencies
  - Winner volatility metrics
- `data/processed/features.npy` - ML input features (1000 samples × 10 features)
  - Features: [plurality_counts(5) + borda_scores(5)]
- `data/processed/labels.npy` - ML target labels (1000 samples × 4 labels)
  - Labels: [plurality_winner, borda_winner, condorcet_winner, irv_winner]
- `data/processed/metadata.json` - Data format documentation

---

### Stage 5: Visualization - Static (`python simulate.py visualize`)
**Purpose**: Generate static PNG plots for papers/presentations

**Outputs** (in `visualizations/static/`):
- `winner_evolution.png` - Winner changes across example runs
- `winner_distribution.png` - Winner frequency by candidate and rule
- `rule_agreement_heatmap.png` - Agreement matrix between rules
- `winner_changes.png` - Change frequency over voter count
- `condorcet_rate.png` - Condorcet winner existence rate

---

### Stage 6: Visualization - Interactive (`python simulate.py visualize-interactive`)
**Purpose**: Generate interactive HTML plots for exploration

**Outputs** (in `visualizations/interactive/`):
- `winner_evolution_interactive.html` - Zoom, hover, explore winner evolution
- `winner_aggregation_interactive.html` - Winner distribution across all runs by voter count
- `winner_distribution_interactive.html` - Interactive bar charts
- `rule_agreement_heatmap_interactive.html` - Interactive heatmap
- `winner_changes_interactive.html` - Interactive change frequency
- `condorcet_rate_interactive.html` - Interactive Condorcet rate
- `dashboard.html` - Combined dashboard view

**Features**:
- Zoom and pan
- Hover tooltips with detailed information
- Toggle series visibility
- Export to PNG

---

## Directory Structure

```
voting simulator/
├── data/                           # Core simulation data
│   ├── raw/                        # Individual run JSON files
│   │   └── run_XXXX.json          # 1000 files (one per run)
│   └── processed/                  # ML-ready processed data
│       ├── features.npy
│       ├── labels.npy
│       └── metadata.json
│
├── analysis/                       # Statistical analysis outputs
│   ├── validation/                # Randomness validation tests
│   │   ├── uniform_10k.json
│   │   ├── uniform_1M.json
│   │   ├── pairwise.json
│   │   └── independence.json
│   └── aggregate_stats.json       # Summary statistics
│
├── visualizations/                 # All visualization outputs
│   ├── static/                    # Static PNG images
│   └── interactive/               # Interactive HTML plots
│
└── uvpd/                          # Source code
    ├── preference.py              # Preference generation
    ├── rules.py                   # Voting rule implementations
    ├── engine.py                  # Simulation engine
    ├── recorder.py                # Data recording
    ├── stats.py                   # Statistical analysis
    ├── visualize.py               # Static visualization
    ├── visualize_interactive.py   # Interactive visualization
    └── cli.py                     # Command-line interface
```

## Typical Workflow

1. **First Time Setup**:
   ```bash
   pip install -r requirements.txt
   python simulate.py validate --quick
   python simulate.py small --seed 42
   ```

2. **Full Dataset Generation**:
   ```bash
   python simulate.py full --seed 42
   ```

3. **Analysis and Visualization**:
   ```bash
   python simulate.py post
   python simulate.py visualize
   python simulate.py visualize-interactive
   ```

4. **Explore Results**:
   - Open `visualizations/interactive/*.html` in browser
   - Check `analysis/aggregate_stats.json` for key metrics
   - Review `visualizations/static/*.png` for static figures

## File Naming Conventions

- **Run files**: `run_XXXX.json` where XXXX is zero-padded run number (0001-1000)
- **Step numbers**: Within each file, steps are 1-500 (representing voter count)
- **Validation files**: Descriptive names indicating test type and sample size
- **Visualization files**: Descriptive names indicating plot type and format

## Key Points

- **Data flow**: Validation → Generation → Post-processing → Visualization
- **Resumability**: Full generation can be interrupted and resumed (skips existing runs)
- **Reproducibility**: All stages accept `--seed` for deterministic results
- **Scalability**: Memory-efficient incremental writing for large datasets

