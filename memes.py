from __future__ import annotations

import random
from pathlib import Path

from resources import bundle_dir

BASE_DIR = bundle_dir()
MEME_PATHS = [
    BASE_DIR / "memes" / "cat1.jpg",
    BASE_DIR / "memes" / "cat2.jpg",
    BASE_DIR / "memes" / "cat3.jpg",
    BASE_DIR / "memes" / "cat4.jpg",
    BASE_DIR / "memes" / "cat5.jpg",
    BASE_DIR / "memes" / "cat6.jpg",
]


def random_existing_meme() -> str | None:
    existing = [p for p in MEME_PATHS if p.exists()]
    if not existing:
        return None
    return str(random.choice(existing))
