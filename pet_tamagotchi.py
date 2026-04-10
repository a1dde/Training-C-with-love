"""Мини-тамагочи: котик на Canvas растёт со стадией; косметика — векторные «наклейки», не эмодзи."""

from __future__ import annotations

import math
import tkinter as tk
from collections.abc import Sequence
from typing import Any

import customtkinter as ctk

from pet_cosmetics import PET_COSMETICS

# Якорь: (head|body, rel_x, rel_y) в долях head_r / body_rx/ry
_COSMETIC_LAYOUT: dict[str, tuple[str, float, float]] = {
    "pink_bow": ("head", -0.50, -0.62),
    "heart_glasses": ("head", 0.0, -0.08),
    "sleepy_cap": ("head", 0.0, -0.95),
    "star_collar": ("head", 0.0, 0.78),
    "rainbow_paw": ("body", 1.08, -0.05),
    "fish_pin": ("body", 0.18, -0.28),
}


class PetTamagotchi(tk.Frame):
    """
    Обычный tk.Frame + Canvas — не CTkFrame: у CTkFrame уже есть свой _canvas для скругления,
    вложенный tk.Canvas ломает инициализацию (int/str в Tk).
    """

    def __init__(self, master: Any, width: int = 200, height: int = 220, **kwargs: Any) -> None:
        kwargs.pop("fg_color", None)
        bg = kwargs.pop("bg", None)
        if bg is None:
            bg = self._default_frame_bg()
        super().__init__(
            master,
            width=int(width),
            height=int(height),
            highlightthickness=0,
            borderwidth=0,
            bg=bg,
        )
        self._pix_w = int(width)
        self._pix_h = int(height)
        self._stage = 0
        self._owned: set[str] = set()
        self._mood: str | None = None  # happy | oops | sleepy
        self._canvas = tk.Canvas(
            self,
            width=self._pix_w,
            height=self._pix_h,
            highlightthickness=0,
            borderwidth=0,
            bg=bg,
        )
        self._canvas.pack(fill="both", expand=True)
        self.bind("<Configure>", self._on_resize)

    @staticmethod
    def _default_frame_bg() -> str:
        return "#2A252E" if ctk.get_appearance_mode() == "Dark" else "#FFF5FA"

    def _on_resize(self, _event: object) -> None:
        w, h = int(self.winfo_width()), int(self.winfo_height())
        if w < 48 or h < 48:
            return
        self._pix_w = max(120, w)
        self._pix_h = max(140, h)
        bg = self._palette()[0]
        try:
            self.configure(bg=bg)
        except tk.TclError:
            pass
        self._canvas.configure(width=self._pix_w, height=self._pix_h, bg=bg)
        self._redraw()

    def refresh_geometry(self) -> None:
        self.update_idletasks()
        w, h = int(self.winfo_width()), int(self.winfo_height())
        if w < 48 or h < 48:
            return
        self._pix_w = max(120, w)
        self._pix_h = max(140, h)
        bg = self._palette()[0]
        try:
            self.configure(bg=bg)
        except tk.TclError:
            pass
        self._canvas.configure(width=self._pix_w, height=self._pix_h, bg=bg)
        self._redraw()

    def set_state(self, stage: int, purchased_ids: Sequence[str] | None) -> None:
        self._stage = max(0, min(4, int(stage)))
        self._owned = set(purchased_ids or [])
        self._redraw()

    def set_mood(self, mood: str | None) -> None:
        """Краткая эмоция: happy / oops / sleepy / None — обычное лицо."""
        if mood not in (None, "happy", "oops", "sleepy"):
            mood = None
        self._mood = mood
        self._redraw()

    def _palette(self) -> tuple[str, str, str, str]:
        mode = ctk.get_appearance_mode()
        if mode == "Light":
            return ("#FFF5FA", "#F8BBD9", "#4A1942", "#E91E8C")
        return ("#2A252E", "#8E7A8A", "#4A3D45", "#D8A4B8")

    def _star_polygon(self, cx: float, cy: float, r: float, n: int = 5) -> list[float]:
        pts: list[float] = []
        for i in range(n * 2):
            ang = math.pi / 2 + i * math.pi / n
            rad = r if i % 2 == 0 else r * 0.45
            pts.append(cx + rad * math.cos(ang))
            pts.append(cy - rad * math.sin(ang))
        return pts

    def _draw_cosmetic(
        self,
        c: tk.Canvas,
        cid: str,
        hx: float,
        hy: float,
        head_r: float,
        cx: float,
        cy: float,
        body_rx: float,
        body_ry: float,
        s: float,
        outline: str,
        eye_off: float,
        ink: str,
    ) -> None:
        dark = ctk.get_appearance_mode() == "Dark"
        rose = "#F48FB1" if dark else "#E91E8C"
        rose_dark = "#AD5270" if dark else "#AD1457"
        gold = "#FFD54F"
        mint = "#80CBC4"
        sky = "#81D4FA"
        layout = _COSMETIC_LAYOUT.get(cid)
        if not layout:
            return
        kind, rx, ry = layout
        if kind == "head":
            ax, ay = hx + rx * head_r, hy + ry * head_r
        else:
            ax, ay = cx + rx * body_rx, cy + ry * body_ry
        u = max(4.0, 5.5 * s)

        if cid == "pink_bow":
            # Бант из двух лепестков + узел
            w, h = 10 * u / 5.5, 8 * u / 5.5
            c.create_polygon(
                ax - w,
                ay,
                ax - w * 0.2,
                ay - h * 0.9,
                ax,
                ay - h * 0.35,
                ax - w * 0.35,
                ay + h * 0.15,
                fill=rose,
                outline=rose_dark,
                width=1,
            )
            c.create_polygon(
                ax + w,
                ay,
                ax + w * 0.2,
                ay - h * 0.9,
                ax,
                ay - h * 0.35,
                ax + w * 0.35,
                ay + h * 0.15,
                fill=rose,
                outline=rose_dark,
                width=1,
            )
            c.create_oval(ax - u * 0.35, ay - u * 0.3, ax + u * 0.35, ay + u * 0.35, fill=rose_dark, outline=rose_dark)

        elif cid == "heart_glasses":
            # Две «линзы» и перемычка
            o = eye_off * 0.95
            r = 4.8 * s
            for sign in (-1, 1):
                ox = hx + sign * o
                oy = hy - 0.1 * head_r
                c.create_oval(ox - r, oy - r * 0.85, ox + r, oy + r * 0.95, outline=rose_dark, width=2, fill="")
                c.create_line(ox - r * 0.3, oy, ox + r * 0.3, oy + r * 0.5, fill=rose, width=2)
            c.create_line(hx - o + r, hy - 0.1 * head_r, hx + o - r, hy - 0.1 * head_r, fill=rose_dark, width=2)

        elif cid == "sleepy_cap":
            # Полупокрышка над макушкой
            w = head_r * 0.95
            y0 = ay
            c.create_arc(
                ax - w,
                y0 - u * 1.1,
                ax + w,
                y0 + u * 0.5,
                start=0,
                extent=180,
                style="pieslice",
                fill=rose,
                outline=rose_dark,
                width=2,
            )
            c.create_oval(ax - u * 0.25, y0 - u * 0.1, ax + u * 0.25, y0 + u * 0.35, fill=gold, outline=rose_dark)

        elif cid == "star_collar":
            pts = self._star_polygon(ax, ay, u * 0.9, 5)
            c.create_polygon(*pts, fill=gold, outline=rose_dark, width=1)
            c.create_oval(ax - u * 0.15, ay - u * 0.15, ax + u * 0.15, ay + u * 0.15, fill=rose, outline="")

        elif cid == "rainbow_paw":
            for i, col in enumerate(("#FF8A80", "#FFAB91", "#81D4FA", mint)):
                off = (i - 1.5) * u * 0.35
                c.create_arc(
                    ax - u * 1.2 + off,
                    ay - u * 0.5,
                    ax + u * 0.4 + off,
                    ay + u * 1.0,
                    start=200,
                    extent=100,
                    style="arc",
                    outline=col,
                    width=3,
                )

        elif cid == "fish_pin":
            body_w, body_h = u * 1.1, u * 0.55
            c.create_oval(ax - body_w, ay - body_h, ax + body_w * 0.2, ay + body_h, fill=sky, outline=rose_dark, width=1)
            c.create_polygon(
                ax + body_w * 0.2,
                ay,
                ax + body_w * 1.0,
                ay - body_h * 0.4,
                ax + body_w * 1.0,
                ay + body_h * 0.4,
                fill=sky,
                outline=rose_dark,
                width=1,
            )
            c.create_oval(ax - body_w * 0.5, ay - body_h * 0.25, ax - body_w * 0.15, ay + body_h * 0.25, fill=ink, outline="")

    def _redraw(self) -> None:
        c = self._canvas
        c.delete("all")
        bg, outline, ink, blush = self._palette()
        c.configure(bg=bg)
        try:
            self.configure(bg=bg)
        except tk.TclError:
            pass
        cx = self._pix_w / 2
        cy = self._pix_h / 2 + 8
        s = 0.72 + self._stage * 0.085

        body_rx = 52 * s
        body_ry = 40 * s
        shadow = "#1E1A22" if ctk.get_appearance_mode() == "Dark" else "#F0D8E4"
        c.create_oval(cx - body_rx - 4, cy - body_ry + 28, cx + body_rx + 4, cy + body_ry + 36, fill=shadow, outline="")

        c.create_oval(cx - body_rx, cy - body_ry, cx + body_rx, cy + body_ry, fill=blush, outline=outline, width=2)

        head_r = 44 * s
        hx, hy = cx, cy - body_ry - head_r * 0.55
        c.create_oval(hx - head_r, hy - head_r, hx + head_r, hy + head_r, fill=blush, outline=outline, width=2)

        c.create_polygon(
            hx - head_r * 0.85,
            hy - head_r * 0.35,
            hx - head_r * 0.45,
            hy - head_r * 1.05,
            hx - head_r * 0.1,
            hy - head_r * 0.25,
            fill=blush,
            outline=outline,
            width=2,
        )
        c.create_polygon(
            hx + head_r * 0.85,
            hy - head_r * 0.35,
            hx + head_r * 0.45,
            hy - head_r * 1.05,
            hx + head_r * 0.1,
            hy - head_r * 0.25,
            fill=blush,
            outline=outline,
            width=2,
        )

        eye_off = 16 * s
        mood = self._mood
        base_eye = 5 * s + (self._stage * 0.4)
        if mood == "happy":
            eye_r = base_eye * 1.12
        elif mood == "oops":
            eye_r = base_eye * 0.72
        else:
            eye_r = base_eye

        if mood == "sleepy":
            for sign in (-1, 1):
                ox = hx + sign * eye_off
                c.create_line(ox - eye_r * 1.1, hy, ox + eye_r * 1.1, hy, fill=ink, width=max(2, int(2 * s)))
        else:
            c.create_oval(hx - eye_off - eye_r, hy - eye_r * 0.3, hx - eye_off + eye_r, hy + eye_r * 1.2, fill=ink, outline="")
            c.create_oval(hx + eye_off - eye_r, hy - eye_r * 0.3, hx + eye_off + eye_r, hy + eye_r * 1.2, fill=ink, outline="")
            c.create_oval(hx - eye_off - eye_r * 0.3, hy - eye_r * 0.5, hx - eye_off + eye_r * 0.2, hy, fill="#FFFFFF", outline="")
            c.create_oval(hx + eye_off - eye_r * 0.3, hy - eye_r * 0.5, hx + eye_off + eye_r * 0.2, hy, fill="#FFFFFF", outline="")

        nose_y = hy + 10 * s
        c.create_polygon(hx, nose_y - 4 * s, hx - 5 * s, nose_y + 4 * s, hx + 5 * s, nose_y + 4 * s, fill="#E57373", outline=outline)

        for dy in (-4, 0, 4):
            c.create_line(hx - head_r - 4, hy + dy, hx - head_r * 0.45, hy + dy * 0.6, fill=outline, width=1)
            c.create_line(hx + head_r + 4, hy + dy, hx + head_r * 0.45, hy + dy * 0.6, fill=outline, width=1)

        paw_y = cy + body_ry * 0.55
        for sign in (-1, 1):
            px = cx + sign * body_rx * 0.65
            c.create_oval(px - 12 * s, paw_y - 8 * s, px + 12 * s, paw_y + 10 * s, fill=blush, outline=outline, width=2)

        c.create_arc(
            cx + body_rx - 4,
            cy - body_ry * 0.2,
            cx + body_rx + 48 * s,
            cy + body_ry * 0.9,
            start=200,
            extent=120,
            style="arc",
            outline=outline,
            width=3,
        )

        for item in PET_COSMETICS:
            cid = item["id"]
            if cid not in self._owned:
                continue
            self._draw_cosmetic(c, cid, hx, hy, head_r, cx, cy, body_rx, body_ry, s, outline, eye_off, ink)
