#!/usr/bin/env python3
"""Generate phrase WAV clips: macOS Kannada TTS (Soumya) when available, else short tones."""
from __future__ import annotations

import json
import math
import shutil
import struct
import subprocess
import sys
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CURRICULUM = ROOT / "content" / "curriculum" / "beginner-path.json"
OUT = ROOT / "content" / "audio"
VOICE = "Soumya"
NORMAL_RATE = 200
SLOW_RATE = 130


def load_items() -> list[dict]:
    if not CURRICULUM.is_file():
        raise SystemExit(f"Missing curriculum: {CURRICULUM}")
    bundle = json.loads(CURRICULUM.read_text(encoding="utf-8"))
    return bundle.get("learning_items", [])


def wav_duration_ms(path: Path) -> int:
    with wave.open(str(path), "rb") as wf:
        return int(1000 * wf.getnframes() / wf.getframerate())


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


def tts_available() -> bool:
    say = shutil.which("say")
    ffmpeg = shutil.which("ffmpeg")
    if not say or not ffmpeg:
        return False
    try:
        subprocess.run(
            [say, "-v", "?", VOICE],
            capture_output=True,
            check=False,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return True


def speak_to_wav(text: str, out_wav: Path, *, rate: int) -> int:
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    aiff = out_wav.with_suffix(".aiff")
    subprocess.run(
        [shutil.which("say"), "-v", VOICE, text, "-o", str(aiff), "-r", str(rate)],
        check=True,
    )
    subprocess.run(
        [
            shutil.which("ffmpeg"),
            "-y",
            "-i",
            str(aiff),
            "-ar",
            "22050",
            "-ac",
            "1",
            str(out_wav),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    aiff.unlink(missing_ok=True)
    return wav_duration_ms(out_wav)


def sync_durations_to_curriculum(durations: dict[tuple[str, str], int]) -> None:
    bundle = json.loads(CURRICULUM.read_text(encoding="utf-8"))
    for asset in bundle.get("audio_assets", []):
        key = (asset["learning_item_id"], asset.get("speaking_speed", "normal"))
        if key in durations:
            asset["duration_ms"] = durations[key]
    CURRICULUM.write_text(
        json.dumps(bundle, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    items = load_items()
    use_tts = tts_available()
    if not use_tts:
        print("WARN: say/ffmpeg/Kannada voice unavailable — falling back to tone placeholders.", file=sys.stderr)

    durations: dict[tuple[str, str], int] = {}
    for item in items:
        item_id = item["id"]
        text = (item.get("kannada_text") or "").strip()
        if not text:
            text = item.get("transliteration", item_id)

        for speed, rate in (("normal", NORMAL_RATE), ("slow", SLOW_RATE)):
            out = OUT / f"{item_id}-{speed}.wav"
            if use_tts:
                try:
                    ms = speak_to_wav(text, out, rate=rate)
                except subprocess.CalledProcessError as exc:
                    print(f"WARN: TTS failed for {item_id} ({speed}): {exc}", file=sys.stderr)
                    ms = write_tone(out, freq=520.0 if speed == "normal" else 440.0, duration_s=0.45 if speed == "normal" else 0.65)
            else:
                ms = write_tone(
                    out,
                    freq=520.0 if speed == "normal" else 440.0,
                    duration_s=0.45 if speed == "normal" else 0.65,
                )
            durations[(item_id, speed)] = ms
            print(f"  {item_id}-{speed}.wav ({ms} ms)")

    sync_durations_to_curriculum(durations)
    print(f"Wrote {len(durations)} files under {OUT} ({'TTS' if use_tts else 'tones'})")
    print(f"Updated durations in {CURRICULUM.name}")


if __name__ == "__main__":
    main()