import unittest

from csharp_compiler import dotnet_sdk_available
from levels_data import LEVELS
from validators import validate_level

requires_sdk = unittest.skipUnless(dotnet_sdk_available(), "requires .NET SDK (dotnet --list-sdks)")


@requires_sdk
class AllLevelsGoldenTests(unittest.TestCase):
    def test_reference_solutions_compile_each_level(self):
        for level in LEVELS:
            with self.subTest(level=level["id"]):
                code = str(level["reference_code"])
                result = validate_level(level["id"], code, attempt_count=1)
                self.assertTrue(result["ok"], f"Level {level['id']}: {result.get('compile_errors')}")


if __name__ == "__main__":
    unittest.main()
