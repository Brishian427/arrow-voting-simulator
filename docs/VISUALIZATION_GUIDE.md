# Visualization Guide

This document explains how to interpret each visualization in the project.

## Overview

All visualizations are organized in the `visualizations/` directory:
- **Static plots** (`visualizations/static/`): PNG images for papers/presentations
- **Interactive plots** (`visualizations/interactive/`): HTML files for exploration (open in browser)

---

## 1. Winner Evolution (`winner_evolution*.png/html`)

**What it shows**: How winners change as voters are progressively added in individual example runs.

**Interpretation**:
- X-axis: Step (number of voters, 1 to N)
- Y-axis: Winner candidate (A, B, C, D, E)
- Each colored line represents a different voting rule
- When lines cross or change, the winner changed for that rule

**Key insights**:
- High volatility (frequent line changes) = unstable outcomes
- Lines converging = rules agreeing as more voters added
- Condorcet line may show "None" when no Condorcet winner exists

---

## 2. Winner Aggregation (`winner_aggregation_interactive.html`)

**What it shows**: Distribution of winners across ALL 1000 runs, aggregated by voter count.

**Interpretation**:
- X-axis: Number of voters (step)
- Y-axis: Count of runs where each candidate won (stacked areas)
- Each colored band = one candidate
- Total height ≈ 1000 (one winner per run per step)

**How to read**:
- At step k, if Candidate A's band height is 200, it means in 200 out of 1000 runs, Candidate A was the winner after k voters
- Wide, stable bands = consistent winners across runs
- Narrow, fluctuating bands = high variability

**Key insights**:
- All candidates should have roughly equal band thickness (20% each) if truly random
- Bands stabilizing over time = law of large numbers taking effect
- Condorcet chart may have lower total height when no winner exists

---

## 3. Winner Distribution (`winner_distribution*.png/html`)

**What it shows**: Total frequency of each candidate winning across all runs and all steps.

**Interpretation**:
- Four bar charts (one per voting rule)
- X-axis: Candidates (A, B, C, D, E)
- Y-axis: Total count of times that candidate won

**Key insights**:
- Equal bar heights = fair distribution (expected with uniform random preferences)
- Skewed distribution = potential tiebreaking bias or rule-specific effects

---

## 4. Rule Agreement Heatmap (`rule_agreement_heatmap*.png/html`)

**What it shows**: How often pairs of voting rules agree on the same winner.

**Interpretation**:
- Matrix where cell (i, j) = fraction of steps where rule i and rule j chose the same winner
- Diagonal = 1.0 (each rule always agrees with itself)
- Off-diagonal values = agreement frequency between different rules

**How to read**:
- Value 0.8 = rules agree 80% of the time
- Bright/high values = high agreement
- Dark/low values = frequent disagreement

**Key insights**:
- High agreement = rules produce similar outcomes
- Low agreement = rules have fundamentally different behaviors

---

## 5. Winner Changes (`winner_changes*.png/html`)

**What it shows**: Average probability that the winner changes when a new voter is added.

**Interpretation**:
- X-axis: Step (voter count)
- Y-axis: Average winner change rate (0 to 1)
- Each line = one voting rule

**How to read**:
- Value 0.5 at step k = 50% chance the winner changed from step k-1 to step k
- Declining line = outcomes becoming more stable as voters increase
- High initial values = high volatility with few voters

**Key insights**:
- All rules should show declining change rates (stabilization)
- Condorcet and IRV may show higher volatility due to their complex mechanics

---

## 6. Condorcet Rate (`condorcet_rate*.png/html`)

**What it shows**: Fraction of runs where a Condorcet winner exists, by voter count.

**Interpretation**:
- X-axis: Step (number of voters)
- Y-axis: Condorcet winner existence rate (0 to 1)
- Value 0.75 = 75% of runs had a Condorcet winner at that voter count

**Key insights**:
- Typically increases with more voters (more likely to have clear majority preferences)
- Plateau indicates stable probability
- Lower rates at small voter counts reflect higher chance of preference cycles

---

## 7. Dashboard (`dashboard.html`)

**What it shows**: Combined view with multiple plots in one page.

**Purpose**: Quick overview of key metrics without opening multiple files.

---

## Interactive Features

All interactive HTML plots support:
- **Zoom**: Click and drag to zoom into regions
- **Pan**: Click and drag to move around
- **Reset**: Double-click to reset zoom
- **Hover**: Hover over data points for exact values
- **Toggle**: Click legend items to show/hide series
- **Export**: Use toolbar to export as PNG

---

## Recommended Exploration Workflow

1. Start with **dashboard.html** for overview
2. Explore **winner_aggregation_interactive.html** to understand distribution patterns
3. Check **rule_agreement_heatmap_interactive.html** to see rule similarities
4. Use **winner_evolution_interactive.html** to see individual run behavior
5. Review **condorcet_rate_interactive.html** for Condorcet-specific insights
6. Analyze **winner_changes_interactive.html** for stability patterns

---

## Static vs Interactive

- **Static PNGs**: Use for papers, presentations, documentation
- **Interactive HTMLs**: Use for exploration, detailed analysis, demonstrations
- Both show the same data, but interactive allows deeper investigation

