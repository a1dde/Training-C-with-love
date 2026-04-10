from __future__ import annotations

from typing import Any, Callable, TypedDict

from engagement_content import MENTOR_LETTERS


class AchievementMeta(TypedDict):
    title: str
    category: str
    rarity: str
    check: Callable[[dict[str, Any]], bool]


def _levels(progress: dict[str, Any]) -> int:
    return len(progress.get("completed_levels", []))


def _bosses(progress: dict[str, Any]) -> int:
    return len(progress.get("completed_bosses", []))


def _dailies(progress: dict[str, Any]) -> int:
    return int(progress.get("daily_events_done", 0))


def _first_try_levels(progress: dict[str, Any]) -> int:
    return len(progress.get("levels_passed_first_try") or [])


def _streak_days(progress: dict[str, Any]) -> int:
    return int(progress.get("streak_days", 0))


def _mentor_read_all(progress: dict[str, Any]) -> bool:
    return int(progress.get("mentor_letter_index", 0)) >= len(MENTOR_LETTERS)


ACHIEVEMENTS: dict[str, AchievementMeta] = {
    "ach_001": {"title": "Первая лапка", "category": "story", "rarity": "обычное", "check": lambda p: _levels(p) >= 1},
    "ach_002": {"title": "Пушистый старт", "category": "story", "rarity": "обычное", "check": lambda p: _levels(p) >= 3},
    "ach_003": {"title": "Десять муров", "category": "story", "rarity": "обычное", "check": lambda p: _levels(p) >= 10},
    "ach_004": {"title": "Глава закрыта", "category": "story", "rarity": "обычное", "check": lambda p: _levels(p) >= 10},
    "ach_005": {"title": "Лапки без паники", "category": "quality", "rarity": "обычное", "check": lambda p: int(p.get("kitten_points", 0)) >= 20},
    "ach_006": {"title": "Охотник за ;", "category": "syntax", "rarity": "редкое", "check": lambda p: _levels(p) >= 8},
    "ach_007": {"title": "Скобочный ниндзя", "category": "syntax", "rarity": "редкое", "check": lambda p: _levels(p) >= 9},
    "ach_008": {"title": "Голос котика", "category": "syntax", "rarity": "обычное", "check": lambda p: _levels(p) >= 5},
    "ach_009": {"title": "Строковый мур", "category": "syntax", "rarity": "редкое", "check": lambda p: _levels(p) >= 8},
    "ach_010": {"title": "Цикличный хвост", "category": "syntax", "rarity": "редкое", "check": lambda p: _levels(p) >= 6},
    "ach_011": {"title": "Мастер условий", "category": "syntax", "rarity": "редкое", "check": lambda p: _levels(p) >= 5},
    "ach_012": {"title": "Лапка методов", "category": "syntax", "rarity": "обычное", "check": lambda p: _levels(p) >= 9},
    "ach_013": {"title": "Коллекционер клубочков", "category": "data", "rarity": "редкое", "check": lambda p: _levels(p) >= 7},
    "ach_014": {"title": "LINQ-мурчание", "category": "data", "rarity": "эпическое", "check": lambda p: _bosses(p) >= 2},
    "ach_015": {"title": "Интерфейсный следопыт", "category": "oop", "rarity": "эпическое", "check": lambda p: _bosses(p) >= 2 and _levels(p) >= 9},
    "ach_016": {"title": "Полиморфный кот", "category": "oop", "rarity": "эпическое", "check": lambda p: _bosses(p) >= 3},
    "ach_017": {"title": "Refactor Paws", "category": "quality", "rarity": "редкое", "check": lambda p: int(p.get("kitten_points", 0)) >= 80},
    "ach_018": {"title": "Bug Hunter", "category": "quality", "rarity": "редкое", "check": lambda p: _dailies(p) >= 3},
    "ach_019": {"title": "Босс повержен", "category": "boss", "rarity": "редкое", "check": lambda p: _bosses(p) >= 1},
    "ach_020": {"title": "Триумф раздела", "category": "boss", "rarity": "эпическое", "check": lambda p: _bosses(p) >= 3},
    "ach_021": {"title": "Boss Chain", "category": "boss", "rarity": "эпическое", "check": lambda p: _bosses(p) >= 3},
    "ach_022": {"title": "Nine Lives Master", "category": "lives", "rarity": "эпическое", "check": lambda p: _levels(p) >= 6 and int(p.get("lives_current", 0)) == 3},
    "ach_023": {"title": "Чай с молоком", "category": "lives", "rarity": "обычное", "check": lambda p: int(p.get("life_resets_tea", 0)) >= 1},
    "ach_024": {"title": "Котику покушать", "category": "lives", "rarity": "обычное", "check": lambda p: int(p.get("life_resets_food", 0)) >= 1},
    "ach_025": {"title": "Daily Paw", "category": "events", "rarity": "редкое", "check": lambda p: _dailies(p) >= 7},
    "ach_026": {"title": "Weekly Hero", "category": "events", "rarity": "редкое", "check": lambda p: int(p.get("weekly_events_done", 0)) >= 1},
    "ach_027": {"title": "Security Paw", "category": "security", "rarity": "эпическое", "check": lambda p: _bosses(p) >= 1 and _levels(p) >= 10},
    "ach_028": {"title": "Crypto Kitten", "category": "security", "rarity": "эпическое", "check": lambda p: int(p.get("security_events_done", 0)) >= 1},
    "ach_029": {"title": "Junior Gate", "category": "capstone", "rarity": "легендарное", "check": lambda p: bool(p.get("final_project_done", False))},
    "ach_030": {
        "title": "Meow Academy Honors",
        "category": "capstone",
        "rarity": "легендарное",
        "check": lambda p: bool(p.get("final_project_done")) and _bosses(p) >= 3,
    },
    "ach_031": {
        "title": "С первого «Проверить»",
        "category": "skill",
        "rarity": "редкое",
        "check": lambda p: _first_try_levels(p) >= 3,
    },
    "ach_032": {
        "title": "Десять раз — и победа",
        "category": "quality",
        "rarity": "редкое",
        "check": lambda p: bool(p.get("won_after_many_tries")),
    },
    "ach_033": {
        "title": "Неделя в Логове",
        "category": "story",
        "rarity": "эпическое",
        "check": lambda p: bool(p.get("chapter_a_speedrun_done")),
    },
    "ach_034": {
        "title": "Серия как привычка",
        "category": "events",
        "rarity": "редкое",
        "check": lambda p: _streak_days(p) >= 7,
    },
    "ach_035": {
        "title": "Все письма наставника",
        "category": "story",
        "rarity": "эпическое",
        "check": lambda p: _mentor_read_all(p),
    },
}


