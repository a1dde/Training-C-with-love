import unittest

from csharp_compiler import compile_result_to_validation, dotnet_sdk_available
from validators import validate_level

requires_sdk = unittest.skipUnless(dotnet_sdk_available(), "requires .NET SDK (dotnet --list-sdks)")


class ValidatorTests(unittest.TestCase):
    def test_compile_errors_never_line_zero_in_ui(self):
        cr = {
            "ok": False,
            "errors": [
                {
                    "line": 0,
                    "column": 1,
                    "code": "CS1002",
                    "message": "CS1002: ; expected (2, 15)",
                }
            ],
            "hint": "test",
            "compiler_unavailable": False,
        }
        src = "line1\nConsole.WriteLine(\n"
        r = compile_result_to_validation(cr, 1, src)
        self.assertGreaterEqual(r["compile_errors"][0]["line"], 1)
        self.assertTrue(r["bad_spans"])

    def test_empty_code_does_not_invoke_dotnet(self):
        result = validate_level(1, "")
        self.assertFalse(result["ok"])
        self.assertFalse(result.get("compiler_unavailable"))

    @requires_sdk
    def test_level_one_valid(self):
        code = 'Console.WriteLine("Привет");'
        result = validate_level(1, code)
        self.assertTrue(result["ok"])
        self.assertEqual(result["score"], 100)

    @requires_sdk
    def test_level_one_missing_semicolon(self):
        code = 'Console.WriteLine("Привет")'
        result = validate_level(1, code, attempt_count=3)
        self.assertFalse(result["ok"])
        self.assertIn("compile", [x["id"] for x in result["missing_rules"]])
        self.assertNotEqual(result["hint"], "")

    @requires_sdk
    def test_level_one_requires_writeline_not_only_int(self):
        """Компилируется, но не то задание — проверяем учебные правила уровня."""
        result = validate_level(1, "int x = 1;\n", attempt_count=1)
        self.assertFalse(result["ok"])
        ids = [x["id"] for x in result["missing_rules"]]
        self.assertIn("console_write", ids)
        self.assertEqual(result["compile_errors"][0].get("code"), "MEOW_RULE")
        self.assertGreaterEqual(int(result["compile_errors"][0].get("line") or 0), 1)


if __name__ == "__main__":
    unittest.main()
