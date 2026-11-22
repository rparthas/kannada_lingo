#!/usr/bin/env python3
"""Generate short placeholder WAV clips for curriculum dev (replace with human recordings)."""
from __future__ import annotations

import json
import math
import struct
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CURRICULUM = ROOT / "content" / "curriculum" / "beginner-path.json"
OUT = ROOT / "content" / "audio"


def learning_item_ids() -> list[str]:
    if not CURRICULUM.is_file():
        raise SystemExit(f"Missing curriculum: {CURRICULUM}")
    bundle = json.loads(CURRICULUM.read_text(encoding="utf-8"))
    return [item["id"] for item in bundle.get("learning_items", [])]


def write_tone(path: Path, *, freq: float, duration_s: float, sample_rate: int = 22050) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    n_frames = int(sample_rate * duration_s)
    with wave.open(str(path), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        frames = bytearray()
        for i in range(n_frames):
            t = i / sample_rate
            envelope = min(1.0, 8.0 * t) * max(0.0, 1.0 - 4.0 * max(0.0, t - duration_s * 0.7))
            sample = int(32767 * 0.25 * envelope * math.sin(2 * math.pi * freq * t))
            frames.extend(struct.pack("<h", sample))
        wf.writeframes(frames)
    return int(duration_s * 1000)


def main() -> None:
    durations: list[tuple[str, str, int]] = []
    for item_id in learning_item_ids():
        normal = OUT / f"{item_id}-normal.wav"
        slow = OUT / f"{item_id}-slow.wav"
        d1 = write_tone(normal, freq=520.0, duration_s=0.45)
        d2 = write_tone(slow, freq=440.0, duration_s=0.65)
        durations.append((item_id, "normal", d1))
        durations.append((item_id, "slow", d2))
    print(f"Wrote {len(durations)} files under {OUT}")
    for item_id, speed, ms in durations:
        print(f"  {item_id}-{speed}.wav ({ms} ms)")


if __name__ == "__main__":
    main()