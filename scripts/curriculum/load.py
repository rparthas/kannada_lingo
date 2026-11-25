"""Load curriculum data from JSON spec files."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent.parent
SPECS = ROOT / "content" / "curriculum" / "specs"
COURSE_FILE = SPECS / "course.json"
UNITS_DIR = SPECS / "units"


def load_curriculum_data() -> dict[str, Any]:
    course = json.loads(COURSE_FILE.read_text(encoding="utf-8"))
    units_meta: list[dict[str, Any]] = []
    lessons_meta: list[dict[str, Any]] = []
    phrases_by_id: dict[str, dict[str, Any]] = {}
    exercises_hand: list[dict[str, Any]] = []
    skip_generated: list[str] = []

    levels = course.get("levels") or []
    level_ordinals = {level["id"]: level["ordinal"] for level in levels}

    def unit_sort_key(path: Path) -> tuple[int, int]:
        unit = json.loads(path.read_text(encoding="utf-8"))
        level_ord = level_ordinals.get(unit["level_id"], 99)
        return (level_ord, unit["ordinal"])

    unit_files = sorted(UNITS_DIR.glob("*.json"), key=unit_sort_key)
    for path in unit_files:
        unit = json.loads(path.read_text(encoding="utf-8"))
        units_meta.append(
            {
                "id": unit["id"],
                "level_id": unit["level_id"],
                "ordinal": unit["ordinal"],
                "title": unit["title"],
                "description": unit["description"],
            }
        )
        for phrase in unit.get("phrases") or []:
            pid = phrase["id"]
            if pid in phrases_by_id:
                raise ValueError(f"Duplicate phrase id {pid} in {path.name}")
            phrases_by_id[pid] = phrase

        for lesson in unit.get("lessons") or []:
            for pid in lesson["phrase_ids"]:
                if pid not in phrases_by_id:
                    raise ValueError(f"Lesson {lesson['id']} references unknown phrase {pid} in {path.name}")
            entry: dict[str, Any] = {
                "id": lesson["id"],
                "unit_id": unit["id"],
                "ordinal": lesson["ordinal"],
                "title": lesson["title"],
                "description": lesson["description"],
                "estimated_minutes": lesson["estimated_minutes"],
                "phrase_ids": lesson["phrase_ids"],
            }
            if lesson.get("exercise_mode") == "hand":
                skip_generated.append(lesson["id"])
                entry["hand_exercises"] = lesson.get("exercises") or []
            else:
                generated: dict[str, Any] = {}
                if lesson.get("convo"):
                    generated["convo"] = lesson["convo"]
                if lesson.get("fill"):
                    generated["fill"] = lesson["fill"]
                if lesson.get("tiles"):
                    generated["tiles"] = lesson["tiles"]
                if lesson.get("en_kn_index") is not None:
                    generated["en_kn_index"] = lesson["en_kn_index"]
                if lesson.get("kn_en"):
                    generated["kn_en"] = lesson["kn_en"]
                if generated:
                    entry["generated"] = generated
            lessons_meta.append(entry)

    return {
        "content_version": course["content_version"],
        "course": course["course"],
        "levels": course["levels"],
        "units": units_meta,
        "lessons_meta": lessons_meta,
        "phrases_by_id": phrases_by_id,
        "exercises_hand": exercises_hand,
        "skip_generated_lessons": skip_generated,
        "extra_audio_assets": course.get("extra_audio_assets") or [],
    }