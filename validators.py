from __future__ import annotations

from typing import Any

from csharp_compiler import analyze_csharp_source, compile_csharp_source, compile_result_to_validation
from levels_data import LEVELS, Level
from ui_helpers import kitten_tail_for_compiler_message


def _find_level(level_id: int) -> Level:
    for level in LEVELS:
        if level["id"] == level_id:
            return level
    raise ValueError(f"Unknown level_id={level_id}")


def _rule_satisfied(rule: dict[str, str], code: str) -> bool:
    kind = rule.get("kind", "contains")
    val = rule.get("value", "")
    if kind == "contains":
        return val in code
    return False


def _first_meaningful_line_number(code: str) -> int:
    """Первая непустая строка, не только // комментарий — куда указывать подсказку."""
    text = code.replace("\r\n", "\n")
    for i, line in enumerate(text.split("\n"), start=1):
        s = line.strip()
        if not s:
            continue
        if s.startswith("//"):
            continue
        return i
    return 1


def _hint_for_rule_map(hints_map: dict[str, list[str]] | None, rule_id: str, attempt: int) -> str | None:
    arr = (hints_map or {}).get(rule_id) or []
    if not arr:
        return None
    idx = min(max(attempt - 1, 0), len(arr) - 1)
    return arr[idx]


def _rule_validation_fail(
    missing: list[dict[str, str]],
    code: str,
    attempt_count: int,
    hints_map: dict[str, list[str]] | None,
) -> dict[str, Any]:
    """Код компилируется, но не выполнены условия квеста (как в задании)."""
    r0 = missing[0]
    line = _first_meaningful_line_number(code)
    hid = r0["id"]
    tail = _hint_for_rule_map(hints_map, hid, attempt_count)
    if not tail:
        tail = (
            f"Компилятор доволен, но в тексте задания нужно ещё: «{r0['label']}». "
            "Сверься с формулировкой квеста и эталоном (если смотришь)."
        )
    hint = tail
    msg = f"{r0['label']}: {tail}"
    return {
        "ok": False,
        "score": 0,
        "missing_rules": [{"id": x["id"], "label": x["label"], "token": x.get("value", "")} for x in missing],
        "good_spans": [],
        "bad_spans": [{"line": line, "start": 0, "end": 1}],
        "hint": hint,
        "compile_errors": [
            {
                "message": msg,
                "line": line,
                "column": 1,
                "code": "MEOW_RULE",
            }
        ],
        "compiler_unavailable": False,
    }


def validate_level(level_id: int, code: str, attempt_count: int = 1) -> dict[str, Any]:
    level = _find_level(level_id)
    cr = analyze_csharp_source(code)
    if cr.get("compiler_unavailable"):
        cr = compile_csharp_source(code)
    if not cr.get("ok"):
        return compile_result_to_validation(cr, attempt_count, code)

    missing = [r for r in level["rules"] if not _rule_satisfied(r, code)]
    if missing:
        return _rule_validation_fail(missing, code, attempt_count, level.get("hints"))

    return compile_result_to_validation(cr, attempt_count, code)


def validate_rules(
    rules: list[dict[str, str]],
    code: str,
    attempt_count: int = 1,
    hints_map: dict[str, list[str]] | None = None,
) -> dict[str, Any]:
    """Сначала реальная компиляция/анализ C#, затем проверка условий квеста (contains)."""
    cr = analyze_csharp_source(code)
    if cr.get("compiler_unavailable"):
        cr = compile_csharp_source(code)
    if not cr.get("ok"):
        return compile_result_to_validation(cr, attempt_count, code)

    missing = [r for r in rules if not _rule_satisfied(r, code)]
    if missing:
        return _rule_validation_fail(missing, code, attempt_count, hints_map)

    return compile_result_to_validation(cr, attempt_count, code)


def validation_status_message(result: dict[str, Any]) -> str:
    """Короткая строка для UI при неуспешной проверке."""
    if result.get("compiler_unavailable"):
        return str(result.get("hint") or "Установи .NET 8 SDK — без него котик не сможет проверить C#.")
    errs = result.get("compile_errors") or []
    if errs:
        e0 = errs[0]
        if str(e0.get("code")) == "MEOW_RULE":
            return str(e0.get("message") or result.get("hint") or "")
        msg = str(e0.get("message", "") or "")
        tail = kitten_tail_for_compiler_message(msg)
        short = msg.replace("\n", " ")[:140]
        return f"{tail} ({short})" if short else tail
    return str(result.get("hint") or "Исправь ошибки — котик ждёт 🐾")
