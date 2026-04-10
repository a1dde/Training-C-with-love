"""Общие приёмы UI: модальные окна поверх главного, дружелюбные цвета кнопок."""

from __future__ import annotations

from typing import Any

import customtkinter as ctk

# Акценты для явных override (согласованы с assets/meow_pink.json)
PINK_PRIMARY = "#E91E8C"
PINK_PRIMARY_DARK = "#C2185B"
PINK_HOVER = "#F06292"
PINK_SOFT_BTN = "#F8BBD9"
CORAL_ACCENT = "#FF8A80"


def attach_popup(parent: ctk.CTk, win: ctk.CTkToplevel) -> None:
    """Дочернее окно остаётся привязанным к главному (не уезжает под него)."""
    try:
        win.transient(parent)
        win.lift()
        win.focus_force()

        def _lift_again() -> None:
            try:
                if win.winfo_exists():
                    win.lift()
            except Exception:
                pass

        win.after(120, _lift_again)
    except Exception:
        pass


def messagebox_with_parent(master: ctk.CTk | None, ctor: Any, **kwargs: Any) -> Any:
    """CTkMessagebox с привязкой к главному окну — позиция и stacking корректны."""
    if master is not None:
        kwargs.setdefault("master", master)
    kwargs.setdefault("topmost", True)
    kwargs.setdefault("button_color", PINK_PRIMARY)
    kwargs.setdefault("button_hover_color", PINK_HOVER)
    return ctor(**kwargs)


def kitten_tail_for_compiler_message(message: str) -> str:
    """
    Одна простая кото-аналогия к сообщению Roslyn/MSBuild (по коду CS или тексту).
    Не заменяет техническую строку — только добавляет понятный образ.
    """
    u = message.upper()
    if "MEOW001" in u or "ПУСТОЙ" in message:
        return "Пустой файл — как пустая миска: напиши хоть строчку кода, чтобы котик мог проверить."
    if "CS1002" in u or ("EXPECTED" in u and ";" in message):
        return "Не хватает `;` в конце «фразы» — как хвостика после мяу: многие команды в C# им заканчиваются."
    if "CS1513" in u or ("}" in message and "EXPECTED" in u):
        return "Скобка `}` закрывает блок — проверь, что каждая `{` нашла пару, как крышка на банке с кормом."
    if "CS1003" in u or ("SYNTAX" in u and "ERROR" in u):
        return "Синтаксис споткнулся: посмотри на скобки `()`, `{}` и кавычки — как на застёжку переноски."
    if "CS1525" in u or "INVALID EXPRESSION" in u:
        return "Тут выражение получилось кривым — перечитай строку с начала, как кот пересчитывает лапки."
    if "CS0103" in u or "DOES NOT EXIST" in u or "НЕ СУЩЕСТВУЕТ" in message.upper():
        return "Имя не найдено — как если позвать кота чужим кличкой: переменная или тип не объявлены выше."
    if "CS0246" in u or "TYPE OR NAMESPACE" in u:
        return "Тип или пространство имён не узнаны — проверь написание, как имя на ошейнике."
    if "CS0029" in u or "CANNOT IMPLICITLY CONVERT" in u:
        return "Типы не дружат: нельзя положить рыбу в миску для чисел — приведи тип или поменяй значение."
    if "CS0162" in u:
        return "Код после `return` недостижим — как запасной выход, который заложен кирпичом."
    if "CS0161" in u or "NOT ALL CODE PATHS RETURN" in u:
        return "Не из всех веток `if` метод возвращает значение — кот должен принести ответ по любому сценарию."
    if "CS0119" in u:
        return "Тут ожидали значение, а встретили что-то другое — перепроверь скобки и имена."
    if "CS1503" in u or "ARGUMENT" in u and "CANNOT CONVERT" in u:
        return "Аргумент не подошёл по типу — как не та насадка на шприц с пастой."
    if "CS1501" in u:
        return "Такой набор аргументов метод не знает — пересчитай параметры, как лапки на подстилке."
    if "CS7036" in u:
        return "Не передали обязательный аргумент — как забыть миску, когда зовёшь кота кушать."
    if "CS0128" in u or "ALREADY DEFINED" in u:
        return "Дважды одно и то же имя в одной области — у каждого котика своё имя в комнате."
    if "CS8805" in u or "TOP-LEVEL" in u:
        return "С top-level и локальными функциями порядок важен — как кто первым прыгнул на диван."
    if "CS0136" in u:
        return "Переменная с таким именем уже есть в этой области — выбери другое имя для второго котёнка."
    if "CS0165" in u:
        return "Используешь переменную, которой ещё нет значения — сначала положи в миску, потом зови кота."
    if "CS0027" in u:
        return "В свойстве не всё пути возвращают значение — допиши `return` или `get`."
    if "CS0152" in u:
        return "Два одинаковых `case` в `switch` — как две одинаковые этикетки на банках."
    if "CS0160" in u:
        return "После `catch` нужен тип исключения — укажи, какую «ошибку» ловишь."
    if "CS1001" in u or "IDENTIFIER EXPECTED" in u:
        return "Тут ждали имя (переменной, метода…) — как кличку, без неё котик не откликнется."
    if "CS1031" in u or "TYPE EXPECTED" in u:
        return "На этом месте нужен тип — `int`, `string` и т.д., как выбрать размер миски."
    if "CS8076" in u or "INTERPOLATED" in u:
        return "В `$\"...\"` фигурные скобки для выражений — проверь, что `{` и `}` парные."
    if "CS1010" in u or "NEWLINE IN CONSTANT" in u:
        return "Строка оборвалась — закрой кавычки, как крышку на банке с молоком."
    if "CS1039" in u:
        return "Незавершённая строка — проверь кавычки `\"` или `$\"`."
    if "CS8641" in u or "TOO MANY" in u and "CHARACTER" in u:
        return "Лишний символ в литерале — убери лишнее или экранируй."
    if "CS0106" in u:
        return "Модификатор тут недопустим — как шлейка на хвост: не то место."
    if "CS0542" in u:
        return "Имя типа совпадает с членом — переименуй, чтобы не путать двух рыжих котов."
    if "CS0535" in u:
        return "Не реализован метод из интерфейса — допиши заглушку, как недостающий трюк."
    if "CS0538" in u:
        return "`explicit interface` использован не там — перепроверь объявление."
    if "CS1591" in u:
        return "Публичный член без комментария — для учебы не критично, но можно добавить `///`."
    if "MEOW_TIMEOUT" in u or "ТАЙМАУТ" in message.upper():
        return "Проверка долго не отвечала — попробуй ещё раз; если часто, напиши разработчику."
    return "Котик-редактор указал на место в коде — ниже точная формулировка; исправь и нажми «Проверить» снова."


def friendly_compiler_hint_block(technical_hint: str) -> str:
    """Блок подсказки: кото-образ + исходное сообщение."""
    tech = technical_hint.strip()
    if not tech:
        return "Что-то не так с кодом — смотри чек-лист под редактором."
    tail = kitten_tail_for_compiler_message(tech)
    return f"{tail}\n\n— Точнее: {tech}"
