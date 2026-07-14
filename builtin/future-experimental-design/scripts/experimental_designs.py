"""Advanced experimental designs: crossover, Latin square, repeated measures.

These designs go beyond simple randomization and factorial layouts. They handle
situations where subjects receive multiple treatments or where two blocking
factors must be controlled simultaneously.

Functions:
  crossover_design       each subject receives every treatment (with washout)
  latin_square_design    block on two sources of variation (row + column)
  repeated_measures      within-subject factor design (split-plot structure)
  randomize_run_order    utility: randomize execution order for any design

Requirements: numpy, pandas (no pyDOE3 needed for these).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from itertools import permutations


def crossover_design(treatments, n_subjects, n_periods=None, 
                     seed=0, balance="latin"):
    """Crossover design: each subject receives multiple treatments in sequence.

    In a crossover study, every subject serves as their own control by receiving
    all treatments across different periods (with a washout period between).
    This dramatically increases statistical power compared to parallel-group
    designs — you're comparing within-subject, not between-subject.

    Parameters:
        treatments: list of treatment labels, e.g. ["DrugA", "DrugB", "Placebo"]
        n_subjects: total number of subjects
        n_periods: number of periods (default: len(treatments))
        seed: random seed for reproducibility
        balance: "latin" (balanced Latin square) or "random" (random sequence per subject)

    Returns:
        DataFrame with columns: subject_id, period, treatment

    ⚠️  CRITICAL ASSUMPTIONS for crossover designs:
        1. Washout period between treatments must be sufficient
        2. No carryover effects (or they're negligible)
        3. Stable disease/trait over the study duration
        4. Subjects complete all periods (handle dropouts in analysis)
    """
    rng = np.random.default_rng(seed)
    k = len(treatments)
    if n_periods is None:
        n_periods = k
    
    if balance == "latin":
        # Build a balanced Latin square: each treatment appears exactly once
        # in each period position (column) and each subject (row).
        # For k treatments, need k subjects in the base square.
        # We repeat the square to cover n_subjects.
        base_square = _build_latin_square(treatments, seed=seed)
        rows_needed = max(n_subjects, k)
        n_repeats = (rows_needed + k - 1) // k
        full_square = np.tile(base_square, (n_repeats, 1))
        full_square = full_square[:n_subjects, :n_periods]
    else:
        # Random sequence per subject
        full_square = np.array([
            rng.permutation(treatments)[:n_periods]
            for _ in range(n_subjects)
        ])
    
    rows = []
    for i in range(n_subjects):
        for p in range(n_periods):
            rows.append({
                "subject_id": i + 1,
                "period": p + 1,
                "treatment": full_square[i, p]
            })
    
    return pd.DataFrame(rows)


def _build_latin_square(treatments, seed=0):
    """Build a balanced Latin square for crossover designs."""
    rng = np.random.default_rng(seed)
    k = len(treatments)
    # Start with a cyclic Latin square and optionally randomize
    square = np.array([
        treatments[(i + j) % k]
        for i in range(k)
        for j in range(k)
    ]).reshape(k, k)
    # Randomize row order
    row_order = rng.permutation(k)
    return square[row_order, :]


def latin_square_design(treatment_labels, n_levels=None, seed=0):
    """Latin square design: block on TWO sources of nuisance variation.

    A Latin square eliminates two blocking factors simultaneously. Classic
    example: testing k fertilizer treatments on a k×k field grid, blocking
    on both row position (north-south gradient) and column position (east-west).
    
    Each treatment appears exactly once in each row and each column.
    Total runs = k² (for k treatments).
    
    Parameters:
        treatment_labels: list of k treatment labels, e.g. ["A", "B", "C"]
        n_levels: number of levels (default: len(treatment_labels))
        seed: random seed
    
    Returns:
        DataFrame with columns: row_block, col_block, treatment
    
    ⚠️  The Latin square assumes NO interaction between blocking factors.
        If row×col interaction exists, you need a factorial or Graeco-Latin square.
    """
    rng = np.random.default_rng(seed)
    k = n_levels or len(treatment_labels)
    labels = treatment_labels
    
    if len(labels) < k:
        # Extend labels if needed
        labels = list(labels) + [f"T{i}" for i in range(len(labels) + 1, k + 1)]
    labels = labels[:k]
    
    # Build standard Latin square and randomize
    square = np.array([
        labels[(i + j) % k]
        for i in range(k)
        for j in range(k)
    ]).reshape(k, k)
    
    row_perm = rng.permutation(k)
    col_perm = rng.permutation(k)
    square = square[row_perm, :][:, col_perm]
    
    rows = []
    for i in range(k):
        for j in range(k):
            rows.append({
                "row_block": i + 1,
                "col_block": j + 1,
                "treatment": square[i, j]
            })
    
    return pd.DataFrame(rows)


def repeated_measures_design(between_subject_factors, within_subject_factors,
                              n_subjects, seed=0):
    """Repeated measures / split-plot design with within-subject factors.

    Classic scenario: you have a between-subject factor (e.g., treatment group:
    drug vs placebo) and one or more within-subject factors (e.g., time: pre,
    post, follow-up). Each subject is measured at every level of the within-subject
    factors.
    
    This is the split-plot structure:
      ┌─ Whole plot (between-subject) ─┐
      │  Subject → assigned to group   │
      │    ┌─ Subplot (within) ──┐     │
      │    │  time=0, time=1, ... │     │
      │    └──────────────────────┘     │
      └────────────────────────────────┘
    
    Parameters:
        between_subject_factors: dict mapping factor name → list of levels
            e.g. {"group": ["drug", "placebo"]}
        within_subject_factors: dict mapping factor name → list of levels
            e.g. {"time": ["pre", "post", "followup"]}
        n_subjects: total subjects (will be divided equally across between-subject groups)
        seed: random seed
    
    Returns:
        DataFrame with columns: subject_id, [between factors...], [within factors...]
    
    ⚠️  ANALYSIS NOTE: You MUST use a mixed-effects model (e.g., lmer, lme4) that
        accounts for the correlation among repeated measures on the same subject.
        Do NOT analyze this as if observations are independent (pseudoreplication!).
        The subject_id column identifies the clustering unit for the random effect.
    """
    rng = np.random.default_rng(seed)
    
    # Between-subject factor combinations
    b_names = list(between_subject_factors)
    b_levels = [between_subject_factors[n] for n in b_names]
    b_combos = _product(b_levels)
    n_groups = len(b_combos)
    subjects_per_group = max(1, n_subjects // n_groups)
    
    # Within-subject factor combinations
    w_names = list(within_subject_factors)
    w_levels = [within_subject_factors[n] for n in w_names]
    w_combos = _product(w_levels)
    
    rows = []
    subj_id = 0
    for b_combo in b_combos:
        for _ in range(subjects_per_group):
            subj_id += 1
            # Randomize within-subject order
            w_order = rng.permutation(len(w_combos))
            for w_idx in w_order:
                row = {"subject_id": subj_id}
                for j, name in enumerate(b_names):
                    row[name] = b_combo[j]
                for j, name in enumerate(w_names):
                    row[name] = w_combos[w_idx][j]
                rows.append(row)
    
    return pd.DataFrame(rows)


def _product(levels_list):
    """Cartesian product of multiple level lists."""
    import itertools
    return list(itertools.product(*levels_list))


def randomize_run_order(df, seed=0):
    """Add a randomized 'run_order' column to any design DataFrame.
    
    Essential for eliminating time/order confounds: equipment warm-up,
    reagent degradation, operator fatigue all correlate with run order.
    Randomizing breaks this correlation.
    
    Returns a new DataFrame with 'run_order' column added, sorted by run_order.
    """
    rng = np.random.default_rng(seed)
    order = rng.permutation(len(df)) + 1
    df = df.copy()
    df.insert(0, "run_order", order)
    return df.sort_values("run_order").reset_index(drop=True)


if __name__ == "__main__":
    print("=== Crossover Design (3 treatments, 12 subjects) ===")
    cd = crossover_design(["DrugA", "DrugB", "Placebo"], n_subjects=12, seed=42)
    print(cd.head(12).to_string(index=False))
    
    print("\n=== Latin Square (4 treatments) ===")
    ls = latin_square_design(["A", "B", "C", "D"], seed=42)
    print(ls.to_string(index=False))
    
    print("\n=== Repeated Measures Design ===")
    rm = repeated_measures_design(
        between_subject_factors={"group": ["drug", "placebo"]},
        within_subject_factors={"time": ["pre", "1mo", "3mo"]},
        n_subjects=20,
        seed=42
    )
    print(rm.head(18).to_string(index=False))
    print(f"\nTotal observations: {len(rm)}")
    print(f"Subjects: {rm['subject_id'].nunique()}")
