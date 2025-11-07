from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional
from pathlib import Path
import time
import numpy as np
from tqdm import tqdm

from .preference import PreferenceGenerator, CandidateSet
from .rules import PluralityRule, BordaRule, CondorcetRule, IRVRule
from .recorder import DataRecorder, RecorderConfig


@dataclass
class SimulationConfig:
	runs: int = 1000
	max_voters: int = 500
	seed: Optional[int] = None
	progress: bool = True
	resume: bool = True


class ProgressiveSimulator:
	def __init__(self, config: SimulationConfig, root: Path) -> None:
		self.config = config
		self.root = root
		self.recorder = DataRecorder(config=RecorderConfig(root=root))
		self.rng = np.random.default_rng(config.seed)
		self.pref_gen = PreferenceGenerator(rng=self.rng, candidates=CandidateSet())

	def _run_exists(self, run_id: int) -> bool:
		return (self.root / "data" / "raw" / f"run_{run_id:04d}.json").exists()

	def run(self) -> None:
		iterator = range(1, self.config.runs + 1)
		if self.config.progress:
			iterator = tqdm(iterator, desc="Simulations")
		for run_id in iterator:
			if self.config.resume and self._run_exists(run_id):
				continue
			self._run_single(run_id)

	def _compute_winners(self, prefs: np.ndarray) -> Dict[str, Optional[str]]:
		pl = PluralityRule.compute(prefs).winner
		bd = BordaRule.compute(prefs).winner
		cd = CondorcetRule.compute(prefs).winner
		ir = IRVRule.compute(prefs).winner
		labels = CandidateSet().labels
		return {
			"plurality": labels[pl] if pl is not None else None,
			"borda": labels[bd] if bd is not None else None,
			"condorcet": labels[cd] if cd is not None else None,
			"irv": labels[ir] if ir is not None else None,
		}

	def _run_single(self, run_id: int) -> None:
		self.recorder.start_run(run_id)
		prefs_all = np.empty((0, 5), dtype=np.int8)
		ts0 = time.time()
		for step in range(1, self.config.max_voters + 1):
			new_pref = self.pref_gen.sample(1)
			prefs_all = np.vstack([prefs_all, new_pref])
			winners = self._compute_winners(prefs_all)
			record = {
				"run_id": run_id,
				"step": step,
				"timestamp": time.time(),
				"voter_preferences": prefs_all.tolist(),
				"winners": winners,
			}
			self.recorder.append_step(run_id, record, is_last=(step == self.config.max_voters))
		self.recorder.end_run(run_id)
