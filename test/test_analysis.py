import json
import unittest
import os

from app import analysis


class AnalysisTestCase(unittest.TestCase):

    def test_expected_value(self):

        counts = {"00000": 0.4, "10101": 0.3, "10000": 0.25, "11100": 0.05}
        result = analysis.calc_expected_value(counts)
        self.assertEqual(11.7, round(result, 2))

    def test_standard_deviation(self):
        counts = {"00000": 0.4, "10101": 0.3, "10000": 0.25, "11100": 0.05}
        expected_value = 11.7
        result = analysis.calc_standard_deviation(counts, expected_value)
        self.assertEqual(9.93026, round(result, 5))

    def test_percentage_error(self):
        counts_sim = {"11111": 500, "00000": 500}
        counts_real = {"11111": 350, "00000": 200, "10101": 200, "11100": 250}
        ideal_result = {"11111": 0.3, "00000": 0.6}
        result = analysis.calc_percentage_error(counts_sim, counts_real)
        self.assertEqual(ideal_result, result)

    def test_intersection(self):
        counts_sim = {"11111": 500, "00000": 500}
        counts_real = {"11111": 350, "00000": 200, "10101": 200, "11100": 250}
        result = analysis.calc_intersection(counts_sim, counts_real, 1000)
        self.assertEqual(0.55, result)

    def test_chi_square_disctance(self):
        counts_sim = {"11111": 500, "00000": 500}
        counts_real = {"11111": 350, "00000": 200, "10101": 200, "11100": 250}
        result = analysis.calc_chi_square_distance(counts_sim, counts_real)
        self.assertEqual(302.521, round(result, 3))

    def test_correlation(self):
        counts_sim = {"11111": 500, "00000": 500}
        counts_real = {"11111": 350, "00000": 200, "10101": 200, "11100": 250}
        result = analysis.calc_correlation(counts_sim, counts_real, 1000)
        self.assertEqual(0.408, round(result, 3))


if __name__ == "__main__":
    unittest.main()