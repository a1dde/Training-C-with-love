import unittest

from engagement_content import weekly_digest_text
from progress import DEFAULT_PROGRESS


class EngagementContentTests(unittest.TestCase):
    def test_digest_contains_stats(self):
        t = weekly_digest_text(dict(DEFAULT_PROGRESS))
        self.assertIn("Пройдено", t)
        self.assertIn("очки", t.lower())


if __name__ == "__main__":
    unittest.main()
