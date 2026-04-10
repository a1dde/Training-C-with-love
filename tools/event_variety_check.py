"""Проверка разнообразия daily/weekly ивентов (офлайн quality-gate)."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from levels_data import DAILY_EVENTS, WEEKLY_EVENTS


def run_event_variety_check() -> list[str]:
    issues: list[str] = []
    if len(DAILY_EVENTS) < 2:
        issues.append("Мало daily-ивентов для разнообразия")
    if len(WEEKLY_EVENTS) < 2:
        issues.append("Мало weekly-ивентов для разнообразия")
    titles = [e["title"] for e in DAILY_EVENTS]
    if len(titles) != len(set(titles)):
        issues.append("Дублируются заголовки daily")
    wtitles = [e["title"] for e in WEEKLY_EVENTS]
    if len(wtitles) != len(set(wtitles)):
        issues.append("Дублируются заголовки weekly")
    return issues


if __name__ == "__main__":
    found = run_event_variety_check()
    if found:
        for i in found:
            print(i)
        raise SystemExit(1)
    print("event_variety_check: OK")
