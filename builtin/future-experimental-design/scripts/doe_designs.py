"""Design-of-experiments (DOE) matrices as labeled, decoded pandas DataFrames.

pyDOE3 returns designs in *coded* units (-1/+1, or 0..k-1). Researchers want the
design in *real* factor units (temperature in C, concentration in mM) with named
columns, randomized run order, and a clear sense of what each design is for. This
module wraps pyDOE3 to do exactly that.

A `factors` spec maps factor names to their real-world levels:
  - two-level / continuous:  {"temp": (20, 60), "conc": (1, 10)}   # (low, high)
  - multi-level categorical:  {"catalyst": ["A", "B", "C"]}

Functions:
  full_factorial          every combination of given levels (cost grows fast)
  two_level_factorial     2^k full factorial (screening + interactions)
  fractional_factorial    2^(k-p) fraction (screening many factors cheaply)
  plackett_burman         very economical main-effects-only screening
  central_composite       response-surface design (curvature / optimization)
  box_behnken             response-surface design, no extreme corners
  latin_hypercube         space-filling sample for simulation / computer experiments

Each returns a DataFrame in real units; pass randomize=True (default) to also get
a randomized 'run_order'. Requires: pyDOE3, numpy, pandas.

═══ Design Selection Quick Reference ═══

 Question                                              → Design
 ─────────────────────────────────────────────────────────────────────
 Compare 2-5 predefined conditions, independent units → two_level_factorial
 Compare conditions with known noise (batch/day/site) → block_randomization
 Screen 5+ factors to find the vital few               → plackett_burman / fractional_factorial
 Quantify main effects + interactions for 3-5 factors  → two_level_factorial
 Optimize continuous factors (curvature matters)       → central_composite / box_behnken
 Explore simulation/computer model space               → latin_hypercube
 Subject receives every treatment (washout period)     → crossover (see experimental_designs.py)

═══ Yates Notation for Generators ═══

In Yates notation, each lower-case letter defines a factor column:
  'a'         = factor A alone
  'a b'       = factors A, B (full factorial, 4 runs)
  'a b c'     = factors A, B, C (full factorial, 8 runs)
  'a b c abc' = 2^(4-1) design: A, B, C measured directly, D aliased with ABC

Multi-letter tokens alias a factor with an interaction:
  'ab'  = factor aliased with A×B interaction
  'abc' = factor aliased with A×B×C interaction
  
Design Resolution (key concept from factorial_and_doe.md):
  Resolution III  — main effects confounded with 2-factor interactions
  Resolution IV   — main effects clear of 2-factor interactions
  Resolution V    — main effects AND 2-factor interactions all clear

Common generators:
  3 factors in 4 runs (2^(3-1), Res III): "a b ab"
  4 factors in 8 runs (2^(4-1), Res IV): "a b c abc"
  5 factors in 8 runs (2^(5-2), Res III): "a b c ab ac"
  5 factors in 16 runs (2^(5-1), Res V): "a b c d abcd"
  7 factors in 8 runs (2^(7-4), Res III): "a b c abc abd acd bcd"
"""

from __future__ import annotations

import importlib
import numpy as np
import pandas as pd
import sys


def _ensure_pydoe3():
    """Check for pyDOE3 and provide a helpful install hint if missing."""
    if importlib.util.find_spec("pyDOE3") is None:
        print(
            "╔══════════════════════════════════════════════════════════════╗\n"
            "║  pyDOE3 is required for DOE designs but not installed.      ║\n"
            "║                                                            ║\n"
            "║  Install with:                                             ║\n"
            "║    pip install pyDOE3                                       ║\n"
            "║    # or if PEP 668 enforced:                                ║\n"
            "║    pip install --break-system-packages pyDOE3               ║\n"
            "║    # or with uv:                                            ║\n"
            "║    uv pip install --system pyDOE3                           ║\n"
            "║                                                            ║\n"
            "║  Randomization functions (randomization.py) work without it.║\n"
            "╚══════════════════════════════════════════════════════════════╝",
            file=sys.stderr
        )
        raise ImportError("pyDOE3 is required. See install instructions above.")


def _decode_two_level(coded, factors):
    """Map a -1/+1 coded matrix to real (low/high) units per factor."""
    names = list(factors)
    out = {}
    for j, name in enumerate(names):
        lvl = factors[name]
        low, high = lvl[0], lvl[1]
        mid, half = (high + low) / 2.0, (high - low) / 2.0
        out[name] = mid + coded[:, j] * half
    return pd.DataFrame(out)


def _randomize(df, randomize, seed):
    if not randomize:
        return df.reset_index(drop=True)
    rng = np.random.default_rng(seed)
    order = rng.permutation(len(df)) + 1
    df = df.copy()
    df.insert(0, "run_order", order)
    return df.sort_values("run_order").reset_index(drop=True)


