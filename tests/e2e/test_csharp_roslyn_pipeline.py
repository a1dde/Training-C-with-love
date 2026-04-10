"""Проверка цепочки MeowSyntaxCheck (Roslyn) → csharp_compiler → validators."""

from __future__ import annotations

import unittest

from csharp_compiler import analyze_csharp_source, compile_result_to_validation, dotnet_sdk_available, syntax_checker_dll
from validators import validate_level

requires_sdk = unittest.skipUnless(dotnet_sdk_available(), "requires .NET SDK (dotnet --list-sdks)")


def _has_syntax_checker() -> bool:
    return syntax_checker_dll() is not None


requires_roslyn_dll = unittest.skipUnless(_has_syntax_checker(), "build csharp_syntax_check (MeowSyntaxCheck.dll)")


@requires_sdk
@requires_roslyn_dll
class RoslynPipelineTests(unittest.TestCase):
    def test_analyze_minimal_top_level_ok(self) -> None:
        r = analyze_csharp_source('Console.WriteLine("ok");\n')
        self.assertFalse(r.get("compiler_unavailable"), r)
        self.assertTrue(r.get("ok"), r)
        self.assertEqual(r.get("errors"), [])

    def test_analyze_list_without_explicit_usings_ok(self) -> None:
        """Глобальные using в MeowSyntaxCheck — как в SDK, List доступен."""
        code = "var a = new System.Collections.Generic.List<int> { 1 };\nConsole.WriteLine(a.Count);\n"
        r = analyze_csharp_source(code)
        self.assertTrue(r.get("ok"), r.get("errors"))

    def test_analyze_missing_semicolon_error_has_line_column(self) -> None:
        r = analyze_csharp_source('Console.WriteLine("x")\n')
        self.assertFalse(r.get("ok"))
        self.assertFalse(r.get("compiler_unavailable"))
        errs = r.get("errors") or []
        self.assertTrue(errs)
        e0 = errs[0]
        self.assertGreaterEqual(int(e0.get("line", 0)), 1)
        self.assertIn("CS", str(e0.get("code", "")))

    def test_compile_result_to_validation_normalizes_lines(self) -> None:
        cr = {
            "ok": False,
            "errors": [{"line": 0, "column": 1, "code": "CS1", "message": "err (2, 3)"}],
            "hint": "x",
            "compiler_unavailable": False,
        }
        src = "a\nb\n"
        out = compile_result_to_validation(cr, 1, src)
        self.assertGreaterEqual(out["compile_errors"][0]["line"], 1)

    def test_validate_level_1_reference_succeeds(self) -> None:
        from levels_data import LEVELS

        code = str(LEVELS[0]["reference_code"])
        r = validate_level(1, code, 1)
        self.assertTrue(r["ok"], r.get("compile_errors"))
        self.assertFalse(r.get("compiler_unavailable"))


if __name__ == "__main__":
    unittest.main()
