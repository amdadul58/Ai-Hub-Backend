import unittest

from src.traffic_intelligence.anpr.saudi_plate_mapping import (
    latin_to_arabic,
    LATIN_TO_ARABIC,
    WESTERN_TO_ARABIC_DIGITS,
)


class TestSaudiPlateMapping(unittest.TestCase):

    def test_valid_plate(self):
        self.assertEqual(latin_to_arabic("6251EJA"), "احع ٦٢٥١")

    def test_lowercase_input(self):
        self.assertEqual(latin_to_arabic("6251eja"), "احع ٦٢٥١")

    def test_unsupported_letter(self):
        with self.assertRaises(ValueError):
            latin_to_arabic("6251ABC")

    def test_invalid_digit_section(self):
        with self.assertRaises(ValueError):
            latin_to_arabic("62A1EJA")

    def test_short_input(self):
        with self.assertRaises(ValueError):
            latin_to_arabic("123")

    def test_mapping_counts(self):
        self.assertEqual(len(LATIN_TO_ARABIC), 17)
        self.assertEqual(len(WESTERN_TO_ARABIC_DIGITS), 10)


if __name__ == "__main__":
    unittest.main(verbosity=2)
