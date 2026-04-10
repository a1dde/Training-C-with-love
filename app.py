from __future__ import annotations

import random
import sys
import threading
from typing import Callable

import customtkinter as ctk

from achievements import achievement_catalog_rows, update_achievements
from csharp_reference import FULL_REFERENCE_TEXT
from engagement_content import (
    FIVE_MIN_QUESTS,
    JUNIOR_DAY_STEPS,
    MENTOR_LETTERS,
    ROADMAP_PHASES,
    weekly_digest_text,
)
from ide_editor import CodeEditorPanel, apply_editor_theme, build_editor
from levels_data import (
    BOSS_CHOICES,
    DAILY_EVENTS,
    FINAL_PROJECT_TRACKS,
    GLOSSARY,
    LEVELS,
    WEEKLY_EVENTS,
    level_short_name,
)
from memes import random_existing_meme
from pet_cosmetics import PET_COSMETICS
from pet_tamagotchi import PetTamagotchi
from progress import (
    finalize_chapter_and_project,
    load_progress,
    lose_life,
    milestone_caption,
    pet_stage,
    reset_lives,
    save_progress,
)
from resources import resource_path
from ui_helpers import CORAL_ACCENT, PINK_HOVER, PINK_PRIMARY, attach_popup, messagebox_with_parent

_UI_WRAP_MAIN = 720
_UI_WRAP_STATUS = 420
from validators import validate_level, validate_rules, validation_status_message

try:
    from CTkMessagebox import CTkMessagebox
except Exception:  # pragma: no cover
    CTkMessagebox = None

try:
    from customtkinter import CTkImage
except Exception:  # pragma: no cover
    CTkImage = None  # type: ignore[misc, assignment]

try:
    from PIL import Image
except Exception:  # pragma: no cover
    Image = None  # type: ignore[misc, assignment]


class MeowAcademyApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("C# Meow Academy 🐾")
        self.geometry("1280x820")
        self.minsize(1100, 720)
        self._apply_window_icon()

        self.progress = load_progress()
        self.attempt_count = 0
        self.current_level = int(self.progress.get("selected_level", 1))
        self.level_buttons: dict[int, ctk.CTkButton] = {}
        self._burnout_nag_shown = False
        self._love_after_id: object | None = None
        self._validation_busy = False
        self._boss_ctk_image = None

        ctk.set_appearance_mode(self.progress.get("theme", "dark"))
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self._build_layout()
        apply_editor_theme(self.code_editor, self.progress.get("theme", "dark"))
        self._render_level(self.current_level)
        self._refresh_sidebar()
        self._refresh_progress_labels()
        self._refresh_code_highlight_theme()
        self._schedule_love_reminder()

    def _on_close(self) -> None:
        self._cancel_love_reminder()
        self.destroy()

    def _msg(self, **kwargs: object):
        if not CTkMessagebox:
            return None
        return messagebox_with_parent(self, CTkMessagebox, **kwargs)

    def _popup(self, win: ctk.CTkToplevel) -> None:
        attach_popup(self, win)

    def _toggle_love_reminder(self) -> None:
        """Переключатель: раз в ~30 мин показывать мягкое окно «Я тебя люблю» (см. _show_love_reminder)."""
        self.progress["love_reminder_enabled"] = bool(self.btn_love_reminder.get())
        save_progress(self.progress)
        if self.progress["love_reminder_enabled"]:
            self._schedule_love_reminder()
            self.status_label.configure(
                text="💖 Напоминание включено: примерно раз в 30 минут всплывёт окошко с любовью от котика."
            )
        else:
            self._cancel_love_reminder()
            self.status_label.configure(text="Напоминание любви выключено — переключатель можно снова включить.")

    def _build_layout(self) -> None:
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.topbar = ctk.CTkFrame(self, corner_radius=12)
        self.topbar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 6))
        self.topbar.grid_columnconfigure(0, weight=1)

        top_stats = ctk.CTkFrame(self.topbar, fg_color="transparent")
        top_stats.grid(row=0, column=0, sticky="ew", padx=6, pady=(8, 4))
        top_stats.grid_columnconfigure(4, weight=1)

        self.label_progress = ctk.CTkLabel(top_stats, text="")
        self.label_progress.grid(row=0, column=0, padx=(4, 10), pady=4)

        self.label_remaining = ctk.CTkLabel(top_stats, text="")
        self.label_remaining.grid(row=0, column=1, padx=(0, 10), pady=4)

        self.label_lives = ctk.CTkLabel(top_stats, text="")
        self.label_lives.grid(row=0, column=2, padx=(0, 10), pady=4)

        self.label_kitten_points = ctk.CTkLabel(top_stats, text="", font=ctk.CTkFont(size=13, weight="bold"))
        self.label_kitten_points.grid(row=0, column=3, padx=(0, 10), pady=4)

        self.theme_toggle = ctk.CTkSegmentedButton(
            top_stats,
            values=["dark", "light"],
            command=self._on_theme_change,
            width=130,
        )
        self.theme_toggle.set(self.progress.get("theme", "dark"))
        self.theme_toggle.grid(row=0, column=5, padx=(8, 4), pady=4, sticky="e")

        top_actions = ctk.CTkFrame(self.topbar, fg_color="transparent")
        top_actions.grid(row=1, column=0, sticky="ew", padx=6, pady=(2, 8))
        for c in range(8):
            top_actions.grid_columnconfigure(c, weight=0)
        top_actions.grid_columnconfigure(8, weight=1)

        self.btn_glossary = ctk.CTkButton(top_actions, text="Справочник 🐾", command=self._open_glossary, width=128)
        self.btn_glossary.grid(row=0, column=0, padx=3, pady=2)

        self.btn_boss = ctk.CTkButton(top_actions, text="Босс 👑", command=self._open_boss_fight, width=88)
        self.btn_boss.grid(row=0, column=1, padx=3, pady=2)

        self.btn_event = ctk.CTkButton(top_actions, text="Daily ⚡", command=self._open_daily_event, width=82)
        self.btn_event.grid(row=0, column=2, padx=3, pady=2)

        self.btn_weekly = ctk.CTkButton(top_actions, text="Weekly 🌙", command=self._open_weekly_event, width=88)
        self.btn_weekly.grid(row=0, column=3, padx=3, pady=2)

        self.btn_ach = ctk.CTkButton(top_actions, text="Награды 🏅", command=self._open_achievements, width=102)
        self.btn_ach.grid(row=0, column=4, padx=3, pady=2)

        self.btn_sound = ctk.CTkSwitch(top_actions, text="Звук 🔊", command=self._toggle_sound)
        if self.progress.get("sound_enabled", True):
            self.btn_sound.select()
        self.btn_sound.grid(row=0, column=5, padx=(10, 6), pady=2, sticky="w")

        self.btn_love_reminder = ctk.CTkSwitch(
            top_actions,
            text="Напоминание 💕",
            command=self._toggle_love_reminder,
        )
        if self.progress.get("love_reminder_enabled", True):
            self.btn_love_reminder.select()
        self.btn_love_reminder.grid(row=0, column=6, padx=4, pady=2, sticky="w")

        self.meta_bar = ctk.CTkFrame(self, corner_radius=12)
        self.meta_bar.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 4))
        self.meta_bar.grid_columnconfigure(1, weight=1)

        self.label_milestone = ctk.CTkLabel(
            self.meta_bar,
            text="",
            anchor="w",
            justify="left",
            wraplength=400,
        )
        self.label_milestone.grid(row=0, column=0, padx=10, pady=(8, 4), sticky="nw")
        self.chapter_progress = ctk.CTkProgressBar(self.meta_bar, height=14)
        self.chapter_progress.grid(row=0, column=1, padx=8, pady=(10, 4), sticky="ew")

        meta_btns = ctk.CTkFrame(self.meta_bar, fg_color="transparent")
        meta_btns.grid(row=1, column=0, columnspan=2, sticky="ew", padx=6, pady=(0, 8))
        for c in range(5):
            meta_btns.grid_columnconfigure(c, weight=0)
        meta_btns.grid_columnconfigure(5, weight=1)

        self.btn_path = ctk.CTkButton(meta_btns, text="Карта 🗺️", width=100, command=self._open_path_map)
        self.btn_path.grid(row=0, column=0, padx=3, pady=2)
        self.btn_final = ctk.CTkButton(meta_btns, text="Финал 🎓", width=108, command=self._open_final_project_hub)
        self.btn_final.grid(row=0, column=1, padx=3, pady=2)
        self.btn_care = ctk.CTkButton(meta_btns, text="Забота 🐾", width=100, command=self._open_care_hub)
        self.btn_care.grid(row=0, column=2, padx=3, pady=2)
        self.btn_digest = ctk.CTkButton(meta_btns, text="Дайджест 📰", width=102, command=self._open_weekly_digest)
        self.btn_digest.grid(row=0, column=3, padx=3, pady=2)

        self.sidebar = ctk.CTkFrame(self, width=252, corner_radius=14)
        self.sidebar.grid(row=2, column=0, sticky="nsw", padx=(10, 6), pady=(0, 10))
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(11, weight=1)

        ctk.CTkLabel(self.sidebar, text="Глава A · вперёд лапками", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, padx=10, pady=(10, 6), sticky="w"
        )

        for level in LEVELS:
            lid = level["id"]
            sn = level_short_name(level)
            label = f"{lid}. {sn}"
            if len(label) > 40:
                label = label[:38] + "…"
            btn = ctk.CTkButton(
                self.sidebar,
                text=label,
                width=220,
                height=36,
                font=ctk.CTkFont(size=12),
                command=lambda x=lid: self._try_select_level(x),
            )
            btn.grid(row=lid, column=0, padx=10, pady=3, sticky="ew")
            self.level_buttons[lid] = btn

        self.sidebar_points = ctk.CTkLabel(self.sidebar, text="", justify="center", font=ctk.CTkFont(size=12))
        self.sidebar_points.grid(row=11, column=0, padx=10, pady=(8, 10), sticky="s")

        self.main = ctk.CTkFrame(self, fg_color="transparent")
        self.main.grid(row=2, column=1, sticky="nsew", padx=(6, 10), pady=(0, 10))
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(0, weight=1)

        self.main_tabs = ctk.CTkTabview(
            self.main,
            corner_radius=14,
            border_width=1,
            border_color=("#F8BBD9", "#6D3756"),
            command=self._on_main_tab_changed,
        )
        self.main_tabs.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)

        tab_lesson = self.main_tabs.add("Урок 💻")
        tab_pet = self.main_tabs.add("Котик 🐾")

        tab_lesson.grid_columnconfigure(0, weight=1)
        tab_lesson.grid_rowconfigure(1, weight=1, minsize=280)

        self.quest_card = ctk.CTkFrame(
            tab_lesson,
            corner_radius=18,
            border_width=1,
            border_color=("#F8BBD9", "#6D3756"),
            fg_color=("#FFF5FA", "#2A1F26"),
        )
        self.quest_card.grid(row=0, column=0, sticky="ew", padx=8, pady=(4, 8))
        self.quest_card.grid_columnconfigure(0, weight=1)

        self.level_title = ctk.CTkLabel(
            self.quest_card,
            text="",
            font=ctk.CTkFont(size=20, weight="bold"),
            anchor="w",
        )
        self.level_title.grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 6))

        self.wisdom_box = ctk.CTkTextbox(self.quest_card, height=88, wrap="word", font=ctk.CTkFont(size=13))
        self.wisdom_box.grid(row=1, column=0, sticky="ew", padx=12, pady=4)

        self.mission_box = ctk.CTkTextbox(self.quest_card, height=80, wrap="word", font=ctk.CTkFont(size=13))
        self.mission_box.grid(row=2, column=0, sticky="ew", padx=12, pady=(4, 12))

        self.editor_panel = ctk.CTkFrame(tab_lesson, fg_color="transparent")
        self.editor_panel.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 4))
        self.editor_panel.grid_columnconfigure(0, weight=1)
        self.editor_panel.grid_rowconfigure(1, weight=1)

        editor_head = ctk.CTkFrame(self.editor_panel, fg_color="transparent")
        editor_head.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        ctk.CTkLabel(
            editor_head,
            text="Редактор кода",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("#AD1457", "#F8BBD9"),
        ).pack(side="left")
        tab_chip = ctk.CTkFrame(editor_head, corner_radius=9, border_width=1, border_color=("#F48FB1", "#8E4A66"))
        tab_chip.pack(side="left", padx=(14, 0))
        ctk.CTkLabel(tab_chip, text=" Program.cs ", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=4, pady=5)
        ctk.CTkLabel(
            tab_chip,
            text="· C# · твой учебный файл",
            font=ctk.CTkFont(size=11),
            text_color=("gray45", "gray60"),
        ).pack(side="left", padx=(0, 8), pady=5)

        ide_shell = ctk.CTkFrame(self.editor_panel, corner_radius=14, border_width=2, border_color=("#F8BBD9", "#AD5270"))
        ide_shell.grid(row=1, column=0, sticky="nsew")
        ide_shell.grid_columnconfigure(0, weight=1)
        ide_shell.grid_rowconfigure(0, weight=1)

        self.code_editor = build_editor(ide_shell, lambda: ctk.get_appearance_mode())
        self.code_editor.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        self.code_box = self.code_editor

        row = ctk.CTkFrame(tab_lesson, fg_color="transparent")
        row.grid(row=2, column=0, sticky="ew", padx=8, pady=(4, 2))
        row.grid_columnconfigure(2, weight=1)

        self.btn_check = ctk.CTkButton(row, text="Проверить 💕", command=self._check_code, fg_color=PINK_PRIMARY, hover_color=PINK_HOVER)
        self.btn_check.grid(row=0, column=0, padx=(0, 8))

        self.btn_ref = ctk.CTkButton(row, text="Эталон", width=86, command=self._show_level_reference)
        self.btn_ref.grid(row=0, column=1, padx=(0, 8))

        self.status_label = ctk.CTkLabel(
            row,
            text="",
            anchor="w",
            justify="left",
            wraplength=_UI_WRAP_STATUS,
        )
        self.status_label.grid(row=0, column=2, sticky="ew")

        self.checklist_label = ctk.CTkLabel(
            tab_lesson,
            text="Нажми «Проверить 💕» — котик проверит C# быстро; кнопки на месте, ничего не уезжает.",
            anchor="w",
            justify="left",
            wraplength=_UI_WRAP_MAIN,
        )
        self.checklist_label.grid(row=3, column=0, sticky="ew", padx=8, pady=(2, 10))

        tab_pet.grid_columnconfigure(0, weight=1)
        tab_pet.grid_rowconfigure(0, weight=1)

        self.pet_strip = ctk.CTkFrame(
            tab_pet,
            corner_radius=18,
            border_width=2,
            border_color=("#F8BBD9", "#5C2338"),
            fg_color=("#FFFBFD", "#251820"),
        )
        self.pet_strip.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        self.pet_strip.grid_columnconfigure(1, weight=1)

        pet_left = ctk.CTkFrame(self.pet_strip, fg_color="transparent")
        pet_left.grid(row=0, column=0, padx=(14, 10), pady=12, sticky="nw")
        self.pet_widget = PetTamagotchi(pet_left, width=210, height=230)
        self.pet_widget.pack()

        pet_mid = ctk.CTkFrame(self.pet_strip, fg_color="transparent")
        pet_mid.grid(row=0, column=1, padx=8, pady=12, sticky="ew")
        self.pet_growth_title = ctk.CTkLabel(
            pet_mid,
            text="Тамагочи: котик растёт с твоим уровнем",
            font=ctk.CTkFont(size=15, weight="bold"),
            anchor="w",
        )
        self.pet_growth_title.pack(anchor="w")
        self.pet_growth_detail = ctk.CTkLabel(pet_mid, text="", anchor="w", justify="left")
        self.pet_growth_detail.pack(anchor="w", pady=(2, 6))
        self.pet_growth_bar = ctk.CTkProgressBar(pet_mid, width=280, height=12)
        self.pet_growth_bar.pack(fill="x", pady=(0, 4))
        self.pet_growth_hint = ctk.CTkLabel(
            pet_mid,
            text="Каждый пройденный уровень делает котика крупнее. Купленные украшения видны на нём — в магазине «Забота».",
            font=ctk.CTkFont(size=11),
            text_color=("gray35", "gray60"),
            anchor="w",
            wraplength=420,
        )
        self.pet_growth_hint.pack(anchor="w")

        pet_right = ctk.CTkFrame(self.pet_strip, fg_color="transparent")
        pet_right.grid(row=0, column=2, padx=(14, 16), pady=12, sticky="ne")
        self.pet_points_strip = ctk.CTkLabel(
            pet_right,
            text="",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("#AD1457", "#F8BBD9"),
        )
        self.pet_points_strip.pack(anchor="e")

    def _on_main_tab_changed(self) -> None:
        """Вкладка «Котик» после показа даёт корректный размер canvas (не 1×1)."""
        try:
            if self.main_tabs.get() == "Котик 🐾":
                self.after(60, self.pet_widget.refresh_geometry)
        except Exception:
            pass

    def _try_select_level(self, level_id: int) -> None:
        unlocked = set(self.progress.get("unlocked_levels", [1]))
        if level_id not in unlocked:
            self.status_label.configure(
                text="🔒 Уровень закрыт — сначала заверши предыдущий, и котик откроет следующий."
            )
            return
        self._select_level(level_id)

    def _embed_ide_editor(self, parent: ctk.CTkFrame) -> CodeEditorPanel:
        """Тот же вид, что у уровня: рамка + gutter + Consolas."""
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        ide_shell = ctk.CTkFrame(
            parent,
            corner_radius=14,
            border_width=2,
            border_color=("#F8BBD9", "#AD5270"),
        )
        ide_shell.grid(row=0, column=0, sticky="nsew")
        ide_shell.grid_rowconfigure(0, weight=1)
        ide_shell.grid_columnconfigure(0, weight=1)
        editor = build_editor(ide_shell, lambda: ctk.get_appearance_mode())
        editor.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        apply_editor_theme(editor, self.progress.get("theme", "dark"))
        return editor

    def _pack_modal_code_editor(self, win: ctk.CTkToplevel, initial_code: str, *, read_only: bool = False) -> CodeEditorPanel:
        head = ctk.CTkFrame(win, fg_color="transparent")
        head.pack(fill="x", padx=10, pady=(4, 6))
        ctk.CTkLabel(
            head,
            text="Редактор кода",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#AD1457", "#F8BBD9"),
        ).pack(side="left")
        tab_chip = ctk.CTkFrame(head, corner_radius=9, border_width=1, border_color=("#F48FB1", "#8E4A66"))
        tab_chip.pack(side="left", padx=(12, 0))
        ctk.CTkLabel(tab_chip, text=" Program.cs ", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=4, pady=4)
        ctk.CTkLabel(
            tab_chip,
            text="· C#",
            font=ctk.CTkFont(size=11),
            text_color=("gray45", "gray60"),
        ).pack(side="left", padx=(0, 8), pady=4)
        mid = ctk.CTkFrame(win, fg_color="transparent")
        mid.pack(fill="both", expand=True, padx=10, pady=(0, 8))
        editor = self._embed_ide_editor(mid)
        editor.insert("1.0", initial_code)
        if read_only:
            editor.set_read_only(True)
        return editor

    def _open_glossary(self) -> None:
        win = ctk.CTkToplevel(self)
        self._popup(win)
        win.title("Справочник C# — от основ до джуна")
        win.geometry("820x640")
        ctk.CTkLabel(
            win,
            text="Операторы, массивы, коллекции, строки, ООП, async и ИБ — от основ до первой работы. Во второй вкладке краткий глоссарий A–Я.",
            wraplength=780,
            justify="left",
            font=ctk.CTkFont(size=13),
        ).pack(anchor="w", padx=14, pady=(12, 4))
        tabs = ctk.CTkTabview(win)
        tabs.pack(fill="both", expand=True, padx=10, pady=(4, 10))
        t1 = tabs.add("Обзор")
        t2 = tabs.add("Термины A–Я")
        box1 = ctk.CTkTextbox(t1, wrap="word", font=ctk.CTkFont(size=13))
        box1.pack(fill="both", expand=True, padx=6, pady=6)
        box1.insert("1.0", FULL_REFERENCE_TEXT)
        box1.configure(state="disabled")
        box2 = ctk.CTkTextbox(t2, wrap="word", font=ctk.CTkFont(size=12))
        box2.pack(fill="both", expand=True, padx=6, pady=6)
        lines = ["Глоссарий (кратко)\n"]
        for key, value in sorted(GLOSSARY.items(), key=lambda kv: kv[0].lower()):
            lines.append(f"• {key}: {value}\n")
        box2.insert("1.0", "\n".join(lines))
        box2.configure(state="disabled")

    def _open_achievements(self) -> None:
        win = ctk.CTkToplevel(self)
        self._popup(win)
        win.title("Достижения — витрина наград")
        win.geometry("620x520")
        ctk.CTkLabel(
            win,
            text="Здесь твои награды 💖 Категории: сюжет, навыки, ИБ, регулярность, уют. Редкость растёт вместе с тобой.",
            wraplength=580,
            justify="left",
        ).pack(anchor="w", padx=12, pady=(10, 4))
        scroll = ctk.CTkScrollableFrame(win, height=420)
        scroll.pack(fill="both", expand=True, padx=10, pady=8)
        for row in achievement_catalog_rows(self.progress):
            icon = "🏅" if row["unlocked"] else "🔒"
            fr = ctk.CTkFrame(scroll, fg_color="transparent")
            fr.pack(fill="x", pady=3)
            ctk.CTkLabel(
                fr,
                text=f"{icon} {row['title']}  ·  {row['category']}  ·  {row['rarity']}",
                anchor="w",
            ).pack(fill="x")
            bar = ctk.CTkProgressBar(fr, width=400)
            bar.set(row["progress_pct"] / 100.0)
            bar.pack(fill="x", pady=(2, 0))
            ctk.CTkLabel(fr, text=row["progress_label"], font=ctk.CTkFont(size=11)).pack(anchor="w")

    def _boss_image(self):
        if self._boss_ctk_image is not None:
            return self._boss_ctk_image
        path = resource_path("assets", "boss_kitten_throne.png")
        if CTkImage and Image and path.is_file():
            try:
                pil = Image.open(path).convert("RGBA")
                self._boss_ctk_image = CTkImage(light_image=pil, dark_image=pil, size=(88, 88))
            except OSError:
                self._boss_ctk_image = None
        else:
            self._boss_ctk_image = None
        return self._boss_ctk_image

    def _open_boss_fight(self) -> None:
        win = ctk.CTkToplevel(self)
        self._popup(win)
        win.title("Выбор босса")
        win.geometry("620x480")
        ctk.CTkLabel(win, text="Финальный босс в троне 🔥", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        img = self._boss_image()
        for boss in BOSS_CHOICES:
            row = ctk.CTkFrame(win, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=8)
            if img:
                ctk.CTkLabel(row, text="", image=img).pack(side="left", padx=(0, 12))
            else:
                ctk.CTkLabel(row, text="👑", font=ctk.CTkFont(size=36)).pack(side="left", padx=(0, 12))
            ctk.CTkButton(
                row,
                text=boss["title"],
                command=lambda b=boss: self._open_boss_editor(b),
                fg_color=CORAL_ACCENT,
                hover_color="#FF7043",
            ).pack(side="left", fill="x", expand=True)

    def _open_boss_editor(self, boss: dict) -> None:
        win = ctk.CTkToplevel(self)
        self._popup(win)
        win.title(boss["title"])
        win.geometry("800x620")
        head = ctk.CTkFrame(win, fg_color="transparent")
        head.pack(fill="x", padx=10, pady=(8, 4))
        img = self._boss_image()
        if img:
            ctk.CTkLabel(head, text="", image=img).pack(side="left", padx=(0, 12))
        else:
            ctk.CTkLabel(head, text="👑", font=ctk.CTkFont(size=40)).pack(side="left")
        ctk.CTkLabel(head, text=boss["mission"], wraplength=620, justify="left").pack(side="left", fill="x", expand=True)
        editor = self._pack_modal_code_editor(win, boss["starter_code"])
        status = ctk.CTkLabel(win, text="Котоинтеллект готов к бою 🛡️")
        status.pack(anchor="w", padx=10, pady=(0, 8))

        def _check() -> None:
            result = validate_rules(boss["rules"], editor.get("1.0", "end-1c"), 1, {})
            if result["ok"]:
                completed = set(self.progress.get("completed_bosses", []))
                completed.add(boss["id"])
                self.progress["completed_bosses"] = sorted(completed)
                self.progress["kitten_points"] = int(self.progress.get("kitten_points", 0)) + 25
                new_ach = update_achievements(self.progress)
                save_progress(self.progress)
                extra = ""
                if new_ach:
                    extra = "\nНовые достижения:\n- " + "\n- ".join(new_ach)
                status.configure(text=f"Победа! Босс {boss['title']} повержен 🐱{extra}")
                self._play_meow()
            else:
                status.configure(text=f"Пока не победа. {validation_status_message(result)}")

        ctk.CTkButton(win, text="Проверить босса", command=_check, fg_color=CORAL_ACCENT, hover_color="#FF7043").pack(
            padx=10, pady=8, anchor="e"
        )

    def _open_daily_event(self) -> None:
        event = DAILY_EVENTS[random.randint(0, len(DAILY_EVENTS) - 1)]
        win = ctk.CTkToplevel(self)
        self._popup(win)
        win.title(event["title"])
        win.geometry("780x560")
        ctk.CTkLabel(win, text=event["mission"], wraplength=720, justify="left").pack(anchor="w", padx=10, pady=8)
        editor = self._pack_modal_code_editor(win, event.get("starter_code") or "// Daily · пиши код здесь сама\n\n")
        status = ctk.CTkLabel(win, text="Daily ивент ждёт твой код 💫")
        status.pack(anchor="w", padx=10, pady=(0, 8))

        def _check_daily() -> None:
            result = validate_rules(
                event["rules"],
                editor.get("1.0", "end-1c"),
                1,
                event.get("hints"),
            )
            if result["ok"]:
                self.progress["daily_events_done"] = int(self.progress.get("daily_events_done", 0)) + 1
                self.progress["kitten_points"] = int(self.progress.get("kitten_points", 0)) + 8
                update_achievements(self.progress)
                save_progress(self.progress)
                status.configure(text="Daily закрыт! Котик гордится тобой 🐾")
                self._play_meow()
            else:
                status.configure(text=f"Почти! {validation_status_message(result)}")

        ctk.CTkButton(win, text="Проверить daily", command=_check_daily).pack(padx=10, pady=8, anchor="e")

    def _open_weekly_event(self) -> None:
        event = WEEKLY_EVENTS[random.randint(0, len(WEEKLY_EVENTS) - 1)]
        win = ctk.CTkToplevel(self)
        self._popup(win)
        win.title(event["title"])
        win.geometry("780x560")
        ctk.CTkLabel(win, text=event["mission"], wraplength=720, justify="left").pack(anchor="w", padx=10, pady=8)
        editor = self._pack_modal_code_editor(win, event.get("starter_code") or "// Weekly · твоё решение с нуля\n\n")
        status = ctk.CTkLabel(win, text="Weekly ивент ждёт твой код 🌟")
        status.pack(anchor="w", padx=10, pady=(0, 8))

        def _check_weekly() -> None:
            result = validate_rules(
                event["rules"],
                editor.get("1.0", "end-1c"),
                1,
                event.get("hints"),
            )
            if result["ok"]:
                self.progress["weekly_events_done"] = int(self.progress.get("weekly_events_done", 0)) + 1
                if "security" in event["id"]:
                    self.progress["security_events_done"] = int(self.progress.get("security_events_done", 0)) + 1
                self.progress["kitten_points"] = int(self.progress.get("kitten_points", 0)) + 15
                update_achievements(self.progress)
                save_progress(self.progress)
                status.configure(text="Weekly закрыт! Котик хлопает лапками 👏")
                self._play_meow()
            else:
                status.configure(text=f"Почти! {validation_status_message(result)}")

        ctk.CTkButton(win, text="Проверить weekly", command=_check_weekly).pack(padx=10, pady=8, anchor="e")

    def _toggle_sound(self) -> None:
        self.progress["sound_enabled"] = bool(self.btn_sound.get())
        save_progress(self.progress)

    def _on_theme_change(self, value: str) -> None:
        ctk.set_appearance_mode(value)
        self.progress["theme"] = value
        save_progress(self.progress)
        apply_editor_theme(self.code_editor, value)
        self._refresh_code_highlight_theme()
        self._refresh_sidebar()
        self._refresh_meta_and_pet()

    def _select_level(self, level_id: int) -> None:
        if level_id not in self.progress.get("unlocked_levels", [1]):
            return
        self.current_level = level_id
        self.progress["selected_level"] = level_id
        save_progress(self.progress)
        self.attempt_count = 0
        self._render_level(level_id)
        self._refresh_sidebar()

    def _render_level(self, level_id: int) -> None:
        level = LEVELS[level_id - 1]
        self.level_title.configure(text=level["title"])
        self._set_ro_text(self.wisdom_box, f"🐱 Лапка-подсказка\n\n{level['wisdom']}")
        self._set_ro_text(self.mission_box, f"🎯 Задание квеста\n\n{level['mission']}")
        self.code_box.delete("1.0", "end")
        self.code_box.insert("1.0", level["starter_code"])
        self._clear_highlight_tags()
        self.status_label.configure(text="Котик ждёт твоё решение 💖")
        self._update_checklist(None, level_id)

    def _set_ro_text(self, box: ctk.CTkTextbox, text: str) -> None:
        box.configure(state="normal")
        box.delete("1.0", "end")
        box.insert("1.0", text)
        box.configure(state="disabled")

    def _apply_window_icon(self) -> None:
        """Иконка лапки: Windows — .ico (окно + задача); иначе PNG через PhotoImage."""
        ico = resource_path("assets", "paw_icon.ico")
        png = resource_path("assets", "paw_icon.png")
        try:
            if sys.platform == "win32" and ico.is_file():
                # Абсолютный путь: иначе Tk на Windows может не найти ico рядом с exe/временной папкой
                p = str(ico.resolve())
                self.iconbitmap(p)
                try:
                    self.iconbitmap(default=p)
                except Exception:
                    pass
            if png.is_file():
                try:
                    from PIL import Image, ImageTk

                    img = Image.open(png)
                    if img.size[0] > 64 or img.size[1] > 64:
                        try:
                            resample = Image.Resampling.LANCZOS
                        except AttributeError:
                            resample = Image.LANCZOS
                        img = img.resize((64, 64), resample)
                    self._window_icon_photo = ImageTk.PhotoImage(img)
                    self.iconphoto(True, self._window_icon_photo)
                except ImportError:
                    pass
        except OSError:
            pass

    def _refresh_sidebar(self) -> None:
        unlocked = set(self.progress.get("unlocked_levels", [1]))
        theme_btn = ctk.ThemeManager.theme["CTkButton"]
        default_fg = theme_btn["fg_color"]
        default_hover = theme_btn["hover_color"]
        default_txt = theme_btn["text_color"]
        locked_fg = ("#DDD5E8", "#4A3F50")
        locked_hover = ("#D0C8E0", "#5A5262")
        locked_txt = ("#4A3558", "#E8DCE8")
        for lid, btn in self.level_buttons.items():
            if lid not in unlocked:
                btn.configure(
                    state="normal",
                    fg_color=locked_fg,
                    hover_color=locked_hover,
                    text_color=locked_txt,
                )
            elif lid == self.current_level:
                btn.configure(
                    state="normal",
                    fg_color=PINK_PRIMARY,
                    hover_color=PINK_HOVER,
                    text_color=("#FAFAFA", "#FAFAFA"),
                )
            else:
                btn.configure(
                    state="normal",
                    fg_color=default_fg,
                    hover_color=default_hover,
                    text_color=default_txt,
                )

    def _refresh_progress_labels(self) -> None:
        completed = len(self.progress.get("completed_levels", []))
        total = len(LEVELS)
        remaining = max(0, total - completed)
        lives_max = max(1, int(self.progress.get("lives_max", 3)))
        lives = max(0, min(int(self.progress.get("lives_current", 3)), lives_max))
        hearts = "❤️" * lives + "🖤" * (lives_max - lives)
        self.label_progress.configure(text=f"Пройдено: {completed}/{total}")
        self.label_remaining.configure(text=f"Осталось уровней: {remaining}")
        self.label_lives.configure(text=f"Жизни: {hearts}")
        kp = int(self.progress.get("kitten_points", 0))
        self.label_kitten_points.configure(text=f"🐾 {kp} очков")
        self.sidebar_points.configure(text=f"🐾\n{kp}")
        self._refresh_meta_and_pet()

    def _refresh_meta_and_pet(self) -> None:
        finalize_chapter_and_project(self.progress, total_levels=len(LEVELS))
        self.label_milestone.configure(text=milestone_caption(self.progress, total_levels=len(LEVELS)))
        done_n = len(self.progress.get("completed_levels", []))
        self.chapter_progress.set(min(1.0, done_n / max(1, len(LEVELS))))
        if self.progress.get("final_project_done"):
            self.btn_final.configure(state="disabled", text="Финал ✓")
        elif self.progress.get("final_project_unlocked"):
            self.btn_final.configure(state="normal", text="Финал 🎓")
        else:
            self.btn_final.configure(state="disabled", text="Финал 🔒")
        st = pet_stage(done_n)
        pts = int(self.progress.get("kitten_points", 0))
        purchased = list(self.progress.get("purchased_cosmetics", []))
        self.pet_widget.set_state(st, purchased)
        total_lv = len(LEVELS)
        self.pet_growth_detail.configure(
            text=f"Стадия роста: {st + 1} из 5  ·  пройдено уровней: {done_n} из {total_lv}"
        )
        self.pet_growth_bar.set(min(1.0, done_n / max(1, total_lv)))
        self.pet_points_strip.configure(text=f"{pts}\nлапок")

    def _check_code(self) -> None:
        if self._validation_busy:
            return
        code = self.code_box.get("1.0", "end-1c")
        self.attempt_count += 1
        self.progress["total_attempts"] = int(self.progress.get("total_attempts", 0)) + 1
        self._validation_busy = True
        self.btn_check.configure(state="disabled")
        self.status_label.configure(text="Проверяю код в фоне…")
        self.update_idletasks()
        level_id = self.current_level
        attempt = self.attempt_count

        def _work() -> None:
            result = validate_level(level_id, code, attempt)
            self.after(0, lambda res=result: self._apply_validation_result(res))

        threading.Thread(target=_work, daemon=True).start()

    def _apply_validation_result(self, result: dict) -> None:
        self._validation_busy = False
        try:
            self.btn_check.configure(state="normal")
        except Exception:
            pass
        self._apply_highlights(result["good_spans"], result["bad_spans"])
        self._update_checklist(result, self.current_level)

        if result["ok"]:
            self._on_success(result["score"])
            return
        self.progress["session_fail_streak"] = int(self.progress.get("session_fail_streak", 0)) + 1
        hint = result["hint"]
        if self.progress.get("anxiety_care_mode"):
            hint += " 💕 Ты в безопасности: дышим медленно, шаг за шагом."
        soft = bool(self.progress.get("soft_mode_no_lives"))
        if soft:
            msg = f"Мягкий режим: жизни не тратятся. {hint}"
        else:
            msg = f"Упс! Кажется, котик запутался в ниточках. {hint}"
        self.status_label.configure(text=msg)
        if not soft:
            lives_left = lose_life(self.progress)
        else:
            lives_left = int(self.progress.get("lives_current", 3))
        save_progress(self.progress)
        if not soft and lives_left == 0:
            self._show_life_reset_modal()
        self._refresh_progress_labels()
        if self.progress["session_fail_streak"] >= 5 and not self._burnout_nag_shown:
            self._burnout_nag_shown = True
            if CTkMessagebox:
                self._msg(
                    title="Забота о тебе",
                    message="Котик заметил много попыток подряд. Сделай паузу, вода, растяжка лапок — и ты вернёшься сильнее.",
                    option_1="Спасибо, котик",
                )

    def _on_success(self, score: int) -> None:
        self.progress["session_fail_streak"] = 0
        self.progress["current_streak"] = int(self.progress.get("current_streak", 0)) + 1
        completed = set(self.progress.get("completed_levels", []))
        was_new = self.current_level not in completed
        completed.add(self.current_level)
        self.progress["completed_levels"] = sorted(completed)
        self.progress["kitten_points"] = int(self.progress.get("kitten_points", 0)) + 10
        if was_new:
            album = list(self.progress.get("photo_album", []))
            if self.current_level not in album:
                album.append(self.current_level)
            self.progress["photo_album"] = sorted(album)
        if self.current_level < len(LEVELS):
            unlocked = set(self.progress.get("unlocked_levels", [1]))
            unlocked.add(self.current_level + 1)
            self.progress["unlocked_levels"] = sorted(unlocked)

        finalize_chapter_and_project(self.progress, total_levels=len(LEVELS))
        new_ach = update_achievements(self.progress)
        save_progress(self.progress)
        self._refresh_sidebar()
        self._refresh_progress_labels()
        level = LEVELS[self.current_level - 1]
        rules_ok = ", ".join(r["label"] for r in level["rules"])
        self.status_label.configure(
            text=f"Ура! Уровень пройден 💖 Оценка: {score}% · Запомни на будущее: {rules_ok}"
        )
        self._play_meow()
        self._show_success_modal(new_ach, was_new)

    def _show_success_modal(self, new_achievements: list[str], was_new: bool) -> None:
        message = "Мяу-эффект! Ты справилась блестяще 🐾"
        if new_achievements:
            message += "\n\nНовые достижения:\n- " + "\n- ".join(new_achievements[:3])
        if was_new and self.current_level < len(LEVELS):
            message += f"\n\nОткрыт уровень {self.current_level + 1}!"

        meme_path = random_existing_meme()
        if CTkMessagebox:
            kwargs: dict = {"title": "Мяу-эффект!", "message": message, "option_1": "Мурр!"}
            if meme_path:
                kwargs["icon"] = meme_path
            try:
                self._msg(**kwargs)
            except Exception:
                kwargs.pop("icon", None)
                try:
                    self._msg(**kwargs)
                except Exception:
                    self.status_label.configure(text=message)
        else:
            self.status_label.configure(text=message)

    def _show_life_reset_modal(self) -> None:
        text, button = random.choice(
            [
                ("налей своему котику чай с молоком", "Налила"),
                ("Сделай своему котику покушать ^_^", "Сделала"),
            ]
        )
        if CTkMessagebox:
            self._msg(title="Котик устал", message=text, option_1=button)
        else:
            self.status_label.configure(text=f"{text} [{button}]")
        if button == "Налила":
            self.progress["life_resets_tea"] = int(self.progress.get("life_resets_tea", 0)) + 1
        else:
            self.progress["life_resets_food"] = int(self.progress.get("life_resets_food", 0)) + 1
        update_achievements(self.progress)
        reset_lives(self.progress)
        save_progress(self.progress)
        self._refresh_progress_labels()

    def _refresh_code_highlight_theme(self) -> None:
        """Contrast-friendly green/red for light and dark themes."""
        mode = ctk.get_appearance_mode()
        if mode == "Light":
            good, bad = "#2E7D52", "#D81B60"
        else:
            good, bad = "#69F0AE", "#FF80AB"
        self.code_box.tag_config("good", foreground=good)
        self.code_box.tag_config("bad", foreground=bad)

    def _clear_highlight_tags(self) -> None:
        for tag in ("good", "bad"):
            self.code_box.tag_remove(tag, "1.0", "end")
        self._refresh_code_highlight_theme()

    def _apply_highlights(self, good_spans: list[dict], bad_spans: list[dict]) -> None:
        self._clear_highlight_tags()
        for span in good_spans:
            start = f"{span['line']}.{span['start']}"
            end = f"{span['line']}.{span['end']}"
            self.code_box.tag_add("good", start, end)
        for span in bad_spans:
            start = f"{span['line']}.{span['start']}"
            end = f"{span['line']}.{max(span['start'] + 1, span['end'])}"
            self.code_box.tag_add("bad", start, end)

    def _update_checklist(self, result: dict | None, _level_id: int) -> None:
        if result is None:
            self.checklist_label.configure(
                text="🎮 Готова сдать квест? Нажми «Проверить 💕» — котик мгновенно заглянет в код (кнопки остаются на месте)."
            )
            return
        if result.get("compiler_unavailable"):
            self.checklist_label.configure(
                text="💔 Сейчас не получается вызвать компилятор C#.\n"
                "Если это exe без встроенного .NET — напиши разработчику; иначе поставь .NET 8 с сайта Microsoft — и снова можно играть."
            )
            return
        if result.get("ok"):
            self.checklist_label.configure(
                text="🏆 Уровень по коду чистый!\n✅ Ошибок компилятора нет — можно идти дальше по кампании."
            )
            return
        miss = [m for m in (result.get("missing_rules") or []) if m.get("id") not in ("compile", "sdk")]
        lines: list[str] = ["🐾 Что поправить (номера строк — как в редакторе слева):", ""]
        if len(miss) > 1:
            lines.append("  Условия квеста:")
            for m in miss[:12]:
                lines.append(f"    — {m.get('label', m.get('id', '?'))}")
            lines.append("")
        for err in (result.get("compile_errors") or [])[:10]:
            msg = err.get("message", "")
            ln = int(err.get("line") or 0)
            code = str(err.get("code") or "")
            if ln >= 1:
                tag = "задание" if code == "MEOW_RULE" else "ошибка"
                lines.append(f"  • строка {ln} ({tag}): {msg}")
            else:
                lines.append(f"  • {msg}")
        if len(lines) == 2:
            lines.append(f"  • {result.get('hint', 'См. сообщение выше.')}")
        self.checklist_label.configure(text="\n".join(lines))

    def _play_meow(self) -> None:
        if not self.progress.get("sound_enabled", True):
            return
        wav = resource_path("assets", "audio", "meow.wav")
        if wav.exists():
            try:
                import winsound

                winsound.PlaySound(str(wav.resolve()), winsound.SND_FILENAME | winsound.SND_ASYNC)
                return
            except Exception:
                pass
        if sys.platform == "win32":
            try:
                import winsound

                winsound.Beep(880, 140)
                return
            except Exception:
                pass
        self.bell()

    def _show_level_reference(self) -> None:
        level = LEVELS[self.current_level - 1]
        win = ctk.CTkToplevel(self)
        self._popup(win)
        win.title("Эталон — только подглядывай, если совсем застряла")
        win.geometry("720x520")
        ctk.CTkLabel(
            win,
            text="Это один из рабочих вариантов. Лучше сначала попробуй сама — эталон не исчезнет.",
            anchor="w",
        ).pack(anchor="w", padx=10, pady=8)
        ref = str(level.get("reference_code") or "").strip()
        if not ref:
            ref = "// Эталон для этого уровня ещё не добавлен.\n"
        self._pack_modal_code_editor(win, ref, read_only=True)

    def _open_path_map(self) -> None:
        win = ctk.CTkToplevel(self)
        self._popup(win)
        win.title("Карта пути")
        win.geometry("560x440")
        ctk.CTkLabel(win, text="Главы кампании (релизы B–F — в следующих обновлениях)", font=ctk.CTkFont(size=16, weight="bold")).pack(
            pady=10
        )
        done_a = "A" in self.progress.get("completed_chapters", []) or len(self.progress.get("completed_levels", [])) >= len(LEVELS)
        chapters = [
            ("A — Логово синтаксиса", "10 уровней, боссы, финальный проект", done_a),
            ("B — Коллекции", "List, Dictionary, foreach — скоро", False),
            ("C — Методы глубже", "Параметры, return — скоро", False),
            ("D — ООП", "class, поля — скоро", False),
            ("E — Исключения", "try/catch — скоро", False),
            ("F — LINQ / файлы", "опционально — скоро", False),
        ]
        for title, sub, ok in chapters:
            mark = "✅" if ok else "⏳"
            ctk.CTkLabel(win, text=f"{mark} {title}\n   {sub}", anchor="w", justify="left").pack(anchor="w", padx=16, pady=4)
        ctk.CTkButton(win, text="Roadmap Junior Security Cat", command=self._open_roadmap).pack(pady=12)

    def _open_roadmap(self) -> None:
        win = ctk.CTkToplevel(self)
        self._popup(win)
        win.title("Roadmap до Junior Security Cat")
        win.geometry("520x360")
        for title, body in ROADMAP_PHASES:
            ctk.CTkLabel(win, text=f"{title}\n{body}", anchor="w", justify="left", wraplength=480).pack(anchor="w", padx=12, pady=6)

    def _open_weekly_digest(self) -> None:
        win = ctk.CTkToplevel(self)
        self._popup(win)
        win.title("ИБ-дайджест недели")
        win.geometry("480x320")
        box = ctk.CTkTextbox(win, wrap="word")
        box.pack(fill="both", expand=True, padx=10, pady=10)
        box.insert("1.0", weekly_digest_text(self.progress))
        box.configure(state="disabled")

    def _open_final_project_hub(self) -> None:
        if not self.progress.get("final_project_unlocked"):
            return
        if self.progress.get("final_project_done"):
            if CTkMessagebox:
                self._msg(title="Проект", message="Ты уже сдала финальный проект! Котик гордится тобой 🎓", option_1="Мурр!")
            return
        win = ctk.CTkToplevel(self)
        self._popup(win)
        win.title("Финальный проект — выбери трек")
        win.geometry("560x400")
        ctk.CTkLabel(win, text="Один трек на выбор — мини-продукт в кото-стиле 🐾", font=ctk.CTkFont(size=15, weight="bold")).pack(
            pady=10
        )
        for track in FINAL_PROJECT_TRACKS:
            ctk.CTkButton(
                win,
                text=str(track["title"]),
                command=lambda t=track: self._open_final_project_editor(win, t),
            ).pack(fill="x", padx=14, pady=6)

    def _open_final_project_editor(self, parent: ctk.CTkToplevel, track: dict) -> None:
        parent.destroy()
        win = ctk.CTkToplevel(self)
        self._popup(win)
        win.title(str(track["title"]))
        win.geometry("800x620")
        ctk.CTkLabel(win, text=str(track["mission"]), wraplength=740, justify="left").pack(anchor="w", padx=10, pady=8)
        editor = self._pack_modal_code_editor(win, str(track["starter_code"]))
        status = ctk.CTkLabel(win, text="Котоинтеллект оценивает проект 📋")
        status.pack(anchor="w", padx=10, pady=(0, 8))
        rules = track["rules"]

        def _check() -> None:
            result = validate_rules(rules, editor.get("1.0", "end-1c"), 1, {})
            if result["ok"]:
                self.progress["final_project_done"] = True
                self.progress["final_project_track"] = track["id"]
                self.progress["kitten_points"] = int(self.progress.get("kitten_points", 0)) + 50
                new_ach = update_achievements(self.progress)
                save_progress(self.progress)
                self._refresh_progress_labels()
                extra = ""
                if new_ach:
                    extra = "\n" + "\n".join(new_ach)
                status.configure(text=f"Проект принят! Диплом котика 🎓{extra}")
                self._play_meow()
            else:
                status.configure(text=f"Ещё не готово. {validation_status_message(result)}")

        ctk.CTkButton(win, text="Сдать проект", command=_check, fg_color=CORAL_ACCENT, hover_color="#FF7043").pack(
            padx=10, pady=8, anchor="e"
        )

    def _open_care_hub(self) -> None:
        win = ctk.CTkToplevel(self)
        self._popup(win)
        win.title("Забота и вовлечение")
        win.geometry("540x480")
        tabs = ctk.CTkTabview(win)
        tabs.pack(fill="both", expand=True, padx=10, pady=10)
        t1 = tabs.add("Забота")
        t2 = tabs.add("Магазин")
        t3 = tabs.add("Джун-день")

        sw_soft = ctk.CTkSwitch(t1, text="Мягкий режим (без потери жизней)", command=lambda: self._persist_soft(sw_soft))
        if self.progress.get("soft_mode_no_lives"):
            sw_soft.select()
        sw_soft.pack(anchor="w", padx=8, pady=6)

        sw_anx = ctk.CTkSwitch(t1, text="Тревожный режим помощи (мягкие фразы)", command=lambda: self._persist_anxiety(sw_anx))
        if self.progress.get("anxiety_care_mode"):
            sw_anx.select()
        sw_anx.pack(anchor="w", padx=8, pady=6)

        ctk.CTkButton(t1, text="Письмо от котика-наставника", command=self._open_mentor_letter).pack(anchor="w", padx=8, pady=4)
        ctk.CTkButton(t1, text="5-минутный уютный квест", command=self._open_five_min).pack(anchor="w", padx=8, pady=4)
        ctk.CTkButton(t1, text="Фотоальбом побед", command=self._open_photo_album).pack(anchor="w", padx=8, pady=4)

        ctk.CTkLabel(
            t2,
            text="Косметика за очки лапок — украшения видны на питомце вверху экрана.",
            wraplength=480,
            justify="left",
        ).pack(anchor="w", padx=8, pady=(8, 4))
        owned = set(self.progress.get("purchased_cosmetics", []))
        pts = int(self.progress.get("kitten_points", 0))
        ctk.CTkLabel(t2, text=f"Сейчас у тебя: {pts} очков 🐾", anchor="w").pack(anchor="w", padx=8, pady=(0, 8))
        for c in PET_COSMETICS:
            cid = c["id"]
            if cid in owned:
                ctk.CTkLabel(
                    t2,
                    text=f"{c['emoji']} {c['title']} — уже твоя",
                    anchor="w",
                    text_color=("gray35", "gray60"),
                ).pack(anchor="w", padx=8, pady=3)
            else:
                ctk.CTkButton(
                    t2,
                    text=f"Купить {c['emoji']} «{c['title']}» — {c['cost']} очков",
                    command=lambda i=cid, price=int(c["cost"]): self._buy_cosmetic(win, i, price),
                ).pack(anchor="w", padx=8, pady=3)

        for i, step in enumerate(JUNIOR_DAY_STEPS, start=1):
            ctk.CTkLabel(t3, text=step, anchor="w", justify="left").pack(anchor="w", padx=10, pady=2)
        ctk.CTkButton(t3, text="Закрыть рабочий день джуна (+15 очков, один раз)", command=lambda: self._complete_junior_day(win)).pack(
            pady=12
        )

    def _persist_soft(self, sw: ctk.CTkSwitch) -> None:
        self.progress["soft_mode_no_lives"] = bool(sw.get())
        save_progress(self.progress)

    def _persist_anxiety(self, sw: ctk.CTkSwitch) -> None:
        self.progress["anxiety_care_mode"] = bool(sw.get())
        save_progress(self.progress)

    def _buy_cosmetic(self, win: ctk.CTkToplevel, cosmetic_id: str, cost: int) -> None:
        owned = set(self.progress.get("purchased_cosmetics", []))
        if cosmetic_id in owned:
            return
        pts = int(self.progress.get("kitten_points", 0))
        if pts < cost:
            if CTkMessagebox:
                self._msg(title="Магазин", message="Мало очков лапок — продолжай учиться!", option_1="Ок")
            return
        self.progress["kitten_points"] = pts - cost
        owned.add(cosmetic_id)
        self.progress["purchased_cosmetics"] = sorted(owned)
        save_progress(self.progress)
        self._refresh_progress_labels()
        if CTkMessagebox:
            self._msg(title="Магазин", message="Косметика куплена! Питомец сияет.", option_1="Ура!")

    def _complete_junior_day(self, win: ctk.CTkToplevel) -> None:
        if self.progress.get("junior_day_done"):
            if CTkMessagebox:
                self._msg(title="Джун-день", message="Ты уже прошла этот квест в этой кампании 💼", option_1="Ок")
            return
        self.progress["junior_day_done"] = True
        self.progress["kitten_points"] = int(self.progress.get("kitten_points", 0)) + 15
        save_progress(self.progress)
        self._refresh_progress_labels()
        if CTkMessagebox:
            self._msg(title="Джун-день", message="Мини-день джуна засчитан: баг → фикс → тест → ревью 💼", option_1="Мурр!")

    def _open_mentor_letter(self) -> None:
        letter = random.choice(MENTOR_LETTERS)
        self.progress["mentor_letters_seen"] = int(self.progress.get("mentor_letters_seen", 0)) + 1
        save_progress(self.progress)
        if CTkMessagebox:
            self._msg(title="Письмо от Миттенс", message=letter, option_1="Спасибо, котик")

    def _open_five_min(self) -> None:
        q = random.choice(FIVE_MIN_QUESTS)
        win = ctk.CTkToplevel(self)
        self._popup(win)
        win.title(q["title"])
        win.geometry("480x260")
        ctk.CTkLabel(win, text=q["body"], wraplength=440, justify="left").pack(padx=12, pady=16)

    def _open_photo_album(self) -> None:
        win = ctk.CTkToplevel(self)
        self._popup(win)
        win.title("Фотоальбом побед")
        win.geometry("420x360")
        photos = self.progress.get("photo_album", [])
        if not photos:
            ctk.CTkLabel(win, text="Пока пусто — пройди уровни, и снимки появятся! 📷").pack(pady=20)
            return
        scroll = ctk.CTkScrollableFrame(win)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        for lid in photos:
            ctk.CTkLabel(
                scroll,
                text=f"Уровень {lid} — {LEVELS[lid - 1]['title']} 🏅",
                anchor="w",
            ).pack(fill="x", pady=3)

    def _cancel_love_reminder(self) -> None:
        if self._love_after_id is not None:
            try:
                self.after_cancel(self._love_after_id)
            except Exception:
                pass
            self._love_after_id = None

    def _schedule_love_reminder(self) -> None:
        self._cancel_love_reminder()
        if not self.progress.get("love_reminder_enabled", True):
            return
        self._love_after_id = self.after(30 * 60 * 1000, self._show_love_reminder)

    def _show_love_reminder(self) -> None:
        self._love_after_id = None
        if not self.progress.get("love_reminder_enabled", True):
            return
        toast = ctk.CTkToplevel(self)
        self._popup(toast)
        toast.title("💖")
        toast.geometry("280x120")
        toast.attributes("-topmost", True)
        ctk.CTkLabel(toast, text="Я тебя люблю! 💕", font=ctk.CTkFont(size=20, weight="bold")).pack(expand=True, pady=18)
        ctk.CTkButton(toast, text="Мурр", command=toast.destroy, width=90).pack(pady=(0, 10))
        toast.after(7000, toast.destroy)
        self._schedule_love_reminder()
