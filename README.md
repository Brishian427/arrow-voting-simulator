# Arrow Voting Simulator

A comprehensive simulation system for progressive election analysis under multiple voting rules.

This project simulates rolling elections with 5 candidates (A–E), generating per-step outcomes for multiple voting rules to produce ML-ready datasets.

## Components
- Preference Generator: uniform permutations over 5 candidates.
- Voting Rules: Plurality, Borda (4-3-2-1-0), Condorcet, IRV/Hare.
- Progressive Engine: adds one voter at a time up to `n_max` per run.
- Data Recorder: writes per-run JSON in `data/raw`.
- Statistical Validator: randomness tests and aggregate analyses.
- Visualization Pipeline: generates static plots for winner evolution, distributions, rule agreement, and Condorcet rates.
- Interactive Visualization Pipeline: generates interactive Plotly plots in separate subfolder for zoom, hover, and exploration.

## Tiebreaking Rule
Deterministic alphabetical order (A < B < C < D < E). When scores tie, the lower index wins.

## Reproducibility
All runs can be seeded with `--seed`. Given the same seed, results are deterministic.

## Progressive Simulation Algorithm

The core algorithm accumulates voters progressively, recalculating winners at each step with all previous voters' preferences preserved:

```mermaid
flowchart TD
    Start([Start Simulation Run]) --> Init[Initialize: prefs_all = empty array<br/>step = 0]
    Init --> Check{step < max_voters?}
    
    Check -->|Yes| Generate[Generate 1 new preference<br/>Random permutation of candidates A-E]
    Generate --> Append[Append to prefs_all<br/>prefs_all = prefs_all + new_pref]
    Append --> Compute[Compute Winners with ALL preferences<br/>Plurality, Borda, Condorcet, IRV]
    
    Compute --> Record[Record State<br/>step, all voter_preferences, winners]
    Record --> Increment[step = step + 1]
    Increment --> Check
    
    Check -->|No| End([End Run])
    
    style Start fill:transparent,stroke:#424242,stroke-width:3px
    style End fill:transparent,stroke:#424242,stroke-width:3px
    style Init fill:transparent,stroke:#2196F3,stroke-width:2px,color:#1976D2
    style Generate fill:transparent,stroke:#4CAF50,stroke-width:2px,color:#388E3C
    style Append fill:transparent,stroke:#FF9800,stroke-width:2px,color:#F57C00
    style Compute fill:transparent,stroke:#9C27B0,stroke-width:2px,color:#7B1FA2
    style Record fill:transparent,stroke:#FBC02D,stroke-width:2px,color:#F9A825
    style Check fill:transparent,stroke:#607D8B,stroke-width:2px,color:#455A64
```

**Key Points:**
- Each step adds exactly **one new voter** to the accumulated set
- All **previous preferences are preserved** (never modified or removed)
- Winners are **recalculated from scratch** at each step using the full accumulated preference matrix
- This creates a progressive view of how winners change as more voters participate

## Pipeline Flow

```mermaid
flowchart TD
    Start([Start]) --> Validate[Validate Randomness<br/>python simulate.py validate]
    Validate --> ValOutput[analysis/validation/<br/>uniform_10k.json<br/>uniform_1M.json<br/>pairwise.json<br/>independence.json]
    
    ValOutput --> Small[Small Test<br/>python simulate.py small]
    Small --> SmallOutput[data/raw/<br/>run_0001.json to run_0010.json<br/>10 runs × 50 steps]
    
    SmallOutput --> Full[Full Generation<br/>python simulate.py full]
    Full --> FullOutput[data/raw/<br/>run_0001.json to run_1000.json<br/>1000 runs × 500 steps]
    
    FullOutput --> Post[Post-Processing<br/>python simulate.py post]
    Post --> PostOutput[analysis/aggregate_stats.json<br/>data/processed/<br/>features.npy, labels.npy]
    
    PostOutput --> VizStatic[Static Visualization<br/>python simulate.py visualize]
    VizStatic --> StaticOutput[visualizations/static/<br/>*.png files]
    
    PostOutput --> VizInteractive[Interactive Visualization<br/>python simulate.py visualize-interactive]
    VizInteractive --> InteractiveOutput[visualizations/interactive/<br/>*.html files]
    
    StaticOutput --> End([End])
    InteractiveOutput --> End
    
    style Validate fill:transparent,stroke:#2196F3,stroke-width:2px,color:#1976D2
    style Small fill:transparent,stroke:#2196F3,stroke-width:2px,color:#1976D2
    style Full fill:transparent,stroke:#2196F3,stroke-width:2px,color:#1976D2
    style Post fill:transparent,stroke:#FF9800,stroke-width:2px,color:#F57C00
    style VizStatic fill:transparent,stroke:#4CAF50,stroke-width:2px,color:#388E3C
    style VizInteractive fill:transparent,stroke:#4CAF50,stroke-width:2px,color:#388E3C
    style ValOutput fill:transparent,stroke:#9C27B0,stroke-width:2px,stroke-dasharray: 5 5
    style SmallOutput fill:transparent,stroke:#9C27B0,stroke-width:2px,stroke-dasharray: 5 5
    style FullOutput fill:transparent,stroke:#9C27B0,stroke-width:2px,stroke-dasharray: 5 5
    style PostOutput fill:transparent,stroke:#FBC02D,stroke-width:2px,stroke-dasharray: 5 5
    style StaticOutput fill:transparent,stroke:#66BB6A,stroke-width:2px,stroke-dasharray: 5 5
    style InteractiveOutput fill:transparent,stroke:#66BB6A,stroke-width:2px,stroke-dasharray: 5 5
    style Start fill:transparent,stroke:#424242,stroke-width:3px
    style End fill:transparent,stroke:#424242,stroke-width:3px
```

