from __future__ import annotations

import re
from typing import Literal, TypedDict

from csharp_reference import GLOSSARY  # noqa: F401 — экспорт для content_lint и UI


RuleKind = Literal["contains"]


class Rule(TypedDict):
    id: str
    kind: RuleKind
    value: str
    label: str


class Level(TypedDict):
    id: int
    chapter: str
    type: str
    title: str
    wisdom: str
    mission: str
    starter_code: str
    reference_code: str
    rules: list[Rule]
    hints: dict[str, list[str]]


def level_short_name(level: Level) -> str:
    """Название задания без префикса «Уровень N:» — для сайдбара и карточек."""
    t = level.get("title", "")
    m = re.match(r"Уровень\s+\d+:\s*(.+)", t)
    if m:
        return m.group(1).strip()
    return t


LEVELS: list[Level] = [
    {
        "id": 1,
        "chapter": "A",
        "type": "classic",
        "title": "Уровень 1: Первый мяу в консоль",
        "wisdom": "Котёнок сначала учится мяукать, а программист — выводить текст. "
        "Команда `Console.WriteLine` — это голос твоего котика в мире C#.",
        "mission": "Напиши строку, которая выводит приветствие в консоль.",
        "starter_code": "// Уровень 1 · выведи приветствие в консоль\n// Подсказка смотри в задании выше — без готового кода здесь 💕\n\n",
        "reference_code": 'Console.WriteLine("Привет, C#!");\n',
        "rules": [
            {"id": "console_write", "kind": "contains", "value": "Console.WriteLine", "label": "Есть Console.WriteLine"},
            {"id": "semicolon", "kind": "contains", "value": ";", "label": "Есть ;"},
        ],
        "hints": {
            "console_write": [
                "Мур! Кажется, котик не нашёл команду вывода в консоль 🐾",
                "Попробуй использовать Console.WriteLine(\"...\")",
                "Мини-шаблон: Console.WriteLine(\"Мяу\");",
            ],
            "semicolon": [
                "Хвостик потерялся: проверь `;` в конце строки 🐱",
                "В C# инструкция обычно заканчивается `;`",
                "Пример: Console.WriteLine(\"Мяу\");",
            ],
        },
    },
    {
        "id": 2,
        "chapter": "A",
        "type": "classic",
        "title": "Уровень 2: Строковая миска",
        "wisdom": "Строка `string` — это миска с текстом. Положи туда имя котика и покажи его.",
        "mission": "Создай переменную string и выведи её через Console.WriteLine.",
        "starter_code": "// Уровень 2 · переменная string и вывод\n\n",
        "reference_code": 'string catName = "Мурка";\nConsole.WriteLine(catName);\n',
        "rules": [
            {"id": "string_kw", "kind": "contains", "value": "string", "label": "Есть string"},
            {"id": "write", "kind": "contains", "value": "Console.WriteLine", "label": "Есть вывод"},
            {"id": "semicolon", "kind": "contains", "value": ";", "label": "Есть ;"},
        ],
        "hints": {
            "string_kw": [
                "Слово `string` — как бирка «текст» на миске: без него компилятор не поймёт, что внутри слова.",
                "Пример: string кличка = \"Мурка\";",
            ],
            "write": [
                "Чтобы показать имя на экране, зови Console.WriteLine(переменная);",
            ],
            "semicolon": [
                "В конце команды — `;`, как точка после мяу.",
            ],
        },
    },
    {
        "id": 3,
        "chapter": "A",
        "type": "classic",
        "title": "Уровень 3: Считаем вкусняшки",
        "wisdom": "`int` — это счётчик вкусняшек. Цифры в C# живут в целых переменных.",
        "mission": "Создай int-переменную и выведи число в консоль.",
        "starter_code": "// Уровень 3 · int и вывод числа\n\n",
        "reference_code": "int treats = 5;\nConsole.WriteLine(treats);\n",
        "rules": [
            {"id": "int_kw", "kind": "contains", "value": "int", "label": "Есть int"},
            {"id": "write", "kind": "contains", "value": "Console.WriteLine", "label": "Есть вывод"},
            {"id": "semicolon", "kind": "contains", "value": ";", "label": "Есть ;"},
        ],
        "hints": {
            "int_kw": [
                "`int` — счётчик вкусняшек: только целые числа, без дробей.",
                "Пример: int лапок = 4;",
            ],
            "write": [
                "Выведи число через Console.WriteLine(переменная);",
            ],
            "semicolon": [
                "Не забудь `;` после присваивания и после WriteLine.",
            ],
        },
    },
    {
        "id": 4,
        "chapter": "A",
        "type": "classic",
        "title": "Уровень 4: Правда или мур?",
        "wisdom": "`bool` — как ответ котика: да (`true`) или нет (`false`).",
        "mission": "Создай bool-переменную и выведи её значение.",
        "starter_code": "// Уровень 4 · bool и вывод\n\n",
        "reference_code": "bool isHungry = true;\nConsole.WriteLine(isHungry);\n",
        "rules": [
            {"id": "bool_kw", "kind": "contains", "value": "bool", "label": "Есть bool"},
            {"id": "truth", "kind": "contains", "value": "true", "label": "Есть true/false"},
            {"id": "write", "kind": "contains", "value": "Console.WriteLine", "label": "Есть вывод"},
        ],
        "hints": {
            "bool_kw": [
                "`bool` — ответ «да/нет»: только true или false, как «голоден / не голоден».",
            ],
            "truth": [
                "В значении bool должно быть слово true или false — как ответ «да» или «нет».",
            ],
            "write": [
                "Покажи bool на экране: Console.WriteLine(переменная);",
            ],
        },
    },
    {
        "id": 5,
        "chapter": "A",
        "type": "classic",
        "title": "Уровень 5: Две дверцы if/else",
        "wisdom": "Котик выбирает дверцу: если голодный — к миске, иначе — спать. Это и есть if/else.",
        "mission": "Напиши код с if и else.",
        "starter_code": "// Уровень 5 · ветвление if / else\n\n",
        "reference_code": "bool isHungry = true;\nif (isHungry)\n{\n    Console.WriteLine(\"Кушаем\");\n}\nelse\n{\n    Console.WriteLine(\"Спим\");\n}\n",
        "rules": [
            {"id": "if_kw", "kind": "contains", "value": "if", "label": "Есть if"},
            {"id": "else_kw", "kind": "contains", "value": "else", "label": "Есть else"},
            {"id": "write", "kind": "contains", "value": "Console.WriteLine", "label": "Есть вывод"},
        ],
        "hints": {
            "if_kw": [
                "`if` — первая дверца: если условие правда, иди туда.",
            ],
            "else_kw": [
                "`else` — вторая дверца: если не правда — иди сюда. Кот идёт только в одну за раз.",
            ],
            "write": [
                "Внутри веток не забудь Console.WriteLine(...), чтобы было что проверить.",
            ],
        },
    },
    {
        "id": 6,
        "chapter": "A",
        "type": "classic",
        "title": "Уровень 6: Круг охоты for",
        "wisdom": "Цикл `for` — как круг охоты: котик делает шаги по счёту.",
        "mission": "Используй for и выведи значения счётчика.",
        "starter_code": "// Уровень 6 · цикл for\n\n",
        "reference_code": "for (int i = 0; i < 3; i++)\n{\n    Console.WriteLine(i);\n}\n",
        "rules": [
            {"id": "for_kw", "kind": "contains", "value": "for", "label": "Есть for"},
            {"id": "int_kw", "kind": "contains", "value": "int", "label": "Есть int"},
            {"id": "write", "kind": "contains", "value": "Console.WriteLine", "label": "Есть вывод"},
        ],
        "hints": {
            "for_kw": [
                "`for` — круг по комнате: счётчик i, сколько шагов, что делать после шага.",
                "Шаблон: for (int i = 0; i < 3; i++)",
            ],
            "int_kw": [
                "Счётчик i обычно `int`, как целые лапки.",
            ],
            "write": [
                "На каждом круге выведи что-нибудь через Console.WriteLine.",
            ],
        },
    },
    {
        "id": 7,
        "chapter": "A",
        "type": "classic",
        "title": "Уровень 7: Кошачья полка (массив)",
        "wisdom": "Массив — это полка, где лежат несколько мисок одного типа.",
        "mission": "Создай массив и выведи один элемент.",
        "starter_code": "// Уровень 7 · массив и индекс\n\n",
        "reference_code": 'string[] cats = {"Мурка", "Барсик"};\nConsole.WriteLine(cats[0]);\n',
        "rules": [
            {"id": "array", "kind": "contains", "value": "[]", "label": "Есть массив []"},
            {"id": "write", "kind": "contains", "value": "Console.WriteLine", "label": "Есть вывод"},
            {"id": "index", "kind": "contains", "value": "[0]", "label": "Есть обращение по индексу"},
        ],
        "hints": {
            "array": [
                "Массив — полка с мисками: тип[] имя = new тип[] { ... } или сокращённо { ... }.",
            ],
            "write": [
                "Выведи элемент через Console.WriteLine(...);",
            ],
            "index": [
                "Индекс [0] — первая миска слева; в C# индексы с нуля.",
            ],
        },
    },
    {
        "id": 8,
        "chapter": "A",
        "type": "classic",
        "title": "Уровень 8: Интерполяция мур-строк",
        "wisdom": "Интерполяция `$\"...\"` — когда имя котика аккуратно вставляется в фразу.",
        "mission": "Используй интерполяцию строки с переменной.",
        "starter_code": "// Уровень 8 · интерполяция $\"...\"\n\n",
        "reference_code": 'string name = "Луна";\nConsole.WriteLine($"Привет, {name}!");\n',
        "rules": [
            {"id": "dollar_quote", "kind": "contains", "value": '$"', "label": 'Есть $"'},
            {"id": "brace_open", "kind": "contains", "value": "{", "label": "Есть {"},
            {"id": "brace_close", "kind": "contains", "value": "}", "label": "Есть }"},
        ],
        "hints": {
            "dollar_quote": [
                "Интерполяция начинается с `$\"` — как волшебная миска: внутри {имя} подставляется само.",
            ],
            "brace_open": [
                "Открытая `{` вставляет переменную в строку.",
            ],
            "brace_close": [
                "Закрытая `}` завершает вставку — не потеряй пару.",
            ],
        },
    },
    {
        "id": 9,
        "chapter": "A",
        "type": "classic",
        "title": "Уровень 9: Свой метод мурчания",
        "wisdom": "Метод — это отдельный трюк котика, который можно вызвать в любой момент.",
        "mission": "Создай метод и вызови его.",
        "starter_code": "// Уровень 9 · метод void и вызов\n\n",
        "reference_code": "void Purr()\n{\n    Console.WriteLine(\"Мур\");\n}\n\nPurr();\n",
        "rules": [
            {"id": "method_decl", "kind": "contains", "value": "void", "label": "Есть объявление метода"},
            {"id": "paren", "kind": "contains", "value": "()", "label": "Есть ()"},
            {"id": "call", "kind": "contains", "value": "Purr();", "label": "Есть вызов метода"},
        ],
        "hints": {
            "method_decl": [
                "Метод `void Имя()` — отдельный трюк: объявляешь один раз, зовёшь сколько угодно.",
            ],
            "paren": [
                "Скобки `()` после имени — как дверца в трюк: сюда потом можно параметры.",
            ],
            "call": [
                "Вызов метода — имя и (); в задании нужен вызов Purr(); как в эталоне.",
            ],
        },
    },
    {
        "id": 10,
        "chapter": "A",
        "type": "classic",
        "title": "Уровень 10: Финальный микс лапок",
        "wisdom": "Финал — как большой квест: условия, циклы и методы работают вместе.",
        "mission": "Напиши мини-программу с методом, for и if/else, выводом в консоль.",
        "starter_code": "// Уровень 10 · метод, for, if/else — всё вместе\n\n",
        "reference_code": "void Check(int i)\n{\n    if (i % 2 == 0)\n    {\n        Console.WriteLine(\"Чёт\");\n    }\n    else\n    {\n        Console.WriteLine(\"Нечёт\");\n    }\n}\n\nfor (int i = 0; i < 3; i++)\n{\n    Check(i);\n}\n",
        "rules": [
            {"id": "method", "kind": "contains", "value": "void", "label": "Есть метод"},
            {"id": "if", "kind": "contains", "value": "if", "label": "Есть if"},
            {"id": "for", "kind": "contains", "value": "for", "label": "Есть for"},
            {"id": "write", "kind": "contains", "value": "Console.WriteLine", "label": "Есть вывод"},
        ],
        "hints": {
            "method": [
                "Собери метод `void` — отдельная комната для кода, чтобы не путать с остальным.",
            ],
            "if": [
                "`if` / `else` — кот выбирает ветку, как миска или подушка.",
            ],
            "for": [
                "`for` — несколько шагов подряд; счётчик помогает не сбиться с лапок.",
            ],
            "write": [
                "Не забудь Console.WriteLine внутри веток или цикла — иначе нечего показать.",
            ],
        },
    },
]


