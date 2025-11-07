# Directory Reorganization Plan

## Current Issues
- Visualizations scattered across validation/interactive
- No clear separation between analysis outputs and presentation materials
- Documentation mixed with code
- No easy way to showcase results to others

## Proposed Structure

```
voting simulator/
├── README.md                          # Main project overview
├── requirements.txt                   # Dependencies
├── simulate.py                        # Main entry point
│
├── uvpd/                              # Source code (unchanged)
│   ├── __init__.py
│   ├── preference.py
│   ├── rules.py
│   ├── engine.py
│   ├── recorder.py
│   ├── stats.py
│   ├── visualize.py
│   ├── visualize_interactive.py
│   └── cli.py
│
├── data/                              # Raw simulation data
│   ├── raw/                           # Individual run JSON files
│   │   └── run_XXXX.json (1000 files)
│   └── processed/                      # ML-ready processed data
│       ├── features.npy
│       ├── labels.npy
│       └── metadata.json
│
├── analysis/                          # Statistical analysis outputs
│   ├── validation/                   # Randomness and correctness tests
│   │   ├── uniform_10k.json
│   │   ├── uniform_1M.json
│   │   ├── pairwise.json
│   │   └── independence.json
│   └── aggregate_stats.json          # Summary statistics
│
├── visualizations/                    # All visualization outputs
│   ├── static/                       # Static PNG images
│   │   ├── winner_evolution.png
│   │   ├── winner_distribution.png
│   │   ├── rule_agreement_heatmap.png
│   │   ├── winner_changes.png
│   │   └── condorcet_rate.png
│   │
│   └── interactive/                  # Interactive HTML plots
│       ├── winner_evolution_interactive.html
│       ├── winner_aggregation_interactive.html
│       ├── winner_distribution_interactive.html
│       ├── rule_agreement_heatmap_interactive.html
│       ├── winner_changes_interactive.html
│       ├── condorcet_rate_interactive.html
│       └── dashboard.html
│
├── docs/                              # Documentation
│   ├── EXPERIMENT_DESCRIPTION.md      # Scientific explanation
│   ├── VISUALIZATION_GUIDE.md        # How to interpret plots
│   ├── API_REFERENCE.md               # Code documentation
│   └── RESULTS_SUMMARY.md            # Key findings
│
└── presentation/                      # Ready-to-present materials
    ├── overview.html                  # Main presentation page
    ├── figures/                       # High-res versions for papers
    │   └── (exported from interactive plots)
    └── README.md                      # How to use presentation materials
```

## Migration Steps

### Step 1: Create New Directory Structure
```bash
mkdir -p analysis/validation
mkdir -p visualizations/static
mkdir -p visualizations/interactive
mkdir -p docs
mkdir -p presentation/figures
```

### Step 2: Move Files
- Move `data/validation/*.json` → `analysis/validation/`
- Move `data/validation/aggregate_stats.json` → `analysis/`
- Move `data/validation/*.png` → `visualizations/static/`
- Move `data/validation/interactive/*.html` → `visualizations/interactive/`
- Move `data/validation/interactive/*.png` → `visualizations/static/` (or keep in interactive)

### Step 3: Update Code References
- Update `uvpd/recorder.py` to use new paths
- Update `uvpd/visualize.py` to use new paths
- Update `uvpd/visualize_interactive.py` to use new paths
- Update `uvpd/stats.py` to use new paths
- Update `uvpd/cli.py` to use new paths

### Step 4: Create Documentation
- Create `docs/EXPERIMENT_DESCRIPTION.md` (from our earlier explanation)
- Create `docs/VISUALIZATION_GUIDE.md` (how to read each plot)
- Create `presentation/overview.html` (index page linking to all visualizations)

### Step 5: Update README
- Update paths in README.md
- Add links to documentation
- Add quick start guide

## Benefits
1. **Clear separation**: Data, analysis, visualizations, docs are distinct
2. **Easy presentation**: `presentation/` folder ready to share
3. **Better navigation**: Logical grouping by purpose
4. **Professional structure**: Follows common scientific project layouts
5. **Scalable**: Easy to add more analysis or visualization types

## Alternative: Keep Current Structure
If reorganization is too disruptive, we could:
- Add README files in each subdirectory explaining contents
- Create a `presentation/` folder that symlinks/copies key files
- Add an index.html that organizes access to visualizations

