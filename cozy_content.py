"""Милые тексты: статусы, сюжетные вставки, темы карточки, сезоны, микро-термины."""

from __future__ import annotations

# Случайные короткие «мур» в статус (дополняют основное сообщение)
MUR_STATUS_LINES: list[str] = [
    "Котик подмигивает: ты молодец.",
    "Лапка одобрения — код пахнет правильным C#.",
    "Мурр… пусть компилятор всегда будет с тобой.",
    "Сегодня ты уже сделала больше, чем вчера.",
    "Пушистый high-five из Логова синтаксиса.",
]

# Мини-истории после ключевых уровней (4 строки)
CHAPTER_BEAT_STORIES: dict[int, str] = {
    5: (
        "Котик-стажёр дополз до середины главы A.\n\n"
        "Ветвления if/else — это уже почти как код-ревью: «если так — принимаем, иначе — переделать».\n\n"
        "Дальше — циклы и данные. Ты держишь темп 💕"
    ),
    10: (
        "Финал главы A: котик надел невидимые очки ревьюера.\n\n"
        "Ты соединила методы, циклы и условия — как в маленьком, но настоящем модуле.\n\n"
        "Глава B (коллекции) ждёт, когда будешь готова. Пока — мур и гордость 🐾"
    ),
}

# Вращающиеся микро-подсказки по C# (одна строка в день/уровень)
CS_MICRO_TIPS: list[str] = [
    "Слово дня: `namespace` — как папка для имён в большом проекте.",
    "`var` — когда тип очевиден справа: var x = \"мяу\";",
    "Строки в C# неизменяемы: каждая склейка `+` создаёт новую строку.",
    "`==` для строк сравнивает содержимое (для string).",
    "`Length` у массива и у string — разное, но оба про «сколько».",
    "Комментарий `//` не попадает в IL — только для людей.",
    "`using` вверху файла — короткий путь к типам из сборок.",
]

# Темы карточки урока: (fg_light, fg_dark, border_light, border_dark)
LESSON_CARD_THEMES: dict[str, tuple[str, str, str, str]] = {
    "default": ("#FFF5FA", "#2A1F26", "#F8BBD9", "#6D3756"),
    "lavender": ("#F3E5F5", "#2D2438", "#CE93D8", "#7B4A8C"),
    "peach": ("#FFF3E0", "#2A2218", "#FFCC80", "#8D5A3A"),
    "mint": ("#E0F7F4", "#1A2523", "#80CBC4", "#3E6F6A"),
}

# Сезонные акценты рамок (light_border, dark_border) — лёгкий оттенок
SEASONAL_BORDERS: dict[str, tuple[str, str]] = {
    "auto": ("#F8BBD9", "#6D3756"),  # fallback, подменяется логикой
    "winter": ("#B3E5FC", "#4A6FA5"),
    "spring": ("#C8E6C9", "#4A7C4E"),
    "summer": ("#FFE082", "#A67C00"),
    "autumn": ("#FFCCBC", "#8D4A3A"),
}


def season_key_from_date(month: int, day: int) -> str:
    """Грубое деление для auto: зима дек-фев и т.д."""
    if month in (12, 1, 2):
        return "winter"
    if month in (3, 4, 5):
        return "spring"
    if month in (6, 7, 8):
        return "summer"
    return "autumn"


def resolve_season_border(progress_season: str, month: int, day: int) -> tuple[str, str]:
    if progress_season == "auto":
        sk = season_key_from_date(month, day)
        return SEASONAL_BORDERS.get(sk, SEASONAL_BORDERS["auto"])
    return SEASONAL_BORDERS.get(progress_season, SEASONAL_BORDERS["auto"])
