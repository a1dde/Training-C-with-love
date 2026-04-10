import unittest

from progress import DEFAULT_PROGRESS


class ThemeConfigTests(unittest.TestCase):
    def test_default_theme_is_valid(self):
        self.assertIn(DEFAULT_PROGRESS["theme"], {"dark", "light"})


if __name__ == "__main__":
    unittest.main()
