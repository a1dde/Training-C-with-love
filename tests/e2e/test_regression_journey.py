import unittest

from achievements import update_achievements
from progress import DEFAULT_PROGRESS, finalize_chapter_and_project, milestone_caption
from csharp_compiler import dotnet_sdk_available
from validators import validate_level

requires_sdk = unittest.skipUnless(dotnet_sdk_available(), "requires .NET SDK (dotnet --list-sdks)")


class RegressionJourneyTests(unittest.TestCase):
    def test_unlock_final_project_at_8_levels(self):
        p = dict(DEFAULT_PROGRESS)
        p["completed_levels"] = list(range(1, 9))
        finalize_chapter_and_project(p, total_levels=10, unlock_threshold=8)
        self.assertTrue(p["final_project_unlocked"])

    def test_milestone_string(self):
        p = dict(DEFAULT_PROGRESS)
        self.assertIn("финального проекта", milestone_caption(p).lower())

    def test_soft_mode_progress_preserved(self):
        p = dict(DEFAULT_PROGRESS)
        p["soft_mode_no_lives"] = True
        p["completed_levels"] = [1]
        update_achievements(p)
        self.assertIsInstance(p.get("achievements"), list)

    @requires_sdk
    def test_level_1_validate(self):
        r = validate_level(1, 'Console.WriteLine("x");', 1)
        self.assertTrue(r["ok"])


if __name__ == "__main__":
    unittest.main()
