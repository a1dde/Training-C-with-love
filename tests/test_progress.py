import unittest

from progress import DEFAULT_PROGRESS, lose_life, normalize_progress_state, reset_lives


class ProgressTests(unittest.TestCase):
    def test_lives_decrease_to_zero(self):
        p = dict(DEFAULT_PROGRESS)
        p["lives_current"] = 3
        self.assertEqual(lose_life(p), 2)
        self.assertEqual(lose_life(p), 1)
        self.assertEqual(lose_life(p), 0)
        self.assertEqual(lose_life(p), 0)

    def test_reset_lives(self):
        p = dict(DEFAULT_PROGRESS)
        p["lives_current"] = 0
        reset_lives(p)
        self.assertEqual(p["lives_current"], 3)

    def test_normalize_clamps_selected_level(self):
        p = dict(DEFAULT_PROGRESS)
        p["unlocked_levels"] = [1, 2]
        p["selected_level"] = 99
        normalize_progress_state(p, level_count=10)
        self.assertEqual(p["selected_level"], 2)

    def test_normalize_fixes_locked_selection(self):
        p = dict(DEFAULT_PROGRESS)
        p["unlocked_levels"] = [1]
        p["selected_level"] = 5
        normalize_progress_state(p, level_count=10)
        self.assertEqual(p["selected_level"], 1)

    def test_normalize_prunes_invalid_level_drafts(self):
        p = dict(DEFAULT_PROGRESS)
        p["level_code_drafts"] = {
            "1": "ok",
            "99": "junk",
            "x": "bad",
            "2": "level2",
        }
        normalize_progress_state(p, level_count=10)
        self.assertEqual(p["level_code_drafts"].get("1"), "ok")
        self.assertEqual(p["level_code_drafts"].get("2"), "level2")
        self.assertNotIn("99", p["level_code_drafts"])


if __name__ == "__main__":
    unittest.main()
