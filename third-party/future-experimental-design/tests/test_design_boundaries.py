"""Regression tests for unit identity and honest design semantics."""
from pathlib import Path
import sys
import unittest

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from experimental_designs import crossover_design, latin_square_design
from randomization import cluster_randomization


class DesignBoundaryTests(unittest.TestCase):
    def test_duplicate_or_missing_clusters_cannot_receive_conflicting_arms(self):
        for clusters in [["clinic1", "clinic1"], ["clinic1", None], [np.nan], -1, True]:
            with self.subTest(clusters=clusters), self.assertRaises(ValueError):
                cluster_randomization(clusters)
        self.assertEqual(len(cluster_randomization(np.int64(4))), 4)
        self.assertEqual(len(cluster_randomization(0)), 0)

    def test_latin_square_never_invents_or_discards_treatments(self):
        for labels, levels in [(["A", "B"], 3), (["A", "B"], 1),
                               (["A", "B"], 0), (["A", "A"], None),
                               ([], None), (["A"], True), (["A", "B"], 2.0)]:
            with self.subTest(labels=labels, levels=levels), self.assertRaises(ValueError):
                latin_square_design(labels, n_levels=levels)
        square = latin_square_design(["A", "B", "C"], n_levels=3)
        self.assertEqual(set(square.treatment), {"A", "B", "C"})
        for block in ["row_block", "col_block"]:
            self.assertTrue((square.groupby(block).treatment.nunique() == 3).all())

    def test_crossover_input_errors_are_explicit(self):
        for kwargs in [{"n_subjects": 0}, {"n_subjects": True},
                       {"n_periods": 4}, {"n_periods": 0}, {"n_periods": 1.5},
                       {"balance": "typo"}, {"treatments": []},
                       {"treatments": ["A", "A"]}]:
            args = {"treatments": ["A", "B", "C"], "n_subjects": 6, **kwargs}
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                crossover_design(**args)

    def test_crossover_complete_sets_balance_periods_and_reproduce(self):
        for balance in ["latin", "random"]:
            frame = crossover_design(["A", "B", "C"], 12, seed=42, balance=balance)
            pd.testing.assert_frame_equal(frame, crossover_design(
                ["A", "B", "C"], 12, seed=42, balance=balance))
            self.assertEqual(len(frame), 36)
            self.assertTrue((frame.groupby("subject_id").treatment.nunique() == 3).all())
            if balance == "latin":
                self.assertTrue((frame.groupby(["period", "treatment"]).size() == 4).all())
        partial = crossover_design(["A", "B", "C"], 5, n_periods=2)
        self.assertEqual(len(partial), 10)


if __name__ == "__main__":
    unittest.main()
