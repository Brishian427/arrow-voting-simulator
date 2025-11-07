# Experimental Setting: Progressive Elections Under Multiple Voting Rules

## Objective

Generate high-quality, unbiased training data that reveals how election winners evolve as voters are progressively added to an election, comparing four different voting rules: **Plurality**, **Borda**, **Condorcet**, and **IRV (Instant-Runoff Voting)**.

## Experimental Components

### Candidates and Voters

- **Five candidates** labeled A, B, C, D, E
- Each voter provides a **complete ranking** (full preference order) of all five candidates
- Voter preferences are generated to be **uniformly random** over all 120 possible rankings

### Preference Generation (Randomness Guarantee)

- All 120 possible rankings of 5 candidates are pre-generated
- Each voter's preference is selected by uniformly sampling from these 120 rankings using a high-quality pseudorandom number generator (NumPy's PCG64)
- This ensures that over many voters, each ranking appears with equal probability (1/120)

**Validation**: The system includes statistical tests to verify:
- Uniform distribution: Each of the 120 rankings appears approximately equally often
- Pairwise balance: For any candidate pair, preferences are split roughly 50-50
- Independence: Consecutive runs produce uncorrelated results

### Simulation Structure

**Independent Runs**: We perform 1,000 completely independent simulation runs. Each run is a separate experiment that starts fresh.

**Progressive Voter Addition**: Within each run:
1. Start with 1 voter
2. Compute winners under all 4 voting rules
3. Add a second voter
4. Recompute winners with 2 voters
5. Continue until N voters (default: 500)
6. Record results at every step

**Result**: Each run produces 500 recorded "election states" (one for each voter count from 1 to 500), yielding 500,000 total election states across all runs.

### Voting Rules (Precise Definitions)

1. **Plurality**: Winner is the candidate with the most first-place votes. Ties broken alphabetically (A < B < C < D < E).

2. **Borda**: Each ranking position earns points: 4 points for 1st place, 3 for 2nd, 2 for 3rd, 1 for 4th, 0 for 5th. Candidate with highest total points wins. Total points across all candidates must equal 10 × number_of_voters. Ties broken alphabetically.

3. **Condorcet**: For every pair of candidates, determine how many voters prefer one over the other. A Condorcet winner must beat every other candidate in head-to-head comparison (receives more than 50% of pairwise votes). If no such candidate exists, the Condorcet winner is recorded as "None" (Condorcet paradox).

4. **IRV (Hare/Instant-Runoff)**: 
   - Count first-place votes
   - If a candidate has >50% of first-place votes, they win
   - Otherwise, eliminate the candidate with fewest first-place votes
   - Redistribute eliminated candidate's votes to each voter's next-ranked active candidate
   - Repeat until a majority winner emerges
   - Ties in elimination broken alphabetically

**Important**: All rules use deterministic alphabetical tiebreaking (A beats B beats C beats D beats E) to ensure reproducibility.

### Data Recording

For every step in every run, we record:
- **Run identifier**: Which simulation run (1-1000)
- **Step number**: Number of voters aggregated so far (1-500)
- **All voter preferences**: Complete history of all rankings up to this step (stored as integers 0-4 representing candidates A-E)
- **Winners**: The winning candidate (or None for Condorcet) under each of the 4 voting rules

### Scale and Reproducibility

- **Default scale**: 1,000 runs × 500 steps = 500,000 data points
- **Reproducibility**: All random generation can be seeded with a fixed seed value, producing identical results across runs

### Research Questions This Setting Addresses

1. How do different voting rules behave as the electorate grows?
2. How often do voting rules agree on the winner?
3. How frequently do winners change as new voters are added?
4. What is the probability that a Condorcet winner exists, and how does it depend on the number of voters?
5. Do certain candidates win more frequently under specific rules (due to tiebreaking bias)?

## Design Rationale

- **Unbiased inputs**: Uniform random preferences ensure no candidate has inherent advantage
- **Progressive observation**: We observe elections at every possible electorate size, not just the final size
- **Comparable conditions**: All voting rules operate on identical voter preferences
- **Deterministic tiebreaking**: Eliminates ambiguity while maintaining reproducibility

## Limitations and Notes

- Real-world electorates are not uniformly random; this simulation isolates voting rule behavior without social structures
- Alphabetical tiebreaking may create minimal systematic advantages, but this is documented and deterministic
- Condorcet "None" results reflect genuine preference cycles, not errors

