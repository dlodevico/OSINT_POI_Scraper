import unittest

from src.main import filter_positive_results


class FilterPositiveResultsTests(unittest.TestCase):
    def test_filters_only_active_results(self):
        results = [
            ("GitHub", "https://github.com/example", "Active"),
            ("Twitter/X", "https://twitter.com/example", "Not Found"),
            ("Instagram", "https://www.instagram.com/example/", "Active"),
        ]

        filtered = filter_positive_results(results)

        self.assertEqual(len(filtered), 2)
        self.assertEqual(filtered[0][0], "GitHub")
        self.assertEqual(filtered[1][0], "Instagram")


if __name__ == "__main__":
    unittest.main()
