"""Assemble beginner-path.json from structured curriculum data."""
from __future__ import annotations

from typing import Any


def audio_for(item_id: str) -> list[dict[str, Any]]:
    base = f"content/audio/{item_id}"
    return [
        {
            "id": f"audio-{item_id}-normal",
            "learning_item_id": item_id,
            "source": "tts",
            "speaking_speed": "normal",
            "review_status": "approved",
            "duration_ms": 450,
            "file_format": "wav",
            "relative_path": f"{base}-normal.wav",
        },
        {
            "id": f"audio-{item_id}-slow",
            "learning_item_id": item_id,
            "source": "tts",
            "speaking_speed": "slow",
            "review_status": "approved",
            "duration_ms": 650,
            "file_format": "wav",
            "relative_path": f"{base}-slow.wav",
        },
    ]


def lesson_exercises(
    lesson_id: str,
    slug: str,
    core: list[dict[str, Any]],
    convo: dict[str, Any],
    *,
    en_kn_index: int = 1,
    kn_en: dict[str, Any] | None = None,
    fill: dict[str, Any] | None = None,
    tiles: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    ex: list[dict[str, Any]] = []
    order = 1
    ex.append(
        {
            "id": f"ex-{slug}-flash",
            "lesson_id": lesson_id,
            "learning_item_id": core[0]["id"],
            "exercise_type": "vocabulary_flashcard",
            "sort_order": order,
            "prompt": {"instruction": "Learn this phrase."},
        }
    )
    order += 1
    mcq_item = core[1] if len(core) > 1 else core[0]
    distractors = [c["english_meaning"] for c in core[2:5]] if len(core) > 2 else []
    while len(distractors) < 3:
        distractors.append("Thank you")
    choices = [distractors[0], mcq_item["english_meaning"], distractors[1], distractors[2]]
    if choices[1] != mcq_item["english_meaning"]:
        ci = choices.index(mcq_item["english_meaning"])
        choices[1], choices[ci] = choices[ci], choices[1]
    ex.append(
        {
            "id": f"ex-{slug}-mcq",
            "lesson_id": lesson_id,
            "learning_item_id": mcq_item["id"],
            "exercise_type": "listen_identify",
            "sort_order": order,
            "prompt": {
                "instruction": "What does this phrase mean?",
                "choices": choices,
                "correct_index": 1,
            },
        }
    )
    order += 1
    en_item = core[min(en_kn_index, len(core) - 1)]
    ex.append(
        {
            "id": f"ex-{slug}-en-kn",
            "lesson_id": lesson_id,
            "learning_item_id": en_item["id"],
            "exercise_type": "english_to_kannada",
            "sort_order": order,
            "prompt": {"instruction": f"How do you say '{en_item['english_meaning']}' in Kannada?"},
        }
    )
    order += 1
    kn_item = core[min(2, len(core) - 1)]
    kn_prompt = kn_en or {
        "instruction": "Choose the best English meaning.",
        "choices": [core[0]["english_meaning"], kn_item["english_meaning"], core[-1]["english_meaning"], "Good night"],
        "correct_index": 1,
    }
    ex.append(
        {
            "id": f"ex-{slug}-kn-en",
            "lesson_id": lesson_id,
            "learning_item_id": kn_item["id"],
            "exercise_type": "kannada_to_english",
            "sort_order": order,
            "prompt": kn_prompt,
        }
    )
    order += 1
    if fill:
        ex.append(
            {
                "id": f"ex-{slug}-fill",
                "lesson_id": lesson_id,
                "learning_item_id": fill["item_id"],
                "exercise_type": "fill_blank",
                "sort_order": order,
                "prompt": {
                    "instruction": fill["instruction"],
                    "blanked_transliteration": fill["blank"],
                    "accepted": fill["accepted"],
                },
            }
        )
        order += 1
    elif tiles:
        ex.append(
            {
                "id": f"ex-{slug}-order",
                "lesson_id": lesson_id,
                "learning_item_id": tiles["item_id"],
                "exercise_type": "sentence_construction",
                "sort_order": order,
                "prompt": {
                    "instruction": tiles.get("instruction", "Arrange the words (transliteration tiles)."),
                    "tiles": tiles["tiles"],
                    "solution": tiles["solution"],
                },
            }
        )
        order += 1
    ex.append(
        {
            "id": f"ex-{slug}-repeat",
            "lesson_id": lesson_id,
            "learning_item_id": core[-1]["id"],
            "exercise_type": "listen_repeat",
            "sort_order": order,
            "prompt": {"instruction": "Listen and repeat aloud. Mark how you did."},
        }
    )
    order += 1
    ex.append(
        {
            "id": f"ex-{slug}-convo",
            "lesson_id": lesson_id,
            "exercise_type": "scripted_conversation",
            "sort_order": order,
            "prompt": convo,
        }
    )
    return ex


def assemble_bundle(data: dict[str, Any]) -> dict[str, Any]:
    phrases_by_id: dict[str, dict[str, Any]] = data["phrases_by_id"]
    lessons_meta = data["lessons_meta"]
    skip = set(data.get("skip_generated_lessons") or [])
    exercises_hand = data.get("exercises_hand") or []
    convo_specs: dict[str, Any] = data.get("convo_specs") or {}
    fill_specs: dict[str, Any] = data.get("fill_specs") or {}
    tile_specs: dict[str, Any] = data.get("tile_specs") or {}

    generated_exercises: list[dict[str, Any]] = []
    for lesson in lessons_meta:
        lid = lesson["id"]
        if lid in skip:
            continue
        core = [phrases_by_id[pid] for pid in lesson["phrase_ids"]]
        slug = lid.replace("lesson-", "")
        gen = lesson.get("generated") or {}
        generated_exercises.extend(
            lesson_exercises(
                lid,
                slug,
                core,
                gen.get("convo") or convo_specs[lid],
                en_kn_index=gen.get("en_kn_index", 1),
                kn_en=gen.get("kn_en"),
                fill=gen.get("fill") or fill_specs.get(lid),
                tiles=gen.get("tiles") or tile_specs.get(lid),
            )
        )

    all_items = list(phrases_by_id.values())
    audio: list[dict[str, Any]] = []
    for it in all_items:
        audio.extend(audio_for(it["id"]))
    for extra in data.get("extra_audio_assets") or []:
        audio.append(extra)

    lesson_items: list[dict[str, Any]] = []
    lessons_json: list[dict[str, Any]] = []
    for lesson in lessons_meta:
        lid = lesson["id"]
        core = [phrases_by_id[pid] for pid in lesson["phrase_ids"]]
        lessons_json.append(
            {
                "id": lid,
                "unit_id": lesson["unit_id"],
                "ordinal": lesson["ordinal"],
                "title": lesson["title"],
                "description": lesson["description"],
                "estimated_minutes": lesson["estimated_minutes"],
            }
        )
        lesson_items.extend(
            [{"lesson_id": lid, "learning_item_id": it["id"], "sort_order": n + 1} for n, it in enumerate(core)]
        )

    if exercises_hand:
        hand = list(exercises_hand)
    else:
        hand = []
        for lesson in lessons_meta:
            if lesson.get("hand_exercises"):
                hand.extend(lesson["hand_exercises"])

    return {
        "content_version": data["content_version"],
        "course": data["course"],
        "levels": data["levels"],
        "units": data["units"],
        "lessons": lessons_json,
        "learning_items": all_items,
        "audio_assets": audio,
        "lesson_items": lesson_items,
        "exercises": hand + generated_exercises,
    }