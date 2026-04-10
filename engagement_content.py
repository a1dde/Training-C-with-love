"""Офлайн-тексты для Emotional UX, engagement и authority-слоя."""

MENTOR_LETTERS: list[str] = [
    "Мур! Я горжусь каждой твоей строчкой. Даже если сегодня трудно — ты уже делаешь шаг к сильному C#. 🐾",
    "Котик-наставник шепчет: отдых — тоже часть учёбы. Потяни лапки, выпей воды и возвращайся, когда будет уютно.",
    "Помни: каждый junior когда-то путал ; и скобки. Ты не одна — я рядом.",
]

FIVE_MIN_QUESTS: list[dict[str, str]] = [
    {
        "title": "5 минут: точка с запятой",
        "body": "Напиши одну строку: Console.WriteLine(\"Мяу\"); и проверь себя глазами — есть ли ; в конце?",
    },
    {
        "title": "5 минут: if на бумаге",
        "body": "Без IDE: придумай условие if (isHungry) и что вывести в ветках. Потом сравни с уровнем 5.",
    },
]

JUNIOR_DAY_STEPS: list[str] = [
    "1) Баг: в коде пропали ; — найди строку.",
    "2) Фикс: добавь ; и проверь мысленно компиляцию.",
    "3) Мини-тест: перечисли вслух три правила хорошего имени переменной.",
    "4) Ревью: прочитай свой код вслух — слышно ли, что делает программа?",
]

ROADMAP_PHASES: list[tuple[str, str]] = [
    ("Глава A — Синтаксис", "Console, типы, if/for, массивы, методы — база для всего."),
    ("Глава B — Коллекции", "List, Dictionary, foreach — как разложить данные по полочкам."),
    ("Глава C — Методы глубже", "Параметры, return, разбиение задачи."),
    ("Junior Security Cat", "Валидация, безопасные строки, основы крипто и сетей в учебных кейсах."),
]


def weekly_digest_text(progress: dict) -> str:
    """Краткая сводка прогресса для офлайн-дайджеста."""
    lines = [
        "📋 ИБ-дайджест недели (локально, без сети)",
        f"Пройдено уровней: {len(progress.get('completed_levels', []))}",
        f"Очки лапок: {int(progress.get('kitten_points', 0))}",
        f"Боссы: {len(progress.get('completed_bosses', []))}/3",
        f"Daily: {int(progress.get('daily_events_done', 0))} · Weekly: {int(progress.get('weekly_events_done', 0))}",
        f"Жизни: {int(progress.get('lives_current', 0))}/{int(progress.get('lives_max', 3))}",
    ]
    if progress.get("soft_mode_no_lives"):
        lines.append("Включён мягкий режим: жизни не тратятся — ты под защитой котика.")
    return "\n".join(lines)
