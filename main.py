import sys

import customtkinter as ctk

from app import MeowAcademyApp
from resources import is_frozen, resource_path


def main() -> None:
    # Иконка на панели задач Windows для onefile exe (иначе иногда показывается generic)
    if sys.platform == "win32" and is_frozen():
        try:
            import ctypes

            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("MeowAcademy.CSharpWithLove.1")
        except Exception:
            pass

    theme = resource_path("assets", "meow_pink.json")
    if theme.is_file():
        ctk.set_default_color_theme(str(theme))
    else:
        ctk.set_default_color_theme("dark-blue")

    app = MeowAcademyApp()
    app.mainloop()


if __name__ == "__main__":
    main()
