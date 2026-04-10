"""Сборка учебного C# через настоящий компилятор: `dotnet build` (Roslyn / MSBuild)."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from resources import bundle_dir
from ui_helpers import friendly_compiler_hint_block

# Ошибка: path(line,col): error CSxxxx: message
_MSBUILD_ERROR = re.compile(
    r"^(.+?)\(\s*(\d+)\s*,\s*(\d+)\s*\)\s*:\s*error\s+(CS\d+)\s*:\s*(.+?)\s*$",
    re.MULTILINE | re.IGNORECASE,
)
# Иногда в тексте диагностики дублируется позиция — подстраховка для строки
_LINE_IN_MESSAGE = re.compile(r"\(\s*(\d+)\s*,\s*\d+\s*\)")


def infer_line_from_message(message: str) -> int | None:
    """Извлечь номер строки из текста Roslyn/MSBuild, если в поле line пришёл 0."""
    if not message:
        return None
    m = _LINE_IN_MESSAGE.search(message)
    if m:
        return int(m.group(1))
    m = re.search(r"(?:строка|line)\s*:?\s*(\d+)", message, re.IGNORECASE)
    if m:
        return int(m.group(1))
    return None


def normalize_compile_errors(errors: list[dict[str, Any]], source: str) -> list[dict[str, Any]]:
    """1-based строки/колонки, зажатые в файл; не оставляем line=0 (ломает подсветку в Tk)."""
    lines = source.replace("\r\n", "\n").split("\n") if source else []
    nlines = max(1, len(lines))
    out: list[dict[str, Any]] = []
    for e in errors:
        d = dict(e)
        msg = str(d.get("message") or "")
        ln = int(d.get("line") or 0)
        if ln < 1:
            inferred = infer_line_from_message(msg)
            ln = inferred if inferred else 1
        ln = max(1, min(ln, nlines))
        col = int(d.get("column") or 0)
        if col < 1:
            col = 1
        d["line"] = ln
        d["column"] = col
        out.append(d)
    return out


def _subprocess_no_console() -> dict[str, Any]:
    """Без отдельного окна консоли на Windows (dotnet build не всплывает cmd)."""
    if sys.platform != "win32":
        return {}
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    if not flags:
        return {}
    return {"creationflags": flags}


def template_project_dir() -> Path:
    return bundle_dir() / "csharp_validator"


def syntax_checker_dll() -> Path | None:
    """Собранный MeowSyntaxCheck.dll (Roslyn, без MSBuild)."""
    base = bundle_dir()
    for rel in (
        ("csharp_syntax_check", "publish", "MeowSyntaxCheck.dll"),
        ("csharp_syntax_check", "bin", "Release", "net8.0", "MeowSyntaxCheck.dll"),
        ("csharp_syntax_check", "bin", "Debug", "net8.0", "MeowSyntaxCheck.dll"),
    ):
        p = base.joinpath(*rel)
        if p.is_file():
            return p
    return None


def analyze_csharp_source(source: str, timeout: float = 15.0) -> dict[str, Any]:
    """
    Быстрая проверка синтаксиса и семантики C# через Roslyn (без MSBuild / без emit).
    Диагностики совпадают с компилятором для Program.cs в учебном шаблоне.
    Если dll недоступна — compiler_unavailable=True (вызывающий код может вызвать compile_csharp_source).
    """
    dotnet = dotnet_path()
    dll = syntax_checker_dll()
    if not dotnet or not dll:
        return {
            "ok": False,
            "errors": [],
            "raw_output": "",
            "hint": "",
            "compiler_unavailable": True,
        }

    source = source.replace("\r\n", "\n").strip()
    if not source:
        return {
            "ok": False,
            "errors": [
                {
                    "line": 1,
                    "column": 1,
                    "code": "MEOW001",
                    "message": "MEOW001: Пустой файл — напиши код на C#.",
                }
            ],
            "raw_output": "",
            "hint": "Пустой код.",
            "compiler_unavailable": False,
        }

    tmp = Path(tempfile.mkdtemp(prefix="meowfast_"))
    try:
        program = tmp / "Program.cs"
        program.write_text(source + ("\n" if not source.endswith("\n") else ""), encoding="utf-8")
        proc = subprocess.run(
            [dotnet, str(dll), str(program.resolve())],
            cwd=str(dll.parent),
            env=dotnet_runtime_env(),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            **_subprocess_no_console(),
        )
        out = (proc.stdout or "").strip()
        err_text = (proc.stderr or "").strip()
        raw_combined = out + ("\n" + err_text if err_text else "")
        try:
            data = json.loads(out)
        except json.JSONDecodeError:
            return {
                "ok": False,
                "errors": [],
                "raw_output": raw_combined,
                "hint": "Не удалось разобрать ответ MeowSyntaxCheck — пересобери csharp_syntax_check (dotnet build).",
                "compiler_unavailable": True,
            }

        errors: list[dict[str, Any]] = []
        for e in data.get("errors") or []:
            code = str(e.get("code", "") or "")
            msg = str(e.get("message", "") or "")
            if code and msg and not msg.startswith(code):
                msg = f"{code}: {msg}"
            errors.append(
                {
                    "line": int(e.get("line", 1)),
                    "column": int(e.get("column", 1)),
                    "code": code,
                    "message": msg,
                }
            )
        ok = bool(data.get("ok"))
        hint = ""
        if not ok and errors:
            hint = errors[0]["message"]

        return {
            "ok": ok,
            "errors": errors,
            "raw_output": raw_combined,
            "hint": hint,
            "compiler_unavailable": False,
        }
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "errors": [],
            "raw_output": "",
            "hint": "Таймаут быстрой проверки.",
            "compiler_unavailable": True,
        }
    except OSError as e:
        return {
            "ok": False,
            "errors": [],
            "raw_output": str(e),
            "hint": str(e),
            "compiler_unavailable": True,
        }
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def bundled_dotnet_root() -> Path | None:
    """Portable SDK из комплекта приложения (лежит рядом с ресурсами после распаковки onefile)."""
    root = bundle_dir() / "bundled_dotnet"
    if (root / "dotnet.exe").is_file():
        return root
    return None


def dotnet_runtime_env() -> dict[str, str]:
    """Окружение для встроенного dotnet: не подмешивать глобальный SDK из Program Files."""
    env = dict(os.environ)
    root = bundled_dotnet_root()
    if root:
        env["DOTNET_ROOT"] = str(root)
        env["DOTNET_MULTILEVEL_LOOKUP"] = "0"
    return env


def dotnet_path() -> str | None:
    bundled = bundled_dotnet_root()
    if bundled:
        return str(bundled / "dotnet.exe")
    return shutil.which("dotnet")


def dotnet_sdk_available() -> bool:
    """True, если установлен SDK (а не только host `dotnet` без `dotnet build`)."""
    dotnet = dotnet_path()
    if not dotnet:
        return False
    try:
        proc = subprocess.run(
            [dotnet, "--list-sdks"],
            env=dotnet_runtime_env(),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=20,
            **_subprocess_no_console(),
        )
        return bool((proc.stdout or "").strip())
    except (OSError, subprocess.TimeoutExpired):
        return False


def _parse_errors(build_output: str) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    for m in _MSBUILD_ERROR.finditer(build_output):
        path, line_s, col_s, code, msg = m.groups()
        errors.append(
            {
                "file": path.strip(),
                "line": int(line_s),
                "column": int(col_s),
                "code": code,
                "message": f"{code}: {msg.strip()}",
                "severity": "error",
            }
        )
    return errors


def compile_csharp_source(source: str, timeout: float = 45.0) -> dict[str, Any]:
    """
    Возвращает:
      ok: bool — сборка Release без ошибок
      errors: список диагностик error (Roslyn)
      raw_output: сырой вывод для отладки
      hint: строка для UI при недоступном SDK или общей ошибке
      compiler_unavailable: нет dotnet или нет шаблона проекта
    """
    dotnet = dotnet_path()
    if not dotnet:
        return {
            "ok": False,
            "errors": [],
            "raw_output": "",
            "hint": "Нет компилятора C#: в exe не найден bundled_dotnet и `dotnet` не в PATH. Пересобери приложение (build_exe.ps1).",
            "compiler_unavailable": True,
        }

    proj_src = template_project_dir() / "MeowValidator.csproj"
    if not proj_src.is_file():
        return {
            "ok": False,
            "errors": [],
            "raw_output": "",
            "hint": "В приложении отсутствует шаблон csharp_validator/MeowValidator.csproj.",
            "compiler_unavailable": True,
        }

    source = source.replace("\r\n", "\n").strip()
    if not source:
        return {
            "ok": False,
            "errors": [
                {
                    "line": 1,
                    "column": 1,
                    "code": "MEOW001",
                    "message": "MEOW001: Пустой файл — напиши код на C#.",
                    "severity": "error",
                }
            ],
            "raw_output": "",
            "hint": "Пустой код.",
            "compiler_unavailable": False,
        }

    if not dotnet_sdk_available():
        return {
            "ok": False,
            "errors": [],
            "raw_output": "",
            "hint": "Нет .NET SDK (ни встроенного, ни в системе). Установи .NET 8 SDK или пересобери exe со встроенным SDK.",
            "compiler_unavailable": True,
        }

    tmp = Path(tempfile.mkdtemp(prefix="meowcs_"))
    try:
        shutil.copy2(proj_src, tmp / "MeowValidator.csproj")
        (tmp / "Program.cs").write_text(source + ("\n" if not source.endswith("\n") else ""), encoding="utf-8")

        proc = subprocess.run(
            [
                dotnet,
                "build",
                str(tmp / "MeowValidator.csproj"),
                "-c",
                "Release",
                "-v",
                "q",
                "--nologo",
                "/p:RunAnalyzers=false",
                "/p:BuildInParallel=true",
            ],
            cwd=tmp,
            env=dotnet_runtime_env(),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            **_subprocess_no_console(),
        )
        raw = (proc.stdout or "") + "\n" + (proc.stderr or "")
        errors = _parse_errors(raw)
        ok = proc.returncode == 0

        hint = ""
        if not ok and errors:
            hint = errors[0]["message"]
        elif not ok and not errors:
            hint = "Сборка не удалась. Смотри вывод компилятора в чек-листе или консоли MSBuild."
            errors = [
                {
                    "line": 1,
                    "column": 1,
                    "code": "MSB",
                    "message": raw.strip()[-2000:] if raw.strip() else "Неизвестная ошибка сборки.",
                    "severity": "error",
                }
            ]

        return {
            "ok": ok,
            "errors": errors,
            "raw_output": raw,
            "hint": hint,
            "compiler_unavailable": False,
        }
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "errors": [
                {
                    "line": 1,
                    "column": 1,
                    "code": "MEOW_TIMEOUT",
                    "message": "MEOW_TIMEOUT: компиляция заняла слишком много времени.",
                    "severity": "error",
                }
            ],
            "raw_output": "",
            "hint": "Таймаут компиляции.",
            "compiler_unavailable": False,
        }
    except OSError as e:
        return {
            "ok": False,
            "errors": [],
            "raw_output": str(e),
            "hint": f"Не удалось запустить компилятор: {e}",
            "compiler_unavailable": True,
        }
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def compile_result_to_validation(
    cr: dict[str, Any],
    attempt_count: int = 1,
    source: str = "",
) -> dict[str, Any]:
    """Приводит результат компиляции к формату, ожидаемому `app.py` / старым валидаторам."""
    if cr.get("compiler_unavailable"):
        sdk = str(cr.get("hint") or "Нет компилятора C#.")
        return {
            "ok": False,
            "score": 0,
            "missing_rules": [{"id": "sdk", "label": "Есть компилятор C# на ПК", "token": ""}],
            "good_spans": [],
            "bad_spans": [],
            "hint": f"🐾 Без .NET котик не может проверить код.\n{sdk}",
            "compile_errors": [],
            "compiler_unavailable": True,
        }

    errors = normalize_compile_errors(list(cr.get("errors") or []), source)
    ok = bool(cr.get("ok"))

    bad_spans: list[dict[str, int]] = []
    for e in errors[:10]:
        line = int(e.get("line", 1))
        col = int(e.get("column", 1))
        start = max(0, col - 1)
        bad_spans.append({"line": line, "start": start, "end": start + 1})

    good_spans: list[dict[str, int]] = []
    if ok:
        good_spans = []

    raw_hint = cr.get("hint", "")
    if not ok and raw_hint:
        hint = friendly_compiler_hint_block(raw_hint)
    elif not ok:
        hint = "Код пока с ошибкой — котик ждёт исправлений; см. чек-лист под редактором 🐾"
    else:
        hint = ""

    compile_errors_ui = [
        {
            "message": e.get("message", ""),
            "line": int(e.get("line", 1)),
            "column": int(e.get("column", 1)),
            "code": e.get("code", ""),
        }
        for e in errors[:12]
    ]

    return {
        "ok": ok,
        "score": 100 if ok else 0,
        "missing_rules": [] if ok else [{"id": "compile", "label": "Код без ошибок компилятора", "token": ""}],
        "good_spans": good_spans,
        "bad_spans": bad_spans,
        "hint": hint,
        "compile_errors": compile_errors_ui,
        "compiler_unavailable": False,
    }
