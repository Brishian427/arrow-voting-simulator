from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns

# Set style - minimal, no colors/emojis as per user preference
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 10


class VotingVisualizer:
	def __init__(self, output_dir: Path) -> None:
		self.output_dir = output_dir
		self.output_dir.mkdir(parents=True, exist_ok=True)

	def plot_winner_evolution(self, raw_dir: Path, run_ids: List[int], max_steps: Optional[int] = None) -> Path:
		"""Plot winner evolution over steps for specified runs."""
		fig, axes = plt.subplots(len(run_ids), 1, figsize=(12, 3 * len(run_ids)), sharex=True)
		if len(run_ids) == 1:
			axes = [axes]
		rules = ["plurality", "borda", "condorcet", "irv"]
		candidates = ["A", "B", "C", "D", "E"]
		colors = {'A': '#1f77b4', 'B': '#ff7f0e', 'C': '#2ca02c', 'D': '#d62728', 'E': '#9467bd'}
		linestyles = {'plurality': '-', 'borda': '--', 'condorcet': '-.', 'irv': ':'}
		for idx, run_id in enumerate(run_ids):
			ax = axes[idx]
			with open(raw_dir / f"run_{run_id:04d}.json", "r", encoding="utf-8") as f:
				data = json.load(f)
			steps = []
			winners_by_rule = {rule: [] for rule in rules}
			for rec in data:
				step = rec["step"]
				if max_steps and step > max_steps:
					break
				steps.append(step)
				for rule in rules:
					win = rec["winners"].get(rule)
					winners_by_rule[rule].append(win if win else "None")
			for rule in rules:
				y_vals = [candidates.index(w) if w in candidates else -1 for w in winners_by_rule[rule]]
				ax.plot(steps, y_vals, label=rule, linestyle=linestyles[rule], linewidth=1.5, alpha=0.7)
			ax.set_yticks(range(5))
			ax.set_yticklabels(candidates)
			ax.set_ylabel(f"Winner (Run {run_id})")
			ax.legend(loc='upper right')
			ax.grid(True, alpha=0.3)
		axes[-1].set_xlabel("Step (Number of Voters)")
		plt.suptitle("Winner Evolution Across Voting Rules", y=1.02)
		plt.tight_layout()
		fpath = self.output_dir / "winner_evolution.png"
		plt.savefig(fpath, dpi=150, bbox_inches='tight')
		plt.close()
		return fpath

	def plot_condorcet_rate(self, analysis_dir: Path) -> Optional[Path]:
		"""Plot Condorcet winner existence rate by step."""
		stats_file = analysis_dir / "aggregate_stats.json"
		if not stats_file.exists():
			return None
		with open(stats_file, "r", encoding="utf-8") as f:
			stats = json.load(f)
		cd_rate = stats.get("condorcet_rate_by_step", {})
		if not cd_rate:
			return None
		steps = sorted([int(k) for k in cd_rate.keys()])
		rates = [cd_rate[str(s)] for s in steps]
		fig, ax = plt.subplots(figsize=(10, 6))
		ax.plot(steps, rates, linewidth=2, marker='o', markersize=3)
		ax.set_xlabel("Step (Number of Voters)")
		ax.set_ylabel("Condorcet Winner Existence Rate")
		ax.set_title("Condorcet Winner Rate vs Number of Voters")
		ax.grid(True, alpha=0.3)
		ax.set_ylim([0, 1])
		plt.tight_layout()
		fpath = self.output_dir / "condorcet_rate.png"
		plt.savefig(fpath, dpi=150, bbox_inches='tight')
		plt.close()
		return fpath

	def plot_winner_distribution(self, raw_dir: Path) -> Path:
		"""Plot distribution of winners by rule and candidate."""
		rules = ["plurality", "borda", "condorcet", "irv"]
		candidates = ["A", "B", "C", "D", "E"]
		counts = {rule: {cand: 0 for cand in candidates} for rule in rules}
		files = sorted(raw_dir.glob("run_*.json"))
		for f in files:
			with open(f, "r", encoding="utf-8") as fh:
				data = json.load(fh)
				for rec in data:
					for rule in rules:
						win = rec["winners"].get(rule)
						if win in candidates:
							counts[rule][win] += 1
		fig, axes = plt.subplots(2, 2, figsize=(12, 10))
		axes = axes.flatten()
		for idx, rule in enumerate(rules):
			ax = axes[idx]
			vals = [counts[rule][c] for c in candidates]
			ax.bar(candidates, vals, alpha=0.7)
			ax.set_title(f"{rule.capitalize()} Winner Distribution")
			ax.set_ylabel("Frequency")
			ax.grid(True, alpha=0.3, axis='y')
		plt.suptitle("Winner Distribution by Voting Rule", y=1.02)
		plt.tight_layout()
		fpath = self.output_dir / "winner_distribution.png"
		plt.savefig(fpath, dpi=150, bbox_inches='tight')
		plt.close()
		return fpath

	def plot_rule_agreement_heatmap(self, raw_dir: Path) -> Path:
		"""Create a heatmap showing agreement between rules."""
		rules = ["plurality", "borda", "condorcet", "irv"]
		agreement = np.zeros((len(rules), len(rules)))
		files = sorted(raw_dir.glob("run_*.json"))
		total = 0
		for f in files:
			with open(f, "r", encoding="utf-8") as fh:
				data = json.load(fh)
				for rec in data:
					wins = [rec["winners"].get(rule) for rule in rules]
					for i in range(len(rules)):
						for j in range(len(rules)):
							if wins[i] is not None and wins[j] is not None and wins[i] == wins[j]:
								agreement[i, j] += 1
					total += 1
		agreement = agreement / total if total > 0 else agreement
		fig, ax = plt.subplots(figsize=(8, 6))
		sns.heatmap(agreement, annot=True, fmt='.3f', xticklabels=rules, yticklabels=rules, cmap='YlOrRd', ax=ax)
		ax.set_title("Voting Rule Agreement Matrix")
		plt.tight_layout()
		fpath = self.output_dir / "rule_agreement_heatmap.png"
		plt.savefig(fpath, dpi=150, bbox_inches='tight')
		plt.close()
		return fpath

	def plot_winner_changes(self, raw_dir: Path, num_runs: int = 10) -> Path:
		"""Plot how often winners change between consecutive steps."""
		files = sorted(raw_dir.glob("run_*.json"))[:num_runs]
		all_changes = []
		for f in files:
			with open(f, "r", encoding="utf-8") as fh:
				data = json.load(fh)
				for rule in ["plurality", "borda", "condorcet", "irv"]:
					prev = None
					changes = []
					for rec in data:
						curr = rec["winners"].get(rule)
						changes.append(1 if curr != prev and prev is not None else 0)
						prev = curr
					all_changes.append(changes)
		if not all_changes:
			all_changes = [[0]]
		changes_array = np.array(all_changes)
		mean_changes = np.mean(changes_array, axis=0)
		steps = list(range(1, len(mean_changes) + 1))
		fig, ax = plt.subplots(figsize=(10, 6))
		ax.plot(steps, mean_changes, linewidth=2)
		ax.set_xlabel("Step")
		ax.set_ylabel("Average Winner Change Rate")
		ax.set_title(f"Winner Change Frequency Across {num_runs} Runs")
		ax.grid(True, alpha=0.3)
		plt.tight_layout()
		fpath = self.output_dir / "winner_changes.png"
		plt.savefig(fpath, dpi=150, bbox_inches='tight')
		plt.close()
		return fpath

	def generate_all(self, root: Path, example_runs: List[int] = None, max_steps: int = 100) -> Dict[str, Path]:
		"""Generate all visualizations."""
		raw_dir = root / "data" / "raw"
		analysis_dir = root / "analysis"
		if example_runs is None:
			files = sorted(raw_dir.glob("run_*.json"))
			example_runs = [int(f.stem.split('_')[1]) for f in files[:5]]
		outputs = {}
		outputs["winner_evolution"] = self.plot_winner_evolution(raw_dir, example_runs, max_steps)
		outputs["winner_distribution"] = self.plot_winner_distribution(raw_dir)
		outputs["rule_agreement"] = self.plot_rule_agreement_heatmap(raw_dir)
		outputs["winner_changes"] = self.plot_winner_changes(raw_dir)
		condorcet_path = self.plot_condorcet_rate(analysis_dir)
		if condorcet_path:
			outputs["condorcet_rate"] = condorcet_path
		return outputs

