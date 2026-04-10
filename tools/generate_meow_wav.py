"""Генерирует короткий meow.wav (моно 44.1kHz) для звука успеха — без внешних файлов."""
from __future__ import annotations

import math
import struct
import wave
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    out = root / "assets" / "audio" / "meow.wav"
    out.parent.mkdir(parents=True, exist_ok=True)

    fr = 44100
    duration = 0.28
    n = int(fr * duration)

    with wave.open(str(out), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(fr)
        for i in range(n):
            t = i / fr
            # «Мяу»: плавное снижение частоты + затухание
            f = 1100.0 - 650.0 * (t / duration)
            env = (1.0 - t / duration) ** 1.4
            sample = int(32767 * 0.22 * env * math.sin(2 * math.pi * f * t))
            sample = max(-32767, min(32767, sample))
            w.writeframes(struct.pack("<h", sample))

    print(f"Wrote {out} ({n} samples)")


if __name__ == "__main__":
    main()
