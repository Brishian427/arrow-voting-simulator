from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple
import json
import numpy as np
from scipy.stats import chisquare

from .preference import PreferenceGenerator


@dataclass
class RandomnessValidator:
	def uniform_distribution_test(self, gen: PreferenceGenerator, total_samples: int = 1_000_000) -> Dict[str, object]:
		# Sample indexes to permutations for memory efficiency
		idx = gen.rng.integers(0, 120, size=total_samples)
		counts = np.bincount(idx, minlength=120)
		expected = np.full(120, total_samples / 120.0)
		chi, p = chisquare(counts, expected)
		return {
			"total_samples": int(total_samples),
			"min": int(counts.min()),
			"max": int(counts.max()),
			"expected": float(expected[0]),
			"p_value": float(p),
		}

	def pairwise_balance_test(self, gen: PreferenceGenerator, total_samples: int = 500_000) -> Dict[str, object]:
		# For each pair (a,b), count how often a is preferred over b
		prefs = gen.sample(total_samples)
		# ranks[row, cand]
		ranks = np.empty((total_samples, 5), dtype=np.int8)
		for i in range(total_samples):
			for pos, cand in enumerate(prefs[i]):
				ranks[i, cand] = pos
		balance = {}
		for a in range(5):
			for b in range(a + 1, 5):
				ab = int(np.sum(ranks[:, a] < ranks[:, b]))
				ba = total_samples - ab
				ratio = ab / total_samples
				balance[f"{a}-{b}"] = {
					"a_over_b": ab,
					"b_over_a": ba,
					"ratio_a": float(ratio),
				}
		return balance

	def independence_test(self, gen: PreferenceGenerator, total_runs: int = 100, per_run: int = 1000) -> Dict[str, object]:
		# Correlation between consecutive run frequency vectors
		vectors = []
		for _ in range(total_runs):
			idx = gen.rng.integers(0, 120, size=per_run)
			counts = np.bincount(idx, minlength=120).astype(float)
			counts /= counts.sum()
			vectors.append(counts)
		corrs = []
		for i in range(1, len(vectors)):
			v1, v2 = vectors[i - 1], vectors[i]
			c = float(np.corrcoef(v1, v2)[0, 1])
			corrs.append(c)
		return {
			"mean_corr": float(np.mean(corrs)),
			"max_corr": float(np.max(corrs)),
			"min_corr": float(np.min(corrs)),
		}


class AggregateAnalyzer:
	def condorcet_rate_by_step(self, raw_dir: Path) -> Dict[int, float]:
		# For each step, compute fraction of runs with a Condorcet winner
		from .rules import CondorcetRule
		import orjson
		files = sorted((raw_dir).glob("run_*.json"))
		if not files:
			return {}
		max_step = 0
		for f in files:
			with open(f, "rb") as fh:
				data = orjson.loads(fh.read())
				if data:
					max_step = max(max_step, int(data[-1]["step"]))
		if max_step == 0:
			return {}
		counts = np.zeros((max_step,), dtype=np.int64)
		totals = np.zeros((max_step,), dtype=np.int64)
		for f in files:
			with open(f, "rb") as fh:
				data = orjson.loads(fh.read())
				for rec in data:
					step = int(rec["step"]) - 1
					if step >= max_step:
						continue
					cd = rec["winners"].get("condorcet")
					totals[step] += 1
					if cd is not None:
						counts[step] += 1
		return {i + 1: (counts[i] / totals[i] if totals[i] else 0.0) for i in range(max_step)}

	def rule_agreement_frequency(self, raw_dir: Path) -> Dict[str, float]:
		import orjson
		files = sorted((raw_dir).glob("run_*.json"))
		agree_any = 0
		agree_all = 0
		total = 0
		for f in files:
			with open(f, "rb") as fh:
				data = orjson.loads(fh.read())
				for rec in data:
					wins = rec["winners"]
					vals = [wins["plurality"], wins["borda"], wins["irv"], wins["condorcet"]]
					vals_nonnull = [v for v in vals if v is not None]
					if len(set(vals_nonnull)) <= 3:
						agree_any += 1
					if len(set(vals_nonnull)) == 1 and len(vals_nonnull) >= 2:
						agree_all += 1
					total += 1
			if total == 0:
				return {"agree_any": 0.0, "agree_all": 0.0}
		return {"agree_any": agree_any / total, "agree_all": agree_all / total}

	def winner_volatility(self, raw_dir: Path) -> Dict[str, float]:
		import orjson
		files = sorted((raw_dir).glob("run_*.json"))
		changes = 0
		total_transitions = 0
		for f in files:
			with open(f, "rb") as fh:
				data = orjson.loads(fh.read())
				prev = None
				for rec in data:
					curr = tuple(rec["winners"][k] for k in ("plurality", "borda", "condorcet", "irv"))
					if prev is not None and curr != prev:
						changes += 1
					prev = curr
					total_transitions += 1
			if total_transitions == 0:
				continue
		return {"avg_changes_per_run": (changes / max(total_transitions, 1.0))}