FINAL_PROJECT_TRACKS: list[dict[str, object]] = [
    {
        "id": "cat_cafe",
        "title": "CatCafeManager — меню и заказы",
        "mission": "Собери мини-сценарий: коллекция List, ветвление if, метод void и вывод Console.WriteLine.",
        "starter_code": "// Финальный трек · твой код с нуля\n// Нужны: List, if, void, Console.WriteLine\n\n",
        "reference_code": "using System.Collections.Generic;\n\nvoid PrintMenu()\n{\n    var items = new List<string> { \"молоко\", \"рыба\" };\n    if (items.Count > 0)\n    {\n        Console.WriteLine(\"меню ок\");\n    }\n}\n",
        "rules": [
            {"id": "list", "kind": "contains", "value": "List", "label": "Есть List"},
            {"id": "if_kw", "kind": "contains", "value": "if", "label": "Есть if"},
            {"id": "void_m", "kind": "contains", "value": "void", "label": "Есть void"},
            {"id": "write", "kind": "contains", "value": "Console.WriteLine", "label": "Есть вывод"},
        ],
    },
    {
        "id": "kitten_tasks",
        "title": "KittenTaskTracker — словарь задач",
        "mission": "Используй Dictionary, if и Console.WriteLine для учебного трекера.",
        "starter_code": "// Финальный трек · Dictionary и if\n\n",
        "reference_code": "using System.Collections.Generic;\n\nvar tasks = new Dictionary<string, int>();\nif (tasks.Count >= 0)\n{\n    Console.WriteLine(\"ок\");\n}\n",
        "rules": [
            {"id": "dict", "kind": "contains", "value": "Dictionary", "label": "Есть Dictionary"},
            {"id": "if_kw", "kind": "contains", "value": "if", "label": "Есть if"},
            {"id": "write", "kind": "contains", "value": "Console.WriteLine", "label": "Есть вывод"},
        ],
    },
    {
        "id": "secure_lab",
        "title": "SecureKittenLab — проверка пароля",
        "mission": "ИБ-мини-кейс: проверь длину пароля через Length и if, выведи вердикт.",
        "starter_code": "// Финальный трек · пароль и if\n\n",
        "reference_code": "string password = \"Secret12\";\nif (password.Length >= 8)\n{\n    Console.WriteLine(\"надёжно\");\n}\nelse\n{\n    Console.WriteLine(\"слабо\");\n}\n",
        "rules": [
            {"id": "length", "kind": "contains", "value": "Length", "label": "Есть Length"},
            {"id": "if_kw", "kind": "contains", "value": "if", "label": "Есть if"},
            {"id": "write", "kind": "contains", "value": "Console.WriteLine", "label": "Есть вывод"},
        ],
    },
]


