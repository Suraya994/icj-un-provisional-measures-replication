import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))
from compute_intercoder_agreement import cohen_kappa, gwet_ac1, observed_agreement  # noqa: E402
from replication_utils import parse_parties, is_p5  # noqa: E402


class AgreementMetrics(unittest.TestCase):
    """Toy arrays only. These tests contain no research data."""

    def test_perfect_agreement(self):
        a = list("0122330")
        self.assertEqual(observed_agreement(a, a), 1.0)
        self.assertAlmostEqual(cohen_kappa(a, a), 1.0)
        self.assertAlmostEqual(gwet_ac1(a, a), 1.0)

    def test_known_kappa(self):
        # 2x2 textbook case: po = 0.7, pe = 0.5, kappa = 0.4
        a = ["1"] * 5 + ["0"] * 5
        b = ["1"] * 4 + ["0"] + ["1"] * 2 + ["0"] * 3
        self.assertAlmostEqual(observed_agreement(a, b), 0.7)
        self.assertAlmostEqual(cohen_kappa(a, b), 0.4)

    def test_degenerate_kappa_is_nan(self):
        self.assertTrue(math.isnan(cohen_kappa(["2"] * 4, ["2"] * 4)))


class TitleParsing(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(parse_parties("Some Case (Ukraine v. Russian Federation)"), ("Ukraine", "Russian Federation"))
        self.assertEqual(parse_parties("No parties here"), (None, None))
        self.assertTrue(is_p5("United States of America"))
        self.assertFalse(is_p5("Israel"))


if __name__ == "__main__":
    unittest.main()
