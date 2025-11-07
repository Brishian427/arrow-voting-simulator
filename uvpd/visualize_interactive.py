from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional
import json
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


class InteractiveVisualizer:
	"""Generate interactive Plotly visualizations for voting data."""

	def __init__(self, output_dir: Path) -> None:
		self.output_dir = output_dir
		self.output_dir.mkdir(parents=True, exist_ok=True)

	def plot_winner_evolution_interactive(self, raw_dir: Path, run_ids: List[int], max_steps: Optional[int] = None) -> Path:
		"""Interactive plot of winner evolution over steps for specified runs."""
		rules = ["plurality", "borda", "condorcet", "irv"]
		candidates = ["A", "B", "C", "D", "E"]
		colors = {'plurality': '#1f77b4', 'borda': '#ff7f0e', 'condorcet': '#2ca02c', 'irv': '#d62728'}
		linestyles = {'plurality': 'solid', 'borda': 'dash', 'condorcet': 'dashdot', 'irv': 'dot'}
		
		fig = make_subplots(
			rows=len(run_ids), 
			cols=1, 
			subplot_titles=[f"Run {run_id}" for run_id in run_ids],
			shared_xaxes=True,
			vertical_spacing=0.1
		)
		
		for idx, run_id in enumerate(run_ids):
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
					winners_by_rule[rule].append(win if win else None)
			
			for rule in rules:
				y_vals = []
				for w in winners_by_rule[rule]:
					if w in candidates:
						y_vals.append(candidates.index(w))
					else:
						y_vals.append(None)
				
				fig.add_trace(
					go.Scatter(
						x=steps,
						y=y_vals,
						mode='lines+markers',
						name=rule,
						line=dict(color=colors[rule], dash=linestyles[rule], width=2),
						marker=dict(size=4),
						showlegend=(idx == 0),
						legendgroup=rule,
						hovertemplate=f"{rule}<br>Step: %{{x}}<br>Winner: %{{text}}<extra></extra>",
						text=[winners_by_rule[rule][i] if winners_by_rule[rule][i] else "None" for i in range(len(y_vals))],
					),
					row=idx + 1,
					col=1
				)
		
		fig.update_yaxes(
			tickmode='array',
			tickvals=list(range(5)),
			ticktext=candidates,
			title_text="Winner",
			row=len(run_ids),
			col=1
		)
		fig.update_xaxes(title_text="Step (Number of Voters)", row=len(run_ids), col=1)
		fig.update_layout(
			height=300 * len(run_ids),
			title_text="Winner Evolution Across Voting Rules (Interactive)",
			hovermode='closest'
		)
		
		fpath = self.output_dir / "winner_evolution_interactive.html"
		fig.write_html(fpath)
		# Also save PNG to static folder
		static_dir = self.output_dir.parent / "static"
		static_dir.mkdir(parents=True, exist_ok=True)
		fpath_png = static_dir / "winner_evolution_interactive.png"
		fig.write_image(fpath_png, width=1200, height=300 * len(run_ids), scale=2)
		return fpath

	def plot_condorcet_rate_interactive(self, analysis_dir: Path) -> Optional[Path]:
		"""Interactive plot of Condorcet winner existence rate by step."""
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
		
		fig = go.Figure()
		fig.add_trace(
			go.Scatter(
				x=steps,
				y=rates,
				mode='lines+markers',
				name='Condorcet Rate',
				line=dict(width=3, color='#2ca02c'),
				marker=dict(size=6),
				hovertemplate='Step: %{x}<br>Rate: %{y:.3f}<extra></extra>'
			)
		)
		fig.update_layout(
			title="Condorcet Winner Rate vs Number of Voters (Interactive)",
			xaxis_title="Step (Number of Voters)",
			yaxis_title="Condorcet Winner Existence Rate",
			yaxis_range=[0, 1],
			hovermode='closest',
			height=600
		)
		
		fpath = self.output_dir / "condorcet_rate_interactive.html"
		fig.write_html(fpath)
		static_dir = self.output_dir.parent / "static"
		static_dir.mkdir(parents=True, exist_ok=True)
		fpath_png = static_dir / "condorcet_rate_interactive.png"
		fig.write_image(fpath_png, width=1200, height=600, scale=2)
		return fpath

	def plot_winner_distribution_interactive(self, raw_dir: Path) -> Path:
		"""Interactive distribution of winners by rule and candidate."""
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
		
		fig = make_subplots(
			rows=2, 
			cols=2,
			subplot_titles=[rule.capitalize() for rule in rules],
			horizontal_spacing=0.15,
			vertical_spacing=0.15
		)
		
		positions = [(1, 1), (1, 2), (2, 1), (2, 2)]
		for idx, rule in enumerate(rules):
			row, col = positions[idx]
			vals = [counts[rule][c] for c in candidates]
			fig.add_trace(
				go.Bar(
					x=candidates,
					y=vals,
					name=rule,
					showlegend=False,
					marker_color='#1f77b4',
					hovertemplate=f"{rule}<br>Candidate: %{{x}}<br>Frequency: %{{y}}<extra></extra>"
				),
				row=row,
				col=col
			)
			fig.update_yaxes(title_text="Frequency", row=row, col=col)
		
		fig.update_layout(
			title_text="Winner Distribution by Voting Rule (Interactive)",
			height=800,
			hovermode='closest'
		)
		
		fpath = self.output_dir / "winner_distribution_interactive.html"
		fig.write_html(fpath)
		static_dir = self.output_dir.parent / "static"
		static_dir.mkdir(parents=True, exist_ok=True)
		fpath_png = static_dir / "winner_distribution_interactive.png"
		fig.write_image(fpath_png, width=1200, height=800, scale=2)
		return fpath

	def plot_rule_agreement_heatmap_interactive(self, raw_dir: Path) -> Path:
		"""Interactive heatmap showing agreement between rules."""
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
		
		fig = go.Figure(data=go.Heatmap(
			z=agreement.tolist(),
			x=rules,
			y=rules,
			colorscale='YlOrRd',
			text=[[f"{agreement[i, j]:.3f}" for j in range(len(rules))] for i in range(len(rules))],
			texttemplate='%{text}',
			textfont={"size": 12},
			hovertemplate='%{y} vs %{x}<br>Agreement: %{z:.3f}<extra></extra>'
		))
		fig.update_layout(
			title="Voting Rule Agreement Matrix (Interactive)",
			xaxis_title="Rule",
			yaxis_title="Rule",
			height=600,
			width=700
		)
		
		fpath = self.output_dir / "rule_agreement_heatmap_interactive.html"
		fig.write_html(fpath)
		static_dir = self.output_dir.parent / "static"
		static_dir.mkdir(parents=True, exist_ok=True)
		fpath_png = static_dir / "rule_agreement_heatmap_interactive.png"
		fig.write_image(fpath_png, width=700, height=600, scale=2)
		return fpath

	def plot_winner_changes_interactive(self, raw_dir: Path, num_runs: int = 10) -> Path:
		"""Interactive plot showing how often winners change between consecutive steps."""
		files = sorted(raw_dir.glob("run_*.json"))[:num_runs]
		rules = ["plurality", "borda", "condorcet", "irv"]
		all_changes_by_rule = {rule: [] for rule in rules}
		
		for f in files:
			with open(f, "r", encoding="utf-8") as fh:
				data = json.load(fh)
				for rule in rules:
					prev = None
					changes = []
					for rec in data:
						curr = rec["winners"].get(rule)
						changes.append(1 if curr != prev and prev is not None else 0)
						prev = curr
					all_changes_by_rule[rule].append(changes)
		
		if not any(all_changes_by_rule.values()):
			steps = [1]
			mean_changes = {rule: [0] for rule in rules}
		else:
			max_len = max(len(changes[0]) for changes in all_changes_by_rule.values() if changes)
			steps = list(range(1, max_len + 1))
			mean_changes = {}
			for rule in rules:
				if all_changes_by_rule[rule]:
					changes_array = np.array(all_changes_by_rule[rule])
					mean_changes[rule] = np.mean(changes_array, axis=0).tolist()
				else:
					mean_changes[rule] = [0] * len(steps)
		
		fig = go.Figure()
		colors = {'plurality': '#1f77b4', 'borda': '#ff7f0e', 'condorcet': '#2ca02c', 'irv': '#d62728'}
		
		for rule in rules:
			fig.add_trace(
				go.Scatter(
					x=steps,
					y=mean_changes[rule],
					mode='lines+markers',
					name=rule,
					line=dict(width=2, color=colors[rule]),
					marker=dict(size=4),
					hovertemplate=f"{rule}<br>Step: %{{x}}<br>Change Rate: %{{y:.3f}}<extra></extra>"
				)
			)
		
		fig.update_layout(
			title=f"Winner Change Frequency Across {num_runs} Runs (Interactive)",
			xaxis_title="Step",
			yaxis_title="Average Winner Change Rate",
			hovermode='closest',
			height=600,
			legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
		)
		
		fpath = self.output_dir / "winner_changes_interactive.html"
		fig.write_html(fpath)
		static_dir = self.output_dir.parent / "static"
		static_dir.mkdir(parents=True, exist_ok=True)
		fpath_png = static_dir / "winner_changes_interactive.png"
		fig.write_image(fpath_png, width=1200, height=600, scale=2)
		return fpath

	def plot_dashboard(self, raw_dir: Path, analysis_dir: Path, run_ids: List[int] = None) -> Path:
		"""Create an interactive dashboard with multiple views."""
		if run_ids is None:
			files = sorted(raw_dir.glob("run_*.json"))
			run_ids = [int(f.stem.split('_')[1]) for f in files[:5]]
		
		fig = make_subplots(
			rows=2, cols=2,
			subplot_titles=(
				"Winner Evolution",
				"Condorcet Rate",
				"Rule Agreement",
				"Winner Changes"
			),
			specs=[[{"secondary_y": False}, {"secondary_y": False}],
				   [{"type": "heatmap"}, {"secondary_y": False}]]
		)
		
		# 1. Winner Evolution (simplified - show first run only)
		if run_ids:
			with open(raw_dir / f"run_{run_ids[0]:04d}.json", "r", encoding="utf-8") as f:
				data = json.load(f)
			rules = ["plurality", "borda", "condorcet", "irv"]
			candidates = ["A", "B", "C", "D", "E"]
			steps = [rec["step"] for rec in data[:50]]
			for rule in rules:
				y_vals = []
				for rec in data[:50]:
					win = rec["winners"].get(rule)
					if win in candidates:
						y_vals.append(candidates.index(win))
					else:
						y_vals.append(None)
				fig.add_trace(
					go.Scatter(x=steps, y=y_vals, mode='lines', name=rule, showlegend=True),
					row=1, col=1
				)
		
		# 2. Condorcet Rate
		stats_file = analysis_dir / "aggregate_stats.json"
		if stats_file.exists():
			with open(stats_file, "r", encoding="utf-8") as f:
				stats = json.load(f)
			cd_rate = stats.get("condorcet_rate_by_step", {})
			if cd_rate:
				cd_steps = sorted([int(k) for k in cd_rate.keys()])
				cd_rates = [cd_rate[str(s)] for s in cd_steps]
				fig.add_trace(
					go.Scatter(x=cd_steps, y=cd_rates, mode='lines+markers', name='Condorcet Rate', showlegend=False),
					row=1, col=2
				)
		
		# 3. Rule Agreement Heatmap
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
		fig.add_trace(
			go.Heatmap(z=agreement.tolist(), x=rules, y=rules, colorscale='YlOrRd', showscale=True),
			row=2, col=1
		)
		
		# 4. Winner Changes (placeholder - simplified)
		fig.add_trace(
			go.Scatter(x=[1, 2, 3], y=[0.1, 0.15, 0.12], mode='lines', name='Changes', showlegend=False),
			row=2, col=2
		)
		
		fig.update_layout(
			title_text="Voting Simulation Dashboard (Interactive)",
			height=1000,
			showlegend=True
		)
		
		fpath = self.output_dir / "dashboard.html"
		fig.write_html(fpath)
		return fpath

	def plot_winner_aggregation_interactive(self, raw_dir: Path, max_steps: Optional[int] = None) -> Path:
		"""Interactive visualization of winner distribution across all runs as voters accumulate."""
		rules = ["plurality", "borda", "condorcet", "irv"]
		candidates = ["A", "B", "C", "D", "E"]
		files = sorted(raw_dir.glob("run_*.json"))
		
		# Build aggregation data: step -> rule -> candidate -> count
		aggregation = {rule: {cand: {} for cand in candidates} for rule in rules}
		max_step_found = 0
		
		for f in files:
			with open(f, "r", encoding="utf-8") as fh:
				data = json.load(fh)
				for rec in data:
					step = rec["step"]
					if max_steps and step > max_steps:
						continue
					max_step_found = max(max_step_found, step)
					for rule in rules:
						winner = rec["winners"].get(rule)
						if winner in candidates:
							if step not in aggregation[rule][winner]:
								aggregation[rule][winner][step] = 0
							aggregation[rule][winner][step] += 1
		
		# Create subplots for each voting rule
		fig = make_subplots(
			rows=2, cols=2,
			subplot_titles=[rule.capitalize() for rule in rules],
			shared_xaxes=True,
			shared_yaxes=False,
			vertical_spacing=0.15,
			horizontal_spacing=0.1
		)
		
		positions = [(1, 1), (1, 2), (2, 1), (2, 2)]
		colors_map = {'A': '#1f77b4', 'B': '#ff7f0e', 'C': '#2ca02c', 'D': '#d62728', 'E': '#9467bd'}
		
		for idx, rule in enumerate(rules):
			row, col = positions[idx]
			steps = sorted(set().union(*[list(aggregation[rule][c].keys()) for c in candidates]))
			
			for cand in candidates:
				y_vals = [aggregation[rule][cand].get(s, 0) for s in steps]
				fig.add_trace(
					go.Scatter(
						x=steps,
						y=y_vals,
						mode='lines+markers',
						name=cand,
						stackgroup='one',
						fill='tonexty' if cand != 'A' else 'tozeroy',
						line=dict(width=0.5, color=colors_map[cand]),
						marker=dict(size=2),
						hovertemplate=f"{rule}<br>Step: %{{x}}<br>Candidate: {cand}<br>Count: %{{y}}<extra></extra>",
						showlegend=(idx == 0),
						legendgroup=cand,
					),
					row=row,
					col=col
				)
		
		fig.update_xaxes(title_text="Number of Voters", row=2, col=1)
		fig.update_xaxes(title_text="Number of Voters", row=2, col=2)
		fig.update_yaxes(title_text="Winner Count", row=1, col=1)
		fig.update_yaxes(title_text="Winner Count", row=2, col=1)
		
		fig.update_layout(
			title_text="Winner Distribution Across All Runs by Voter Count (Interactive)",
			height=1000,
			hovermode='x unified',
			legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
		)
		
		fpath = self.output_dir / "winner_aggregation_interactive.html"
		fig.write_html(fpath)
		static_dir = self.output_dir.parent / "static"
		static_dir.mkdir(parents=True, exist_ok=True)
		fpath_png = static_dir / "winner_aggregation_interactive.png"
		fig.write_image(fpath_png, width=1400, height=1000, scale=2)
		return fpath

	def generate_all(self, root: Path, example_runs: List[int] = None, max_steps: int = 100) -> Dict[str, Path]:
		"""Generate all interactive visualizations."""
		raw_dir = root / "data" / "raw"
		analysis_dir = root / "analysis"
		
		if example_runs is None:
			files = sorted(raw_dir.glob("run_*.json"))
			example_runs = [int(f.stem.split('_')[1]) for f in files[:5]]
		
		outputs = {}
		outputs["winner_evolution"] = self.plot_winner_evolution_interactive(raw_dir, example_runs, max_steps)
		outputs["winner_distribution"] = self.plot_winner_distribution_interactive(raw_dir)
		outputs["rule_agreement"] = self.plot_rule_agreement_heatmap_interactive(raw_dir)
		outputs["winner_changes"] = self.plot_winner_changes_interactive(raw_dir)
		outputs["winner_aggregation"] = self.plot_winner_aggregation_interactive(raw_dir, max_steps=None)
		outputs["dashboard"] = self.plot_dashboard(raw_dir, analysis_dir, example_runs)
		
		condorcet_path = self.plot_condorcet_rate_interactive(analysis_dir)
		if condorcet_path:
			outputs["condorcet_rate"] = condorcet_path
		
		return outputs

