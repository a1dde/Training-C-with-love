from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from resources import user_data_dir

PROGRESS_FILE = user_data_dir() / "progress.json"


DEFAULT_PROGRESS: dict[str, Any] = {
    "schema_version": 1,
    "unlocked_levels": [1],
    "completed_levels": [],
    "selected_level": 1,
    "lives_max": 3,
    "lives_current": 3,
    "kitten_points": 0,
    "achievements": [],
    "completed_chapters": [],
    "current_streak": 0,
    "total_attempts": 0,
    "session_fail_streak": 0,
    "completed_bosses": [],
    "daily_events_done": 0,
    "weekly_events_done": 0,
    "security_events_done": 0,
    "life_resets_tea": 0,
    "life_resets_food": 0,
    "final_project_unlocked": False,
    "final_project_done": False,
    "final_project_track": None,
    "honors_done": False,
    "soft_mode_no_lives": False,
    "anxiety_care_mode": False,
    "purchased_cosmetics": [],
    "mentor_letters_seen": 0,
    "junior_day_done": False,
    "photo_album": [],
    "theme": "dark",
    "sound_enabled": True,
    "love_reminder_enabled": True,
}


def load_progress() -> dict[str, Any]:
    if not PROGRESS_FILE.exists():
        return dict(DEFAULT_PROGRESS)
    try:
        data = json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return dict(DEFAULT_PROGRESS)

    merged = dict(DEFAULT_PROGRESS)
    merged.update(data)
    merged["unlocked_levels"] = sorted(set(int(x) for x in merged.get("unlocked_levels", [1]) if int(x) > 0))
    merged["completed_levels"] = sorted(set(int(x) for x in merged.get("completed_levels", []) if int(x) > 0))
    if not merged["unlocked_levels"]:
        merged["unlocked_levels"] = [1]
    from levels_data import LEVELS

    normalize_progress_state(merged, level_count=len(LEVELS))
    return merged


def normalize_progress_state(progress: dict[str, Any], level_count: int) -> None:
    """Приводит selected_level к допустимому и разблокированному уровню (защита от битого JSON)."""
    max_id = max(1, level_count)
    try:
        sel = int(progress.get("selected_level", 1))
    except (TypeError, ValueError):
        sel = 1
    sel = max(1, min(sel, max_id))
    unlocked = sorted(set(int(x) for x in progress.get("unlocked_levels", [1]) if int(x) > 0))
    if not unlocked:
        unlocked = [1]
    if sel not in unlocked:
        leq = [u for u in unlocked if u <= sel]
        sel = max(leq) if leq else min(unlocked)
    progress["unlocked_levels"] = unlocked
    progress["selected_level"] = sel


def save_progress(progress: dict[str, Any]) -> None:
    temp = PROGRESS_FILE.with_suffix(".tmp")
    temp.write_text(json.dumps(progress, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(PROGRESS_FILE)


def lose_life(progress: dict[str, Any]) -> int:
    progress["lives_current"] = max(0, int(progress.get("lives_current", 3)) - 1)
    return progress["lives_current"]


def reset_lives(progress: dict[str, Any]) -> None:
    progress["lives_current"] = int(progress.get("lives_max", 3))


def finalize_chapter_and_project(progress: dict[str, Any], total_levels: int = 10, unlock_threshold: int = 8) -> None:
    """Закрытие главы A и разблокировка финального проекта по порогу уровней."""
    done = set(progress.get("completed_levels", []))
    if len(done) >= total_levels:
        ch = set(progress.get("completed_chapters", []))
        ch.add("A")
        progress["completed_chapters"] = sorted(ch)
    if len(done) >= unlock_threshold:
        progress["final_project_unlocked"] = True


def milestone_caption(progress: dict[str, Any], total_levels: int = 10) -> str:
    done_n = len(progress.get("completed_levels", []))
    if not progress.get("final_project_unlocked"):
        need = max(0, 8 - done_n)
        return f"До открытия финального проекта: {need} ур."
    if not progress.get("final_project_done"):
        return "Финальный проект открыт — выбери трек в меню «Проект»."
    return "Глава A пройдена — ты большая молодец! 🌟"


def pet_stage(completed_level_count: int) -> int:
    return min(4, completed_level_count // 2)


def pet_emoji(stage: int) -> str:
    return ["🐱", "🐈", "😺", "😸", "🦁"][min(stage, 4)]