def full_factorial(factors, randomize=True, seed=0):
    """Every combination of the listed levels.

    factors values are explicit level lists, e.g.
      {"temp": [20, 40, 60], "catalyst": ["A", "B"]}  -> 3*2 = 6 runs.
    Runs = product of level counts, so this explodes quickly with many factors.
    """
    _ensure_pydoe3()
    from pyDOE3 import fullfact
    names = list(factors)
    levels = [list(factors[n]) for n in names]
    counts = [len(l) for l in levels]
    coded = fullfact(counts).astype(int)
    data = {n: [levels[j][coded[i, j]] for i in range(len(coded))]
            for j, n in enumerate(names)}
    return _randomize(pd.DataFrame(data), randomize, seed)


def two_level_factorial(factors, randomize=True, seed=0):
    """Full 2^k factorial: all main effects and all interactions, estimable.

    Each factor needs a (low, high) pair. Use for k up to ~5; beyond that the
    run count (2^k) gets expensive — switch to fractional_factorial or
    plackett_burman for screening.
    """
    _ensure_pydoe3()
    from pyDOE3 import ff2n
    coded = ff2n(len(factors))
    return _randomize(_decode_two_level(coded, factors), randomize, seed)


def fractional_factorial(factors, generator, randomize=True, seed=0):
    """2^(k-p) fractional factorial from a generator string.

    `generator` is pyDOE3's Yates notation (see module-level docstring above).
    For 4 factors in 8 runs (one of them aliased) use: "a b c abc".
    
    Each token defines a column; multi-letter tokens alias a factor with an
    interaction (this is the tradeoff — fewer runs, some effects confounded).
    Choose a higher-resolution generator if you need to separate main effects
    from two-factor interactions.
    
    Example usage:
        factors = {"A": (10, 50), "B": (100, 200), "C": (0.1, 1.0), "D": (5, 25)}
        design = fractional_factorial(factors, generator="a b c abc", seed=42)
    """
    _ensure_pydoe3()
    from pyDOE3 import fracfact
    coded = fracfact(generator)
    if coded.shape[1] != len(factors):
        raise ValueError(f"generator defines {coded.shape[1]} factors but "
                         f"{len(factors)} were named. Check your Yates notation "
                         f"(see module docstring) or adjust factor count.")
    return _randomize(_decode_two_level(coded, factors), randomize, seed)


def plackett_burman(factors, randomize=True, seed=0, min_runs=None):
    """Plackett-Burman screening design: main effects only, very few runs.

    Ideal for screening many factors to find the vital few. Two-factor interactions
    are heavily confounded with main effects, so use it to screen, not to model
    interactions.
    
    Run-count behavior (pyDOE3 pbdesign):
      k=1..7   → 8 runs    (saturated for k=7; consider min_runs=12 for error df)
      k=8..11  → 12 runs   (4 df for error when k=8)
      k=12..15 → 16 runs
    
    For k=7, pyDOE3 pbdesign returns 8 runs (saturated design — all degrees of
    freedom used for main effects, no error estimation possible). To get a proper
    non-saturated PB design, pass min_runs=12.
    
    Parameters:
        min_runs: If set, forces the design to use a PB matrix with at least
                  this many runs. E.g. plackett_burman(f7, min_runs=12) for 7
                  factors gives 12 runs (uses the 8-factor PB matrix and drops
                  one dummy column).
    """
    _ensure_pydoe3()
    from pyDOE3 import pbdesign
    n_factors = len(factors)
    
    if min_runs is not None and min_runs < n_factors + 1:
        print(f"Warning: min_runs={min_runs} is too low for {n_factors} factors "
              f"(need at least {n_factors + 1}). Using {n_factors + 1} instead.",
              file=sys.stderr)
        min_runs = n_factors + 1
    
    if min_runs is not None:
        # Find the smallest number of "total factors" (including dummies) that
        # produces a PB matrix with >= min_runs rows.
        # pbdesign(k) for k up to 7 gives 8 runs; k=8-11 gives 12; k=12-15 gives 16.
        # We search upward until we find a design with enough rows.
        target_n_factors = n_factors
        while True:
            coded_test = pbdesign(target_n_factors)
            if coded_test.shape[0] >= min_runs:
                break
            target_n_factors += 1
        coded = pbdesign(target_n_factors)
        coded = coded[:, :n_factors]  # drop dummy columns beyond our factors
    else:
        coded = pbdesign(n_factors)
        coded = coded[:, :n_factors]
    
    return _randomize(_decode_two_level(coded, factors), randomize, seed)


