# C# Meow Academy

Десктопное приложение для изучения **C#** в игровом формате: уровни с заданиями, встроенный редактор кода, проверка через **Roslyn** (проект `csharp_syntax_check`), прогресс, достижения, питомец-тамагочи и события.

Интерфейс на **CustomTkinter** (Python 3.10+), Windows.

## Возможности

- Пошаговые уровни и финальный проект, справочник по синтаксису C#
- Валидация решений и правил уровней
- Сохранение прогресса, жизни, босс-уровень, еженедельные и дневные события
- Темы оформления, мемы с котиками (см. `memes/ATTRIBUTION.txt`)

## Запуск из исходников

```powershell
cd "путь\к\Training-C-with-love"
python -m pip install -r requirements.txt
python main.py
```

Для полной проверки кода через Roslyn нужен собранный `MeowSyntaxCheck` (см. ниже). Без него часть функций может быть ограничена.

### Сборка проверки синтаксиса (Roslyn)

Требуется [.NET 8 SDK](https://dotnet.microsoft.com/download).

```powershell
dotnet build csharp_syntax_check\MeowSyntaxCheck.csproj -c Release
```

## Сборка `.exe` (Windows)

Скрипт подтягивает portable .NET в `bundled_dotnet` (при отсутствии), ставит зависимости, собирает `csharp_syntax_check` и запускает PyInstaller:

```powershell
.\build_exe.ps1
```

Готовый файл появится в `dist\` (артефакты сборки в репозиторий не коммитятся — см. `.gitignore`).

## Тесты

Используется `unittest`. Часть тестов требует установленного .NET SDK и собранного `csharp_syntax_check`.

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

## Структура (кратко)

| Путь | Назначение |
|------|------------|
| `main.py`, `app.py` | Точка входа и главное окно |
| `levels_data.py`, `validators.py` | Уровни и проверки |
| `csharp_compiler.py` | Интеграция с компилятором / Roslyn |
| `csharp_syntax_check/` | Консольная утилита проверки (C# / Roslyn) |
| `tests/` | Автотесты |

## Репозиторий

<https://github.com/a1dde/Training-C-with-love>
