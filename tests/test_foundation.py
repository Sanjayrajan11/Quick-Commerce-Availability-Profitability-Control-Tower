import unittest
from src.utils import format_inr, ratio


class ConfigurationFoundationTests(unittest.TestCase):
    def test_indian_grouping(self):
        self.assertEqual(format_inr(12500000), "₹1,25,00,000")

    def test_negative_value(self):
        self.assertEqual(format_inr(-125000), "-₹1,25,000")

    def test_decimal_rounding(self):
        self.assertEqual(format_inr(1250.567, 2), "₹1,250.57")

    def test_empty_denominator(self):
        self.assertEqual(ratio(0, 0), 0)

    def test_valid_ratio(self):
        self.assertEqual(ratio(3, 4), 0.75)

    def test_undefined_currency(self):
        self.assertEqual(format_inr(float("nan")), "Not available")


if __name__ == "__main__":
    unittest.main()
