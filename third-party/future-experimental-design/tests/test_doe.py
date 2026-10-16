"""Reproducibility and design-matrix invariants for supported dependencies."""
from pathlib import Path
import sys
import unittest

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from doe_designs import (latin_hypercube, fractional_factorial,
                         plackett_burman, central_composite)
from randomization import block_randomization, simple_randomization


class DoeTests(unittest.TestCase):
    def test_lhs_is_reproducible_bounded_and_stratified(self):
        factors = {"x": (0, 1), "y": (10, 20)}
        for seed in [0, 1, 42]:
            a = latin_hypercube(factors, 16, seed=seed)
            pd.testing.assert_frame_equal(a, latin_hypercube(factors, 16, seed=seed))
            for name, (lo, hi) in factors.items():
                unit = (a[name].to_numpy() - lo) / (hi - lo)
                self.assertTrue(((unit >= 0) & (unit <= 1)).all())
                self.assertEqual(sorted(np.floor(unit * 16).astype(int)), list(range(16)))
        self.assertFalse(latin_hypercube(factors, 16, seed=1).equals(
            latin_hypercube(factors, 16, seed=2)))

    def test_lhs_does_not_mutate_numpy_global_rng(self):
        np.random.seed(123)
        expected = np.random.random(4)
        np.random.seed(123)
        latin_hypercube({"x": (0, 1)}, 8, seed=42)
        np.testing.assert_array_equal(np.random.random(4), expected)

    def test_documented_seven_factor_generator_is_full_rank(self):
        df = fractional_factorial({k: (-1, 1) for k in "ABCDEFG"},
                                  "a b ab c ac bc abc", randomize=False)
        self.assertEqual(df.shape, (8, 7))
        matrix = np.column_stack([np.ones(8), df.to_numpy()])
        self.assertEqual(np.linalg.matrix_rank(matrix), 8)
        np.testing.assert_allclose(matrix.T @ matrix, np.eye(8) * 8)

    def test_pb_dimensions_and_residual_df(self):
        for k, rows in [(1, 4), (3, 4), (4, 8), (7, 8), (8, 12)]:
            df = plackett_burman({str(i): (-1, 1) for i in range(k)}, randomize=False)
            self.assertEqual(df.shape, (rows, k))
            matrix = np.column_stack([np.ones(rows), df.to_numpy()])
            np.testing.assert_allclose(matrix.T @ matrix, np.eye(k + 1) * rows)
        df = plackett_burman({str(i): (0, 1) for i in range(7)}, min_runs=12)
        self.assertEqual(len(df), 12)

    def test_inscribed_ccd_stays_inside_factor_ranges(self):
        factors = {"temp": (20, 60), "conc": (1, 10), "pH": (6, 8)}
        df = central_composite(factors)
        for name, (lo, hi) in factors.items():
            self.assertTrue(df[name].between(lo, hi).all())

    def test_invalid_design_inputs(self):
        for factors in [{}, {"x": (1, 0)}, {"x": (1, 1)}, {"x": (0, np.inf)}, {"x": (0, 1, 2)}]:
            with self.assertRaises(ValueError):
                latin_hypercube(factors, 4)
        for n in [0, -1, 1.5, True]:
            with self.assertRaises(ValueError):
                latin_hypercube({"x": (0, 1)}, n)
            with self.assertRaises(ValueError):
                plackett_burman({"x": (0, 1)}, min_runs=n)


class AllocationValidationTests(unittest.TestCase):
    def test_invalid_ratios_counts_and_arms(self):
        for fn in [simple_randomization, block_randomization]:
            for ratio in [(1.9, 1.1), (True, 1), (0, 1), (-1, 1), (1,)]:
                with self.subTest(fn=fn.__name__, ratio=ratio), self.assertRaises(ValueError):
                    fn(6, ratio=ratio)
            for arms in [[], ["A", "A"]]:
                with self.assertRaises(ValueError):
                    fn(6, arms=arms)
            for n in [-1, 1.5, True]:
                with self.assertRaises(ValueError):
                    fn(n)
        for block_size in [0, -2, 1.5, True, 3]:
            with self.assertRaises(ValueError):
                block_randomization(6, block_size=block_size)

    def test_complete_blocks_respect_ratio(self):
        df = block_randomization(60, ratio=(2, 1), block_size=6, seed=42)
        for _, block in df.groupby("block"):
            self.assertEqual(block.arm.value_counts().to_dict(), {"treatment": 4, "control": 2})
        self.assertTrue(block_randomization(0).empty)


if __name__ == "__main__":
    unittest.main()