def central_composite(factors, center=(0, 1), alpha="orthogonal",
                      face="inscribed", randomize=True, seed=0):
    """Central composite design (CCD) for response-surface / optimization work.

    Adds axial ("star") points and center points to a 2^k factorial so you can fit
    a quadratic model and locate an optimum.
    
    ⚠️  AXIAL POINT WARNING: The default face='inscribed' keeps axial points
    WITHIN your stated (low, high) range — recommended for most practical work.
    If you use face='circumscribed', axial points WILL exceed your stated factor
    ranges (e.g. conc_mM=(1,10) might produce values like -1.6 and 12.6). Only
    use 'circumscribed' when your equipment can safely operate beyond your
    intended range and you want a larger design space for better model estimation.
    
    Face options:
      'inscribed'      — axial points stay inside (low, high) [DEFAULT, safest]
      'circumscribed'  — axial points go OUTSIDE (low, high) for wider coverage
      'faced'          — axial points sit exactly at (low, high) faces
    
    `center` = (n center pts in factorial block, n in axial block).
    
    Example:
        design = central_composite({"temp_C": (20, 60), "conc_mM": (1, 10)}, seed=42)
    """
    _ensure_pydoe3()
    from pyDOE3 import ccdesign
    
    if face == "circumscribed":
        # Warn about axial points exceeding factor ranges
        names = list(factors)
        for name in names:
            lo, hi = factors[name]
            alpha_val = 1.414  # approximate alpha for orthogonal 2-factor CCD
            ax_lo = (hi + lo) / 2.0 - (hi - lo) / 2.0 * alpha_val
            ax_hi = (hi + lo) / 2.0 + (hi - lo) / 2.0 * alpha_val
            if ax_lo < lo:
                print(f"⚠️  {name}: axial point ({ax_lo:.2f}) < stated low ({lo}). "
                      f"Consider face='inscribed' to stay within range.",
                      file=sys.stderr)
            if ax_hi > hi:
                print(f"⚠️  {name}: axial point ({ax_hi:.2f}) > stated high ({hi}). "
                      f"Consider face='inscribed' to stay within range.",
                      file=sys.stderr)
    
    coded = ccdesign(len(factors), center=center, alpha=alpha, face=face)
    return _randomize(_decode_two_level(coded, factors), randomize, seed)


def box_behnken(factors, center=1, randomize=True, seed=0):
    """Box-Behnken response-surface design (needs >= 3 factors).

    Like a CCD it fits a quadratic, but it never uses the extreme corner
    combinations (all-low or all-high), which is useful when those corners are
    unsafe or infeasible. More economical than a CCD for 3-5 factors.
    """
    _ensure_pydoe3()
    from pyDOE3 import bbdesign
    if len(factors) < 3:
        raise ValueError("box_behnken requires at least 3 factors")
    coded = bbdesign(len(factors), center=center)
    return _randomize(_decode_two_level(coded, factors), randomize, seed)


def latin_hypercube(factors, n_samples, criterion="maximin", seed=0,
                    randomize=False):
    """Space-filling Latin hypercube sample over continuous factor ranges.

    For computer experiments / simulations where you want even coverage of a
    high-dimensional space with relatively few points. Each factor needs a
    (low, high) range. `criterion`: 'maximin' spreads points apart;
    'center'/'centermaximin'/'correlation' are alternatives.
    """
    _ensure_pydoe3()
    from pyDOE3 import lhs
    rng_state = int(seed)  # pyDOE3 lhs uses numpy global RNG; seed it for repeatability
    np.random.seed(rng_state)
    names = list(factors)
    unit = lhs(len(names), samples=n_samples, criterion=criterion)  # in [0,1]
    out = {}
    for j, n in enumerate(names):
        low, high = factors[n][0], factors[n][1]
        out[n] = low + unit[:, j] * (high - low)
    df = pd.DataFrame(out)
    return _randomize(df, randomize, seed)


if __name__ == "__main__":
    f2 = {"temp": (20, 60), "conc": (1, 10), "ph": (6, 8)}

    print("== 2^3 full factorial ==")
    print(two_level_factorial(f2, seed=1).to_string(index=False))

    print("\n== fractional 2^(4-1), generator 'a b c abc' ==")
    f4 = {"A": (-1, 1), "B": (-1, 1), "C": (-1, 1), "D": (-1, 1)}
    print(fractional_factorial(f4, "a b c abc", seed=1).to_string(index=False))

    print("\n== Plackett-Burman screening, 7 factors with min_runs=12 ==")
    f7 = {f"x{i}": (0, 1) for i in range(1, 8)}
    print(f"runs = {len(plackett_burman(f7, min_runs=12, randomize=False))}")

    print("\n== central composite (2 factors, inscribed) ==")
    print(central_composite({"temp": (20, 60), "conc": (1, 10)}, seed=1).round(2).to_string(index=False))

    print("\n== Latin hypercube, 8 samples over 3 factors ==")
    print(latin_hypercube(f2, 8, seed=1).round(2).to_string(index=False))
