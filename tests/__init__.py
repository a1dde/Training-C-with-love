"""Test package root for C# Meow Academy."""

import os

# Ускоряет unittest: не гоняем dotnet run на каждую проверку (полный вывод — вручную / e2e).
os.environ.setdefault("MEOW_SKIP_PROGRAM_RUN", "1")