BOSS_CHOICES = [
    {
        "id": "boss_logic_cat",
        "title": "Босс: Logic Cat 🧠",
        "mission": "Напиши код с if/else и выводом результата проверки пароля.",
        "starter_code": "// Босс-файт · пиши решение сама\n\n",
        "reference_code": 'string password = "cat123";\nif (password == "cat123")\n{\n    Console.WriteLine("OK");\n}\nelse\n{\n    Console.WriteLine("NO");\n}\n',
        "rules": [
            {"id": "if_kw", "kind": "contains", "value": "if", "label": "Есть if"},
            {"id": "else_kw", "kind": "contains", "value": "else", "label": "Есть else"},
            {"id": "write", "kind": "contains", "value": "Console.WriteLine", "label": "Есть вывод"},
        ],
    },
    {
        "id": "boss_data_cat",
        "title": "Босс: Data Cat 📚",
        "mission": "Создай массив и пройди его циклом for, выводя элементы.",
        "starter_code": "// Босс-файт · массив и for\n\n",
        "reference_code": 'string[] cats = {"Мурка", "Луна", "Барсик"};\nfor (int i = 0; i < cats.Length; i++)\n{\n    Console.WriteLine(cats[i]);\n}\n',
        "rules": [
            {"id": "array", "kind": "contains", "value": "[]", "label": "Есть массив"},
            {"id": "for_kw", "kind": "contains", "value": "for", "label": "Есть for"},
            {"id": "write", "kind": "contains", "value": "Console.WriteLine", "label": "Есть вывод"},
        ],
    },
    {
        "id": "boss_security_cat",
        "title": "Босс: Security Cat 🛡️",
        "mission": "Проверь длину пароля: if + Console.WriteLine, минимум 8 символов.",
        "starter_code": "// Босс-файт · длина пароля\n\n",
        "reference_code": 'string password = "mySecret1";\nif (password.Length >= 8)\n{\n    Console.WriteLine("Надежный");\n}\nelse\n{\n    Console.WriteLine("Слабый");\n}\n',
        "rules": [
            {"id": "length", "kind": "contains", "value": "Length", "label": "Есть Length"},
            {"id": "if_kw", "kind": "contains", "value": "if", "label": "Есть if"},
            {"id": "write", "kind": "contains", "value": "Console.WriteLine", "label": "Есть вывод"},
        ],
    },
]


