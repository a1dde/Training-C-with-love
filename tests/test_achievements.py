import unittest

from achievements import update_achievements
from progress import DEFAULT_PROGRESS


class AchievementTests(unittest.TestCase):
    def test_first_level_achievement(self):
        p = dict(DEFAULT_PROGRESS)
        p["completed_levels"] = [1]
        new_items = update_achievements(p)
        self.assertIn("Первая лапка", new_items)

    def test_boss_achievement(self):
        p = dict(DEFAULT_PROGRESS)
        p["completed_bosses"] = ["boss_logic_cat"]
        new_items = update_achievements(p)
        self.assertIn("Босс повержен", new_items)


if __name__ == "__main__":
    unittest.main()
