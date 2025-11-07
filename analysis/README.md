# Analysis Directory

This directory stores statistical analysis outputs and validation results.

## Structure

- `validation/` - Randomness validation tests (created when running `python simulate.py validate`)
  - `uniform_10k.json` - Uniformity test with 10,000 samples
  - `uniform_1M.json` - Uniformity test with 1,000,000 samples
  - `pairwise.json` - Pairwise candidate preference balance test
  - `independence.json` - Independence test across runs

- `aggregate_stats.json` - Summary statistics across all runs (created when running `python simulate.py post`)
  - Condorcet winner rate by voter count
  - Rule agreement frequencies
  - Winner volatility metrics

## Generation

These files are automatically created when you run:
- `python simulate.py validate` → Creates `analysis/validation/`
- `python simulate.py post` → Creates `analysis/aggregate_stats.json`

**Note**: Analysis files are excluded from git via `.gitignore` as they can be regenerated from raw data.

