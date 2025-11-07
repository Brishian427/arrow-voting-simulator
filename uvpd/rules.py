from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple
import numpy as np

Candidate = int  # 0..4
PreferenceArray = np.ndarray  # shape (n, 5), dtype int8, rows are permutations


@dataclass(frozen=True)
class RuleResult:
	winner: Optional[Candidate]
	aux: Dict[str, object]


def _alphabetical_tiebreak(candidates: Sequence[Candidate]) -> Candidate:
	# Deterministic: lower index wins (A < B < C < D < E)
	return int(min(candidates))


class PluralityRule:
	@staticmethod
	def compute(preferences: PreferenceArray) -> RuleResult:
		# Count first-place: first element in each row is the top choice
		first_choices = preferences[:, 0]
		counts = np.bincount(first_choices, minlength=5)
		max_count = counts.max()
		tied = np.flatnonzero(counts == max_count).tolist()
		winner = _alphabetical_tiebreak(tied)
		return RuleResult(winner=winner, aux={"counts": counts.tolist(), "tie": len(tied) > 1})


class BordaRule:
	@staticmethod
	def compute(preferences: PreferenceArray) -> RuleResult:
		# Points by position: 4,3,2,1,0
		n = preferences.shape[0]
		position_points = np.array([4, 3, 2, 1, 0], dtype=np.int16)
		scores = np.zeros(5, dtype=np.int64)
		# For each voter, add points to candidates by position
		# preferences[row, pos] = candidate
		for pos in range(5):
			cands_at_pos = preferences[:, pos]
			points = position_points[pos]
			counts = np.bincount(cands_at_pos, minlength=5)
			scores += counts * points
		max_score = scores.max()
		tied = np.flatnonzero(scores == max_score).tolist()
		winner = _alphabetical_tiebreak(tied)
		# Validation: total points = n * 10
		total_points = int(scores.sum())
		return RuleResult(
			winner=winner,
			aux={
				"scores": scores.tolist(),
				"total_points": total_points,
				"expected_total_points": int(n * 10),
				"tie": len(tied) > 1,
			},
		)


class CondorcetRule:
	@staticmethod
	def compute(preferences: PreferenceArray) -> RuleResult:
		# Build pairwise matrix wins[a,b] = number of voters preferring a over b
		n = preferences.shape[0]
		# ranks[row, candidate] = position rank (0 best)
		ranks = np.empty((n, 5), dtype=np.int8)
		for row in range(n):
			for pos, cand in enumerate(preferences[row]):
				ranks[row, cand] = pos
		wins = np.zeros((5, 5), dtype=np.int32)
		for a in range(5):
			for b in range(5):
				if a == b:
					continue
				wins[a, b] = int(np.sum(ranks[:, a] < ranks[:, b]))
		# Check Condorcet winner
		beats_all = []
		for a in range(5):
			if all(wins[a, b] > (n - wins[a, b]) for b in range(5) if b != a):
				beats_all.append(a)
		winner: Optional[int]
		if len(beats_all) == 1:
			winner = beats_all[0]
		else:
			winner = None
		return RuleResult(winner=winner, aux={"wins": wins.tolist()})


class IRVRule:
	@staticmethod
	def compute(preferences: PreferenceArray) -> RuleResult:
		# Eliminate candidates with fewest first-place votes iteratively
		n = preferences.shape[0]
		active = np.ones(5, dtype=bool)
		elimination_order: List[int] = []
		while True:
			# Compute first-choice among active for each ballot
			first_choices = []
			for row in range(n):
				for cand in preferences[row]:
					if active[cand]:
						first_choices.append(int(cand))
						break
			if not first_choices:
				return RuleResult(winner=None, aux={"elimination_order": elimination_order})
			counts = np.bincount(np.array(first_choices, dtype=np.int8), minlength=5)
			total_active_votes = counts.sum()
			if total_active_votes == 0:
				return RuleResult(winner=None, aux={"elimination_order": elimination_order})
			# Majority check
			if counts.max() * 2 > total_active_votes:
				winner = int(np.argmax(counts))
				return RuleResult(winner=winner, aux={"counts": counts.tolist(), "elimination_order": elimination_order})
			# Eliminate min (deterministic tiebreak)
			min_count = counts[active].min()
			cands_min = [c for c in range(5) if active[c] and counts[c] == min_count]
			elim = _alphabetical_tiebreak(cands_min)
			active[elim] = False
			elimination_order.append(int(elim))
			# If only one remains, they win
			if active.sum() == 1:
				winner = int(np.flatnonzero(active)[0])
				return RuleResult(winner=winner, aux={"counts": counts.tolist(), "elimination_order": elimination_order})
