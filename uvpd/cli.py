from __future__ import annotations

import argparse
from pathlib import Path
import json
import numpy as np

from .preference import PreferenceGenerator
from .engine import ProgressiveSimulator, SimulationConfig
from .stats import RandomnessValidator, AggregateAnalyzer
from .visualize import VotingVisualizer
from .visualize_interactive import InteractiveVisualizer


def cmd_validate(args: argparse.Namespace) -> None:
	root = Path(args.root).resolve()
	gen = PreferenceGenerator()
	val = RandomnessValidator()
	res1 = gen.validate_uniformity(num_samples=10_000)
	(root / "analysis" / "validation").mkdir(parents=True, exist_ok=True)
	(root / "analysis" / "validation" / "uniform_10k.json").write_text(json.dumps(res1, indent=2), encoding="utf-8")
	res2 = val.uniform_distribution_test(gen, total_samples=1_000_000 if not args.quick else 100_000)
	(root / "analysis" / "validation" / "uniform_1M.json").write_text(json.dumps(res2, indent=2), encoding="utf-8")
	res3 = val.pairwise_balance_test(gen, total_samples=500_000 if not args.quick else 50_000)
	(root / "analysis" / "validation" / "pairwise.json").write_text(json.dumps(res3, indent=2), encoding="utf-8")
	res4 = val.independence_test(gen, total_runs=100 if not args.quick else 10, per_run=1000)
	(root / "analysis" / "validation" / "independence.json").write_text(json.dumps(res4, indent=2), encoding="utf-8")
	print("Validation completed. Reports in analysis/validation")


def cmd_small(args: argparse.Namespace) -> None:
	root = Path(args.root).resolve()
	sim = ProgressiveSimulator(SimulationConfig(runs=10, max_voters=50, seed=args.seed, progress=True), root)
	sim.run()
	print("Small-scale test complete.")


def cmd_full(args: argparse.Namespace) -> None:
	root = Path(args.root).resolve()
	sim = ProgressiveSimulator(SimulationConfig(runs=1000, max_voters=500, seed=args.seed, progress=True, resume=True), root)
	sim.run()
	print("Full generation complete.")


def cmd_post(args: argparse.Namespace) -> None:
	root = Path(args.root).resolve()
	raw_dir = root / "data" / "raw"
	ana = AggregateAnalyzer()
	cd_rate = ana.condorcet_rate_by_step(raw_dir)
	agree = ana.rule_agreement_frequency(raw_dir)
	vol = ana.winner_volatility(raw_dir)
	out = {
		"condorcet_rate_by_step": cd_rate,
		"rule_agreement": agree,
		"winner_volatility": vol,
	}
	(root / "analysis" / "aggregate_stats.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
	# Minimal ML features/labels example: For the final step of each run, store winners
	features = []
	labels = []
	for f in sorted(raw_dir.glob("run_*.json")):
		data = json.loads(f.read_text(encoding="utf-8"))
		if not data:
			continue
		last = data[-1]
		wins = last["winners"]
		# Simple features: first-place counts and Borda scores at final step
		# Recompute from voter_preferences to avoid storing in-file
		prefs = np.array(last["voter_preferences"], dtype=np.int8)
		from .rules import PluralityRule, BordaRule
		pl = PluralityRule.compute(prefs).aux["counts"]
		bd = BordaRule.compute(prefs).aux["scores"]
		features.append(pl + bd)
		labels.append([wins.get("plurality"), wins.get("borda"), wins.get("condorcet"), wins.get("irv")])
	np.save(root / "data" / "processed" / "features.npy", np.array(features, dtype=np.int64))
	np.save(root / "data" / "processed" / "labels.npy", np.array(labels, dtype=object))
	(root / "data" / "processed" / "metadata.json").write_text(json.dumps({"note": "features are [plurality_counts(5) + borda_scores(5)]"}, indent=2), encoding="utf-8")
	print("Post-processing complete.")


def cmd_visualize(args: argparse.Namespace) -> None:
	root = Path(args.root).resolve()
	viz = VotingVisualizer(output_dir=root / "visualizations" / "static")
	example_runs = args.runs if args.runs else None
	outputs = viz.generate_all(root, example_runs=example_runs, max_steps=args.max_steps)
	print("Visualizations generated:")
	for name, path in outputs.items():
		print(f"  - {name}: {path}")


def cmd_visualize_interactive(args: argparse.Namespace) -> None:
	root = Path(args.root).resolve()
	interactive_dir = root / "visualizations" / "interactive"
	viz = InteractiveVisualizer(output_dir=interactive_dir)
	example_runs = args.runs if args.runs else None
	outputs = viz.generate_all(root, example_runs=example_runs, max_steps=args.max_steps)
	print("Interactive visualizations generated:")
	for name, path in outputs.items():
		print(f"  - {name}: {path}")
	print(f"\nAll interactive visualizations saved to: {interactive_dir}")
	print("Open the .html files in a web browser for interactive viewing.")


def build_parser() -> argparse.ArgumentParser:
	p = argparse.ArgumentParser(description="Universal Voting Pattern Data Generator")
	p.add_argument("command", choices=["validate", "small", "full", "post", "visualize", "visualize-interactive"], help="Pipeline stage to run")
	p.add_argument("--root", default=".", help="Project root path")
	p.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")
	p.add_argument("--quick", action="store_true", help="Run faster, approximate validation")
	p.add_argument("--runs", type=int, nargs="+", default=None, help="Specific run IDs to visualize (default: first 5)")
	p.add_argument("--max-steps", type=int, default=100, help="Maximum steps to show in evolution plots (default: 100)")
	return p


def main(argv: list[str] | None = None) -> None:
	p = build_parser()
	args = p.parse_args(argv)
	if args.command == "validate":
		cmd_validate(args)
	elif args.command == "small":
		cmd_small(args)
	elif args.command == "full":
		cmd_full(args)
	elif args.command == "post":
		cmd_post(args)
	elif args.command == "visualize":
		cmd_visualize(args)
	elif args.command == "visualize-interactive":
		cmd_visualize_interactive(args)
	else:
		raise SystemExit("Unknown command")


if __name__ == "__main__":
	main()
