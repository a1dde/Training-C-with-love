"""Косметика питомца: магазин и отображение."""

from __future__ import annotations

from typing import Any, TypedDict


class CosmeticItem(TypedDict):
    id: str
    title: str
    cost: int
    emoji: str


# Порядок = порядок «надетых» иконок слева направо
PET_COSMETICS: list[CosmeticItem] = [
    {"id": "pink_bow", "title": "Розовый бантик", "cost": 18, "emoji": "🎀"},
    {"id": "star_collar", "title": "Ошейник со звёздочкой", "cost": 22, "emoji": "⭐"},
    {"id": "rainbow_paw", "title": "Радужная лапка", "cost": 30, "emoji": "🌈"},
    {"id": "heart_glasses", "title": "Очки-сердечки", "cost": 28, "emoji": "💕"},
    {"id": "sleepy_cap", "title": "Шапочка для сна", "cost": 24, "emoji": "🎩"},
    {"id": "fish_pin", "title": "Значок «рыбка»", "cost": 15, "emoji": "🐟"},
]


def cosmetic_by_id(cid: str) -> CosmeticItem | None:
    for c in PET_COSMETICS:
        if c["id"] == cid:
            return c
    return None


def cosmetics_emojis_for_owned(purchased: list[str] | None) -> str:
    """Строка эмодзи купленных предметов (в порядке витрины)."""
    own = set(purchased or [])
    parts: list[str] = []
    for c in PET_COSMETICS:
        if c["id"] in own:
            parts.append(c["emoji"])
    return " ".join(parts) if parts else "— пока без украшений"

