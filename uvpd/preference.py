from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence, Tuple
import numpy as np
from scipy.stats import chisquare


Candidate = int  # 0..4
Preference = Tuple[int, ...]  # permutation of 0..4, length 5


@dataclass(frozen=True)
class CandidateSet:
	labels: Tuple[str, str, str, str, str] = ("A", "B", "C", "D", "E")

	@property
	def size(self) -> int:
		return len(self.labels)


class PreferenceGenerator:
	"""Uniformly samples rankings (permutations) over 5 candidates.

	Uses a precomputed array of all 120 permutations and selects by RNG index.
	"""

	def __init__(self, rng: np.random.Generator | None = None, candidates: CandidateSet | None = None) -> None:
		self.candidates = candidates or CandidateSet()
		if self.candidates.size != 5:
			raise ValueError("This implementation expects exactly 5 candidates.")
		self.rng = rng or np.random.default_rng()
		self._perms = self._generate_all_permutations(self.candidates.size)

	@staticmethod
	def _generate_all_permutations(n: int) -> np.ndarray:
		perms = np.array(list(__import__("itertools").permutations(range(n))), dtype=np.int8)
		if perms.shape != (120, 5):
			raise AssertionError("Expected 120 permutations of 5 candidates")
		return perms

	def sample(self, num_voters: int = 1) -> np.ndarray:
		"""Sample preferences for num_voters; returns shape (num_voters, 5) int8."""
		idx = self.rng.integers(low=0, high=len(self._perms), size=num_voters, endpoint=False)
		return self._perms[idx]

	def validate_uniformity(self, num_samples: int = 10000) -> dict:
		"""Generate num_samples preferences and run chi-square test against uniform.

		Returns summary dict with frequencies and p-value.
		"""
		idx = self.rng.integers(low=0, high=len(self._perms), size=num_samples, endpoint=False)
		counts = np.bincount(idx, minlength=len(self._perms))
		expected = np.full(len(self._perms), num_samples / len(self._perms))
		chi_stat, p_value = chisquare(f_obs=counts, f_exp=expected)
		return {
			"num_samples": int(num_samples),
			"counts": counts.tolist(),
			"expected_per_perm": float(expected[0]),
			"chi_square_stat": float(chi_stat),
			"p_value": float(p_value),
		}
