"""Редактор кода с номерами строк (tk.Text), похожий на IDE."""

from __future__ import annotations

import tkinter as tk
from typing import Any, Callable

import customtkinter as ctk


class CodeEditorPanel(tk.Frame):
    """Два синхронных поля: gutter с номерами строк + основной текст. API совместим с tk.Text для app.py."""

    def __init__(self, master: tk.Misc, **kwargs: Any) -> None:
        bg_main = kwargs.pop("bg_main", "#252028")
        bg_gutter = kwargs.pop("bg_gutter", "#1a1520")
        fg = kwargs.pop("fg", "#F0E6EB")
        fg_dim = kwargs.pop("fg_dim", "#8a7a85")
        font = kwargs.pop("font", ("Consolas", 14))
        super().__init__(master, bg=bg_main, **kwargs)

        self._bg_main = bg_main
        self._bg_gutter = bg_gutter
        self._fg = fg
        self._fg_dim = fg_dim
        self._font = font

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._gutter = tk.Text(
            self,
            width=5,
            padx=6,
            pady=8,
            takefocus=0,
            borderwidth=0,
            highlightthickness=0,
            state="disabled",
            wrap="none",
            font=font,
            bg=bg_gutter,
            fg=fg_dim,
            insertbackground=fg,
            selectbackground=bg_gutter,
        )
        self._gutter.grid(row=0, column=0, sticky="ns")

        self._text = tk.Text(
            self,
            padx=8,
            pady=8,
            borderwidth=0,
            highlightthickness=0,
            undo=True,
            maxundo=-1,
            wrap="none",
            font=font,
            bg=bg_main,
            fg=fg,
            insertbackground=fg,
            selectbackground="#6D3756",
            selectforeground="#FFFFFF",
        )
        self._text.grid(row=0, column=1, sticky="nsew")

        self._scroll = tk.Scrollbar(self, command=self._on_scrollbar)
        self._scroll.grid(row=0, column=2, sticky="ns")
        self._text.config(yscrollcommand=self._on_text_yscroll)

        for ev in ("<KeyRelease>", "<ButtonRelease-1>", "<<Paste>>", "<<Cut>>"):
            self._text.bind(ev, self._refresh_gutter, add="+")
        self._text.bind("<Configure>", self._refresh_gutter, add="+")
        self._text.bind("<MouseWheel>", self._sync_gutter_yview)
        self._text.bind("<Button-4>", self._sync_gutter_yview)
        self._text.bind("<Button-5>", self._sync_gutter_yview)

        self._refresh_gutter()

    def _on_scrollbar(self, *args: Any) -> None:
        self._text.yview(*args)
        self._sync_gutter_yview()

    def _on_text_yscroll(self, first: str, last: str) -> None:
        self._scroll.set(first, last)
        self._sync_gutter_yview()

    def _sync_gutter_yview(self, _event: Any = None) -> None:
        try:
            self._gutter.yview_moveto(self._text.yview()[0])
        except tk.TclError:
            pass

    def _refresh_gutter(self, _event: Any = None) -> None:
        try:
            end_idx = self._text.index("end-1c")
            n = int(end_idx.split(".")[0])
            if n < 1:
                n = 1
            lines = "\n".join(str(i) for i in range(1, n + 1))
            self._gutter.config(state="normal")
            self._gutter.delete("1.0", "end")
            self._gutter.insert("1.0", lines)
            self._gutter.config(state="disabled")
            self._sync_gutter_yview()
        except tk.TclError:
            pass
        return None

    # --- делегирование к основному tk.Text ---
    def get(self, *args: Any, **kwargs: Any) -> Any:
        return self._text.get(*args, **kwargs)

    def insert(self, *args: Any, **kwargs: Any) -> Any:
        r = self._text.insert(*args, **kwargs)
        self._refresh_gutter()
        return r

    def delete(self, *args: Any, **kwargs: Any) -> Any:
        r = self._text.delete(*args, **kwargs)
        self._refresh_gutter()
        return r

    def tag_configure(self, *args: Any, **kwargs: Any) -> Any:
        return self._text.tag_configure(*args, **kwargs)

    def tag_config(self, *args: Any, **kwargs: Any) -> Any:
        """Алиас как у tk.Text / CTkTextbox; app.py вызывает tag_config."""
        return self._text.tag_configure(*args, **kwargs)

    def tag_add(self, *args: Any, **kwargs: Any) -> Any:
        return self._text.tag_add(*args, **kwargs)

    def tag_remove(self, *args: Any, **kwargs: Any) -> Any:
        return self._text.tag_remove(*args, **kwargs)

    def focus_set(self) -> None:
        self._text.focus_set()

    def focus_force(self) -> None:
        self._text.focus_force()

    def bell(self) -> None:
        self._text.bell()

    def set_read_only(self, ro: bool) -> None:
        """Только просмотр (эталон в модалке): отключает правку текста."""
        self._text.config(state=("disabled" if ro else "normal"))


def editor_colors_for_theme(mode: str) -> tuple[str, str, str, str]:
    """bg_main, bg_gutter, fg, fg_dim."""
    m = (mode or "dark").strip().lower()
    if m == "system":
        m = "dark"
    if m == "light":
        return "#FFFFFF", "#FFF5F9", "#2D1B2E", "#9E7A8A"
    return "#252028", "#1a1520", "#F0E6EB", "#8a7a85"


def apply_editor_theme(panel: CodeEditorPanel, mode: str) -> None:
    bg_m, bg_g, fg, fg_d = editor_colors_for_theme(mode)
    panel._bg_main = bg_m
    panel._bg_gutter = bg_g
    panel._fg = fg
    panel._fg_dim = fg_d
    tk.Frame.configure(panel, bg=bg_m)
    panel._gutter.config(bg=bg_g, fg=fg_d, insertbackground=fg, selectbackground=bg_g)
    panel._text.config(bg=bg_m, fg=fg, insertbackground=fg)


def build_editor(parent: ctk.CTkFrame, appearance_getter: Callable[[], str]) -> CodeEditorPanel:
    mode = appearance_getter()
    bg_m, bg_g, fg, fg_d = editor_colors_for_theme(mode)
    panel = CodeEditorPanel(
        parent,
        bg_main=bg_m,
        bg_gutter=bg_g,
        fg=fg,
        fg_dim=fg_d,
        font=("Consolas", 14),
    )
    return panel
