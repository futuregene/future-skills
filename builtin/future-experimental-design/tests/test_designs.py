"""Offline scientific invariants; no real subjects or external services."""
from pathlib import Path
import sys
import unittest

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from experimental_designs import repeated_measures_design
from randomization import stratified_block_randomization


class RepeatedMeasuresTests(unittest.TestCase):
    def design(self, n, seed=42, **kwargs):
        return repeated_measures_design(
            {"group": ["drug", "placebo", "other"]},
            {"time": ["pre", "post", "followup"]}, n, seed=seed, **kwargs)

    def test_exact_subject_counts_and_balanced_assignments(self):
        for n in range(1, 40):
            with self.subTest(n=n):
                df = self.design(n)
                self.assertEqual(df.subject_id.nunique(), n)
                self.assertEqual(len(df), 3 * n)
                subjects = df.groupby("subject_id").first()
                counts = subjects.group.value_counts().reindex(
                    ["drug", "placebo", "other"], fill_value=0)
                self.assertLessEqual(counts.max() - counts.min(), 1)
                self.assertTrue((df.groupby("subject_id").group.nunique() == 1).all())

    def test_seed_controls_between_subject_assignments(self):
        pd.testing.assert_frame_equal(self.design(30, 1), self.design(30, 1))
        a = self.design(30, 1).groupby("subject_id").group.first()
        b = self.design(30, 2).groupby("subject_id").group.first()
        self.assertFalse(a.equals(b))

    def test_measurement_times_are_not_shuffled_by_default(self):
        df = self.design(8)
        for _, subject in df.groupby("subject_id"):
            self.assertEqual(subject.time.tolist(), ["pre", "post", "followup"])
        shuffled = self.design(8, randomize_within=True)
        self.assertFalse(df.equals(shuffled))
        pd.testing.assert_frame_equal(shuffled, self.design(8, randomize_within=True))

    def test_invalid_inputs_are_rejected(self):
        for n in [0, -1, 1.5, True]:
            with self.subTest(n=n), self.assertRaises(ValueError):
                self.design(n)
        for between, within in [({"a": []}, {"b": [1]}),
                                ({"a": [1]}, {"a": [2]}),
                                ({"subject_id": [1]}, {"b": [2]})]:
            with self.assertRaises(ValueError):
                repeated_measures_design(between, within, 3)


class StratifiedIdentityTests(unittest.TestCase):
    def test_interleaved_labels_keep_original_unit_identity(self):
        labels = ["B", "A", "B", "A", "C", "B", "C"]
        df = stratified_block_randomization(labels, seed=42)
        self.assertEqual(df.unit_id.tolist(), list(range(1, 8)))
        self.assertEqual(df.stratum.tolist(), labels)
        pd.testing.assert_frame_equal(df, stratified_block_randomization(labels, seed=42))

    def test_count_input_and_empty_input(self):
        df = stratified_block_randomization({"B": 4, "A": 6}, seed=42)
        self.assertEqual(df.stratum.tolist(), ["B"] * 4 + ["A"] * 6)
        self.assertEqual(df.unit_id.tolist(), list(range(1, 11)))
        for labels in [[], {}, {"A": 0}]:
            self.assertTrue(stratified_block_randomization(labels).empty)
        with self.assertRaises(ValueError):
            stratified_block_randomization({"A": 1.5})


if __name__ == "__main__":
    unittest.main()
