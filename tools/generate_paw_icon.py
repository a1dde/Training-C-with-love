"""Генерация assets/paw_icon.png и assets/paw_icon.ico (лапка, цвета темы Meow)."""

from __future__ import annotations

import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:
    print("Нужен Pillow: pip install Pillow", file=sys.stderr)
    sys.exit(1)


def _paw_image(size: int) -> Image.Image:
    """Простая силуэтная лапка: подушечка + 4 пальца (эллипсы)."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # акценты как в meow_pink.json
    fill = (233, 30, 140, 255)
    outline = (194, 24, 91, 255)
    s = size

    # большая подушечка (внизу по центру)
    cx, cy = s // 2, int(s * 0.58)
    rw, rh = int(s * 0.22), int(s * 0.18)
    draw.ellipse([cx - rw, cy - rh, cx + rw, cy + rh], fill=fill, outline=outline, width=max(1, s // 64))

    # четыре «пальца» сверху
    toe_r = int(s * 0.09)
    positions = [
        (cx - int(s * 0.28), int(s * 0.28)),
        (cx - int(s * 0.10), int(s * 0.18)),
        (cx + int(s * 0.10), int(s * 0.18)),
        (cx + int(s * 0.28), int(s * 0.28)),
    ]
    for tx, ty in positions:
        draw.ellipse([tx - toe_r, ty - toe_r, tx + toe_r, ty + toe_r], fill=fill, outline=outline, width=max(1, s // 64))

    return img


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    assets = root / "assets"
    assets.mkdir(parents=True, exist_ok=True)

    png_path = assets / "paw_icon.png"
    ico_path = assets / "paw_icon.ico"

    img256 = _paw_image(256)
    img256.save(png_path, "PNG")

    # ICO: несколько размеров — для заголовка окна и exe
    sizes = [16, 24, 32, 48, 64, 128, 256]
    imgs = [_paw_image(sz) for sz in sizes]
    imgs[-1].save(
        ico_path,
        format="ICO",
        sizes=[(s, s) for s in sizes],
        append_images=imgs[:-1],
    )

    print(f"OK: {png_path}")
    print(f"OK: {ico_path}")


if __name__ == "__main__":
    main()
