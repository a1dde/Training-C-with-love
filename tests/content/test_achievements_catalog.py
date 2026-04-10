import unittest

from achievements import ACHIEVEMENTS, achievement_catalog_rows
from progress import DEFAULT_PROGRESS


class AchievementsCatalogTests(unittest.TestCase):
    def test_catalog_has_30_items(self):
        self.assertEqual(len(ACHIEVEMENTS), 30)

    def test_every_achievement_has_category_and_rarity(self):
        for ach_id, meta in ACHIEVEMENTS.items():
            self.assertIn("category", meta, ach_id)
            self.assertIn("rarity", meta, ach_id)
            self.assertTrue(meta["title"])

    def test_ui_catalog_has_30_rows(self):
        rows = achievement_catalog_rows(dict(DEFAULT_PROGRESS))
        self.assertEqual(len(rows), 30)

    def test_catalog_row_shape(self):
        rows = achievement_catalog_rows(dict(DEFAULT_PROGRESS))
        for row in rows:
            self.assertIn("progress_pct", row)
            self.assertIn(row["id"], ACHIEVEMENTS)


if __name__ == "__main__":
    unittest.main()
