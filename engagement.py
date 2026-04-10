"""Серия дней, сюжетные вставки уровней и вспомогательные проверки вовлечения."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

# Короткая сцена «стажёрский котик в Логове синтаксиса» — квест ощущается как история
LEVEL_STORY_BEATS: dict[int, str] = {
    1: "Сцена 1/10: Первый вывод в консоль — как первый шаг в офисе разработки.",
    2: "Сцена 2/10: Переменные — имена для данных, как бирки на мисках.",
    3: "Сцена 3/10: Считаем вкусняшки — int пригодится в логах и метриках.",
    4: "Сцена 4/10: bool — основа условий и флагов в реальном коде.",
    5: "Сцена 5/10: Ветвления — каждый if решает, куда пойдёт логика.",
    6: "Сцена 6/10: Циклы — перебор, без которого не обходятся парсеры и игры.",
    7: "Сцена 7/10: Массивы — первый контейнер, до List и баз данных.",
    8: "Сцена 8/10: Строки и интерполяция — как удобно собирать сообщения пользователю.",
    9: "Сцена 9/10: Методы — разбиение кода, как привычка в команде.",
    10: "Сцена 10/10: Финал главы — всё сочетается, как перед код-ревью.",
}


def touch_daily_streak(progress: dict[str, Any]) -> None:
    """Один раз в день увеличивает серию при открытии приложения или успехе."""
    today = date.today()
    today_s = today.isoformat()
    last_s = progress.get("streak_last_date")
    if last_s == today_s:
        return
    prev = int(progress.get("streak_days", 0))
    if not last_s:
        streak = 1
    else:
        try:
            last_d = date.fromisoformat(str(last_s))
        except ValueError:
            last_d = today - timedelta(days=9)
        if last_d == today - timedelta(days=1):
            streak = prev + 1 if prev > 0 else 1
        else:
            streak = 1
    progress["streak_last_date"] = today_s
    progress["streak_days"] = streak
    progress["streak_best"] = max(int(progress.get("streak_best", 0)), streak)


def normalize_engagement_fields(progress: dict[str, Any], *, level_count: int) -> None:
    """Строки/списки для новых полей прогресса."""
    if not isinstance(progress.get("levels_passed_first_try"), list):
        progress["levels_passed_first_try"] = []
    else:
        progress["levels_passed_first_try"] = sorted(
            {int(x) for x in progress["levels_passed_first_try"] if int(x) > 0 and int(x) <= level_count}
        )
    if not isinstance(progress.get("self_explain_levels"), list):
        progress["self_explain_levels"] = []
    else:
        progress["self_explain_levels"] = sorted(
            {int(x) for x in progress["self_explain_levels"] if int(x) > 0 and int(x) <= level_count}
        )
    mi = progress.get("mentor_letter_index")
    try:
        progress["mentor_letter_index"] = max(0, int(mi))
    except (TypeError, ValueError):
        progress["mentor_letter_index"] = 0
    for k in ("streak_days", "streak_best"):
        try:
            progress[k] = max(0, int(progress.get(k, 0)))
        except (TypeError, ValueError):
            progress[k] = 0
    cs = progress.get("campaign_started_at")
    if cs is not None and cs != "" and not isinstance(cs, str):
        progress["campaign_started_at"] = None
    progress["chapter_a_speedrun_done"] = bool(progress.get("chapter_a_speedrun_done"))
    progress["won_after_many_tries"] = bool(progress.get("won_after_many_tries"))
