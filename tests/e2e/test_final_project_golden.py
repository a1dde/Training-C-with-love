import unittest

from csharp_compiler import dotnet_sdk_available
from levels_data import FINAL_PROJECT_TRACKS
from validators import validate_rules

requires_sdk = unittest.skipUnless(dotnet_sdk_available(), "requires .NET SDK (dotnet --list-sdks)")


@requires_sdk
class FinalProjectGoldenTests(unittest.TestCase):
    def test_each_track_reference_passes(self):
        for track in FINAL_PROJECT_TRACKS:
            with self.subTest(track=track["id"]):
                result = validate_rules(track["rules"], str(track["reference_code"]), 1, {})
                self.assertTrue(result["ok"], msg=str(track["id"]))


if __name__ == "__main__":
    unittest.main()