## Usage
1. Install dependencies:
```bash
pip install -r requirements.txt
```
2. Validate randomness and rules:
```bash
python simulate.py validate --quick
```
3. Small-scale test (10 runs × 50 steps):
```bash
python simulate.py small --seed 42
```
4. Full generation (1000 runs × 500 steps):
```bash
python simulate.py full --seed 42
```
5. Post-process aggregate stats and simple features/labels:
```bash
python simulate.py post
```
6. Generate static visualizations:
```bash
python simulate.py visualize
```
7. Generate interactive Plotly visualizations (in separate subfolder):
```bash
python simulate.py visualize-interactive
```
You can specify which runs to visualize: `python simulate.py visualize-interactive --runs 1 2 3 4 5`

## Outputs

**Note**: The following directories are automatically created when you run the simulation commands. They are not included in the git repository but will be generated locally.

### Data Directory (`data/`)
Created by: `python simulate.py small` or `python simulate.py full`
- `data/raw/run_XXXX.json`: Individual simulation run records (1000 files)
- `data/processed/`: ML-ready processed data (created by `python simulate.py post`)
  - `features.npy`: Input features for machine learning
  - `labels.npy`: Target labels (winners)
  - `metadata.json`: Data format documentation

### Analysis Directory (`analysis/`)
Created by: `python simulate.py validate` and `python simulate.py post`
- `analysis/validation/`: Randomness validation tests
  - `uniform_10k.json`: Uniformity test (10k samples)
  - `uniform_1M.json`: Uniformity test (1M samples)
  - `pairwise.json`: Pairwise balance test
  - `independence.json`: Independence test
- `analysis/aggregate_stats.json`: Summary statistics across all runs

### Visualizations Directory (`visualizations/`)
Created by: `python simulate.py visualize` and `python simulate.py visualize-interactive`
- `visualizations/static/`: Static PNG plots
  - `winner_evolution.png`: Winner changes over steps
  - `winner_distribution.png`: Winner frequency by candidate
  - `rule_agreement_heatmap.png`: Rule agreement matrix
  - `winner_changes.png`: Change frequency analysis
  - `condorcet_rate.png`: Condorcet winner rate
- `visualizations/interactive/`: Interactive Plotly HTML plots
  - `winner_evolution_interactive.html` - Interactive winner evolution
  - `winner_aggregation_interactive.html` - Winner distribution by voter count
  - `condorcet_rate_interactive.html` - Interactive Condorcet rate plot
  - `winner_distribution_interactive.html` - Interactive bar charts
  - `rule_agreement_heatmap_interactive.html` - Interactive agreement heatmap
  - `winner_changes_interactive.html` - Interactive change frequency
  - `dashboard.html` - Combined dashboard view

## Notes
- Memory: preferences are stored as integers (0–4). Engine writes incrementally to limit memory usage.
- Resume: by default, existing run files are skipped during `full` to allow resuming.
- Performance: for Windows, parallelization is not enabled by default to keep compatibility. Can be added per-need.