def _progress_fraction(ach_id: str, p: dict[str, Any]) -> tuple[int, int] | None:
    """Для полосы прогресса: (текущее, цель) или None если не считаем."""
    lv = len(p.get("completed_levels", []))
    if ach_id == "ach_003":
        return min(lv, 10), 10
    if ach_id == "ach_025":
        d = _dailies(p)
        return min(d, 7), 7
    if ach_id == "ach_019":
        b = _bosses(p)
        return min(b, 1), 1
    if ach_id == "ach_020":
        b = _bosses(p)
        return min(b, 3), 3
    return None


def achievement_catalog_rows(progress: dict[str, Any]) -> list[dict[str, Any]]:
    """Витрина: все 30 достижений с категорией, редкостью и прогрессом."""
    owned = set(progress.get("achievements", []))
    rows: list[dict[str, Any]] = []
    for ach_id, meta in ACHIEVEMENTS.items():
        frac = _progress_fraction(ach_id, progress)
        if ach_id in owned:
            prog_pct = 100
            prog_label = "открыто"
        elif frac:
            cur, target = frac
            prog_pct = int(100 * cur / target) if target else 0
            prog_label = f"{cur}/{target}"
        else:
            prog_pct = 0 if ach_id not in owned else 100
            prog_label = "в процессе"
        rows.append(
            {
                "id": ach_id,
                "title": meta["title"],
                "category": meta["category"],
                "rarity": meta["rarity"],
                "unlocked": ach_id in owned,
                "progress_pct": prog_pct,
                "progress_label": prog_label,
            }
        )
    return rows


def update_achievements(progress: dict[str, Any]) -> list[str]:
    owned = set(progress.get("achievements", []))
    new_items: list[str] = []
    for ach_id, meta in ACHIEVEMENTS.items():
        if ach_id not in owned and meta["check"](progress):
            owned.add(ach_id)
            new_items.append(meta["title"])
    progress["achievements"] = sorted(owned)
    if "ach_030" in progress["achievements"]:
        progress["honors_done"] = True
    return new_items


def achievement_titles(progress: dict[str, Any]) -> list[str]:
    owned = set(progress.get("achievements", []))
    titles: list[str] = []
    for ach_id in sorted(owned):
        meta = ACHIEVEMENTS.get(ach_id)
        if meta:
            titles.append(meta["title"])
    return titles
