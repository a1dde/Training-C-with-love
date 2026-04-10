import unittest

from progress import DEFAULT_PROGRESS, lose_life, reset_lives


class ProgressFlowE2E(unittest.TestCase):
    def test_lose_then_reset_lives_flow(self):
        p = dict(DEFAULT_PROGRESS)
        lose_life(p)
        lose_life(p)
        lose_life(p)
        self.assertEqual(p["lives_current"], 0)
        reset_lives(p)
        self.assertEqual(p["lives_current"], p["lives_max"])


if __name__ == "__main__":
    unittest.main()
