import unittest

from csharp_compiler import dotnet_sdk_available
from levels_data import BOSS_CHOICES, DAILY_EVENTS, WEEKLY_EVENTS
from validators import validate_rules

requires_sdk = unittest.skipUnless(dotnet_sdk_available(), "requires .NET SDK (dotnet --list-sdks)")


@requires_sdk
class BossAndEventsFlowTests(unittest.TestCase):
    def test_boss_reference_codes_pass(self):
        for boss in BOSS_CHOICES:
            result = validate_rules(boss["rules"], str(boss["reference_code"]))
            self.assertTrue(result["ok"], boss["id"])

    def test_daily_rules_can_be_satisfied(self):
        sample = "int x = 1;\nConsole.WriteLine(x);\n"
        result = validate_rules(DAILY_EVENTS[0]["rules"], sample)
        self.assertTrue(result["ok"])

    def test_weekly_rules_can_be_satisfied(self):
        sample = "for (int i = 0; i < 1; i++) { if (i == 0) { Console.WriteLine(i); } }\n"
        result = validate_rules(WEEKLY_EVENTS[0]["rules"], sample)
        self.assertTrue(result["ok"])


if __name__ == "__main__":
    unittest.main()
