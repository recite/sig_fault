"""Synthetic-control constraints, temporal separation and missing-data tests."""

import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from i4r_synthetic import annual_matrix, fit_case, fit_weights  # noqa: E402


class SyntheticTests(unittest.TestCase):
    def test_recovers_known_combination(self):
        x = np.array([[1, 7], [4, 2], [9, 3]], dtype=float)
        y = x @ np.array([0.3, 0.7])
        w = fit_weights(y, x)
        np.testing.assert_allclose(w, [0.3, 0.7], atol=1e-5)
        self.assertAlmostEqual(w.sum(), 1)
        self.assertTrue((w >= 0).all())

    def test_tiny_ridge_resolves_underdetermined_weights(self):
        rng = np.random.default_rng(37)
        x = rng.uniform(1, 10, (3, 40))
        target = x.mean(axis=1) + np.array([0.1, -0.1, 0.05])
        scale = np.sqrt(np.mean(target**2))
        z, y = x / scale, target / scale
        h = z.T @ z / 3 + 1e-6 * np.eye(40)
        system = np.block([[h, np.ones((40, 1))], [np.ones((1, 40)), np.zeros((1, 1))]])
        expected = np.linalg.solve(system, np.r_[z.T @ y / 3, 1])[:40]
        self.assertTrue((expected > 0).all())
        actual = fit_weights(target, x)
        np.testing.assert_allclose(actual, expected, atol=1e-5, rtol=0)

    def test_outside_convex_hull_is_not_extrapolated(self):
        w = fit_weights([20, 20, 20], [[1, 4], [2, 5], [3, 6]])
        np.testing.assert_allclose(w, [0, 1], atol=1e-7)

    def test_post_outcome_cannot_change_weights(self):
        x = np.array([[1, 7], [4, 2], [9, 3], [10, 8]], dtype=float)
        y = np.array([5.2, 2.6, 4.8, 12])
        initial = fit_case(y, x, 3)
        y[-1], x[-1] = 1000, [1000, 2000]
        changed = fit_case(y, x, 3)
        np.testing.assert_array_equal(initial[0], changed[0])
        np.testing.assert_array_equal(initial[1], changed[1])

    def test_holdout_not_used_in_fitting(self):
        x = np.array([[1, 7], [4, 2], [9, 3], [10, 8]], dtype=float)
        y = np.array([5.2, 2.6, 4.8, 12])
        initial = fit_case(y, x, 3)
        y[2], x[2] = 500, [10, 1000]
        changed = fit_case(y, x, 3)
        np.testing.assert_array_equal(initial[1], changed[1])
        self.assertFalse(np.allclose(initial[0], changed[0]))

    def test_gap_arithmetic(self):
        x = np.array([[1, 7], [4, 2], [9, 3], [10, 8]], dtype=float)
        y = np.array([5.2, 2.6, 4.8, 12])
        w, _, synth, d = fit_case(y, x, 3)
        np.testing.assert_allclose(synth, x @ w)
        self.assertAlmostEqual(d["post_gap"], y[-1] - synth[-1])
        self.assertAlmostEqual(d["gap_change"], d["post_gap"] - y[2] + synth[2])

    def test_missing_counts_and_short_history_fail(self):
        with self.assertRaisesRegex(ValueError, "three pre-years"):
            fit_case([1, 2, 3], [[1], [2], [3]], 2)
        with self.assertRaisesRegex(ValueError, "Incomplete annual history"):
            annual_matrix({}, ["paper"], [2020])
        with self.assertRaisesRegex(ValueError, "Missing annual counts"):
            fit_case([1, 2, 3, np.nan], [[1], [2], [3], [4]], 3)

    def test_observed_zero_is_retained(self):
        matrix = annual_matrix(
            {("paper", 2020): {"status": "complete", "citations": "0"}},
            ["paper"],
            [2020],
        )
        np.testing.assert_array_equal(matrix, [[0]])
        w = fit_weights([0, 0], [[0, 0], [0, 0]])
        np.testing.assert_allclose(w, [0.5, 0.5])


if __name__ == "__main__":
    unittest.main()