DAILY_EVENTS = [
    {
        "id": "daily_syntax",
        "title": "Daily: Syntax Sprint",
        "mission": "Используй int и Console.WriteLine в одной короткой задаче.",
        "starter_code": "// Daily · int и вывод в консоль\n\n",
        "hints": {
            "int_kw": [
                "Объяви целое: int n = 1; — и выведи n через Console.WriteLine(n);",
            ],
            "write": [
                "Без Console.WriteLine котик не увидит результат в «консоли».",
            ],
        },
        "rules": [
            {"id": "int_kw", "kind": "contains", "value": "int", "label": "Есть int"},
            {"id": "write", "kind": "contains", "value": "Console.WriteLine", "label": "Есть вывод"},
        ],
    },
    {
        "id": "daily_fix",
        "title": "Daily: Fix Code",
        "mission": "Почини код ниже: компилятор укажет строку с ошибкой; нужны ; и вывод строки.",
        "starter_code": '// Daily · типичная опечатка: забыли ";" в конце\nConsole.WriteLine("Мяу")\n',
        "hints": {
            "semi": [
                "После Console.WriteLine(\"...\") почти всегда ставят `;` в конце строки.",
                "Сравни с эталоном уровня 1 в кампании — там всё с хвостиком `;`.",
            ],
            "write": [
                "Console.WriteLine уже есть — чаще всего не хватает только `;`.",
            ],
        },
        "rules": [
            {"id": "semi", "kind": "contains", "value": ";", "label": "Есть ;"},
            {"id": "write", "kind": "contains", "value": "Console.WriteLine", "label": "Есть вывод"},
        ],
    },
]


