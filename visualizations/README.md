# Visualizations Directory

This directory stores all visualization outputs.

## Structure

- `static/` - Static PNG images (created when running `python simulate.py visualize`)
  - `winner_evolution.png` - Winner changes over steps
  - `winner_distribution.png` - Winner frequency by candidate
  - `rule_agreement_heatmap.png` - Rule agreement matrix
  - `winner_changes.png` - Change frequency analysis
  - `condorcet_rate.png` - Condorcet winner rate
  - PNG exports from interactive plots (created when running `python simulate.py visualize-interactive`)

- `interactive/` - Interactive Plotly HTML plots (created when running `python simulate.py visualize-interactive`)
  - `winner_evolution_interactive.html` - Interactive winner evolution
  - `winner_aggregation_interactive.html` - Winner distribution by voter count
  - `condorcet_rate_interactive.html` - Interactive Condorcet rate plot
  - `winner_distribution_interactive.html` - Interactive bar charts
  - `rule_agreement_heatmap_interactive.html` - Interactive agreement heatmap
  - `winner_changes_interactive.html` - Interactive change frequency
  - `dashboard.html` - Combined dashboard view

## Generation

These directories and files are automatically created when you run:
- `python simulate.py visualize` → Creates `visualizations/static/`
- `python simulate.py visualize-interactive` → Creates `visualizations/interactive/`

**Note**: Visualization files are excluded from git via `.gitignore` as they can be regenerated from raw data.