WEEKLY_EVENTS = [
    {
        "id": "weekly_mix",
        "title": "Weekly: Mixed Boss Review",
        "mission": "Смешай if, for и Console.WriteLine в одном коротком решении.",
        "starter_code": "// Weekly · if, for, вывод\n\n",
        "hints": {
            "if_kw": ["Мини-шаблон: if (условие) { ... }"],
            "for_kw": ["for (int i = 0; i < n; i++) { ... }"],
            "write": ["Внутри веток или цикла вызови Console.WriteLine(...);"],
        },
        "rules": [
            {"id": "if_kw", "kind": "contains", "value": "if", "label": "Есть if"},
            {"id": "for_kw", "kind": "contains", "value": "for", "label": "Есть for"},
            {"id": "write", "kind": "contains", "value": "Console.WriteLine", "label": "Есть вывод"},
        ],
    },
    {
        "id": "weekly_security",
        "title": "Weekly: Security Check",
        "mission": "Проверь длину пароля через if и Length, затем выведи результат.",
        "starter_code": '// Weekly · string password = "...";\n\n',
        "hints": {
            "length": ["У строки есть .Length — сравни с числом в if (password.Length >= 8)."],
            "if_kw": ["if ( ... ) { ... } else { ... }"],
            "write": ["Выведи вердикт через Console.WriteLine(\"...\");"],
        },
        "rules": [
            {"id": "length", "kind": "contains", "value": "Length", "label": "Есть Length"},
            {"id": "if_kw", "kind": "contains", "value": "if", "label": "Есть if"},
            {"id": "write", "kind": "contains", "value": "Console.WriteLine", "label": "Есть вывод"},
        ],
    },
]
