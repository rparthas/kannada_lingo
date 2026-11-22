#!/usr/bin/env python3
"""Regenerate content/curriculum/beginner-path.json from structured lesson data."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "content" / "curriculum" / "beginner-path.json"


def audio_for(item_id: str) -> list[dict[str, Any]]:
    base = f"content/audio/{item_id}"
    return [
        {
            "id": f"audio-{item_id}-normal",
            "learning_item_id": item_id,
            "source": "human",
            "speaking_speed": "normal",
            "review_status": "approved",
            "duration_ms": 450,
            "file_format": "wav",
            "relative_path": f"{base}-normal.wav",
        },
        {
            "id": f"audio-{item_id}-slow",
            "learning_item_id": item_id,
            "source": "human",
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
    # ensure correct at index 1
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


def build() -> dict[str, Any]:
    # --- learning items keyed by id, grouped per lesson ---
    L: dict[str, dict[str, Any]] = {}

    def reg(
        id_: str,
        kn: str,
        tr: str,
        en: str,
        *,
        context: str | None = None,
        tags: list[str] | None = None,
        difficulty: int = 1,
        accepted: list[str] | None = None,
        register: str = "informal",
    ) -> dict[str, Any]:
        o = {
            "id": id_,
            "kannada_text": kn,
            "transliteration": tr,
            "english_meaning": en,
            "register": register,
            "tags": tags or [],
            "difficulty": difficulty,
            "validation_status": "approved",
        }
        if context:
            o["context_note"] = context
        if accepted:
            o["accepted_answers"] = accepted
        L[id_] = o
        return o

    # Greetings unit (existing + new)
    greet1 = [
        reg("item-namaskara", "ನಮಸ್ಕಾರ", "namaskāra", "Hello (formal greeting)", context="Safe default with shop staff and neighbours.", tags=["greeting", "home"], register="neutral"),
        reg("item-hengidira", "ಹೇಗಿದ್ದೀರಾ?", "hēgiddīrā?", "How are you? (respectful)", context="Use with elders or polite settings.", tags=["greeting"], register="formal"),
        reg("item-chennagi-idini", "ಚೆನ್ನಾಗಿ ಇದ್ದೀನಿ", "cennāgi iddīni", "I am fine", tags=["greeting", "response"]),
        reg("item-dhanyavada", "ಧನ್ಯವಾದ", "dhanyavāda", "Thank you", tags=["politeness"], register="neutral"),
        reg("item-sari", "ಸರಿ", "sari", "Okay / all right", accepted=["okay", "ok", "alright"], tags=["response"]),
        reg("item-illa", "ಇಲ್ಲ", "illa", "No", context="General negation.", tags=["response"]),
    ]
    greet2 = [
        reg("item-houdu", "ಹೌದು", "houdu", "Yes", accepted=["haudu"], tags=["response"]),
        reg("item-dayavittu", "ದಯವಿಟ್ಟು", "dayavittu", "Please", tags=["politeness"], register="neutral"),
        reg("item-kshamisi", "ಕ್ಷಮಿಸಿ", "kṣamisi", "Sorry / excuse me", tags=["politeness"]),
        reg("item-matte-sigona", "ಮತ್ತೆ ಸಿಗೋಣ", "matte sigōna", "See you again", context="Friendly goodbye.", tags=["greeting"]),
        reg("item-shubha-ratri", "ಶುಭ ರಾತ್ರಿ", "śubha rātri", "Good night", tags=["greeting"]),
    ]

    auto1 = [
        reg("item-auto-bidu", "ಆಟೋ ಬಿಡಿ", "āṭō biḍi", "Stop the auto here", tags=["auto", "transport"], difficulty=2),
        reg("item-elli-hogbeku", "ಎಲ್ಲಿಗೆ ಹೋಗಬೇಕು?", "ellige hōgabēku?", "Where do you need to go?", tags=["auto", "question"], difficulty=2),
        reg("item-meter-prati", "ಮೀಟರ್ ಪ್ರಕಾರ", "mīṭar prakāra", "By the meter (fare)", tags=["auto", "fare"], difficulty=2),
        reg("item-aidu-nimisha", "ಐದು ನಿಮಿಷ ಬೇಕು", "aidu nimisha bēku", "Five minutes, please", tags=["time"], difficulty=2),
    ]
    auto2 = [
        reg("item-illi-nilli", "ಇಲ್ಲಿ ನಿಲ್ಲಿ", "illi nilli", "Stop here", tags=["auto", "transport"], difficulty=2),
        reg("item-ellige-hogi", "ಅಲ್ಲಿಗೆ ಹೋಗಿ", "allige hōgi", "Go there", tags=["auto", "direction"], difficulty=2),
        reg("item-tumba-doora", "ತುಂಬಾ ದೂರ", "tumba dūra", "Very far", tags=["auto"], difficulty=2),
        reg("item-bere-varthe", "ಬೇರೆ ವಾತೆ ಇದೆಯಾ?", "bēre vāte ideyā?", "Is there another route?", tags=["auto", "question"], difficulty=3),
    ]

    nums1 = [
        reg("item-ondu", "ಒಂದು", "ondu", "One (1)", tags=["numbers"], difficulty=1),
        reg("item-eradu", "ಎರಡು", "eraḍu", "Two (2)", tags=["numbers"], difficulty=1),
        reg("item-mooru", "ಮೂರು", "mūru", "Three (3)", tags=["numbers"], difficulty=1),
        reg("item-naalku", "ನಾಲ್ಕು", "nālku", "Four (4)", tags=["numbers"], difficulty=1),
        reg("item-aidu-num", "ಐದು", "aidu", "Five (5)", tags=["numbers"], difficulty=1),
    ]
    nums2 = [
        reg("item-aaru", "ಆರು", "āru", "Six (6)", tags=["numbers"], difficulty=1),
        reg("item-elu", "ಏಳು", "ēḷu", "Seven (7)", tags=["numbers"], difficulty=1),
        reg("item-entu", "ಎಂಟು", "eṇṭu", "Eight (8)", tags=["numbers"], difficulty=1),
        reg("item-ombattu", "ಒಂಬತ್ತು", "ombattu", "Nine (9)", tags=["numbers"], difficulty=1),
        reg("item-hattu", "ಹತ್ತು", "hattu", "Ten (10)", tags=["numbers"], difficulty=1),
        reg("item-eshtu", "ಎಷ್ಟು?", "eshtu?", "How much? / How many?", tags=["numbers", "shopping"], difficulty=2),
    ]

    food1 = [
        reg("item-idli", "ಒಂದು ಇಡ್ಲಿ", "ondu idli", "One idli", tags=["food"], difficulty=2),
        reg("item-dosa", "ದೋಸೆ", "dōse", "Dosa", accepted=["dosa"], tags=["food"], difficulty=1),
        reg("item-kafe", "ಒಂದು ಚಹಾ", "ondu chahā", "One tea", accepted=["ondu chai", "one tea"], tags=["food"], difficulty=2),
        reg("item-swasthi", "ನನಗೆ ಇದು ಬೇಕು", "nanagē idu bēku", "I want this", tags=["food", "shopping"], difficulty=2),
    ]
    food2 = [
        reg("item-shakaahaari", "ಶಾಕಾಹಾರಿ", "śākāhāri", "Vegetarian", tags=["food"], difficulty=2),
        reg("item-mirchi-kammi", "ಮೆಣಸು ಕಡಿಮೆ", "meṇasu kadi me", "Less spice", tags=["food"], difficulty=2),
        reg("item-bili-kodi", "ಬಿಲ್ ಕೊಡಿ", "bill koḍi", "Give the bill", tags=["food", "shopping"], difficulty=2),
        reg("item-ruchiyagi", "ರುಚಿಯಾಗಿ ಇತ್ತು", "ruciyāgi ittu", "It was tasty", tags=["food", "response"], difficulty=3),
    ]

    shop1 = [
        reg("item-beku", "ಬೇಕು", "bēku", "Want / need", tags=["shopping"], difficulty=1),
        reg("item-beda", "ಬೇಡ", "bēḍa", "Don't want", tags=["shopping"], difficulty=1),
        reg("item-eshtu-beela", "ಎಷ್ಟು ಬೇಲ?", "eshtu bēla?", "What's the price?", tags=["shopping"], difficulty=2),
        reg("item-kodthira", "ಕೊಡ್ತೀರಾ?", "koḍtīrā?", "Will you give it?", tags=["shopping"], difficulty=2),
    ]
    shop2 = [
        reg("item-tumba-jasta", "ತುಂಬಾ ಜಾಸ್ತಿ", "tumba jāsti", "Too expensive", tags=["shopping"], difficulty=2),
        reg("item-swalpa-kami", "ಸ್ವಲ್ಪ ಕಡಿಮೆ", "svalpa kadi me", "A little less", tags=["shopping"], difficulty=2),
        reg("item-cash-ide", "ಕ್ಯಾಶ್ ಇದೆ", "kyāsh ide", "I have cash", tags=["shopping"], difficulty=2),
        reg("item-samayavaagilla", "ಸಮಯವಾಗಿಲ್ಲ", "samayavāgilla", "No time", tags=["response"], difficulty=2),
    ]

    dir1 = [
        reg("item-bala", "ಬಲ", "bala", "Right (direction)", tags=["directions"], difficulty=2),
        reg("item-eda", "ಎಡ", "eḍa", "Left", tags=["directions"], difficulty=2),
        reg("item-nera", "ನೇರ", "nēra", "Straight ahead", tags=["directions"], difficulty=2),
        reg("item-elligide", "ಎಲ್ಲಿದೆ?", "elligide?", "Where is it?", tags=["directions", "question"], difficulty=2),
    ]
    dir2 = [
        reg("item-hattira", "ಹತ್ತಿರ", "hattira", "Near / close by", tags=["directions"], difficulty=2),
        reg("item-doora", "ದೂರ", "dūra", "Far", tags=["directions"], difficulty=2),
        reg("item-illiyeee", "ಇಲ್ಲಿಯೇ", "illiyē", "Right here", tags=["directions"], difficulty=2),
        reg("item-dayavittu-helu", "ದಯವಿಟ್ಟು ಹೇಳಿ", "dayavittu hēḷi", "Please tell me", tags=["directions", "politeness"], difficulty=2, register="neutral"),
    ]

    lessons_meta = [
        ("lesson-greetings-1", "unit-1-greetings", 1, "Hello and thank you", "Core polite phrases you'll use many times a day.", 12, greet1),
        ("lesson-greetings-2", "unit-1-greetings", 2, "Yes, please, and goodbye", "Polite words to open and close any chat.", 12, greet2),
        ("lesson-auto-1", "unit-2-travel", 1, "Talking to your auto driver", "Fare, destination, and simple requests.", 15, auto1),
        ("lesson-auto-2", "unit-2-travel", 2, "Routes and stopping", "Steer the ride when maps fail.", 14, auto2),
        ("lesson-numbers-1", "unit-3-numbers", 1, "Numbers 1–5", "Count things you order and pay for.", 10, nums1),
        ("lesson-numbers-2", "unit-3-numbers", 2, "Six to ten and how much", "Bigger counts and asking price.", 12, nums2),
        ("lesson-food-1", "unit-4-food", 1, "Ordering basics", "Idli, dosa, tea, and pointing at the menu.", 14, food1),
        ("lesson-food-2", "unit-4-food", 2, "Preferences and paying", "Spice level, veg, and the bill.", 14, food2),
        ("lesson-shop-1", "unit-5-shopping", 1, "Want this, how much?", "Market and kirana counter phrases.", 12, shop1),
        ("lesson-shop-2", "unit-5-shopping", 2, "Bargaining gently", "When the quote feels too high.", 12, shop2),
        ("lesson-dir-1", "unit-6-directions", 1, "Left, right, straight", "Follow local directions on foot.", 12, dir1),
        ("lesson-dir-2", "unit-6-directions", 2, "Near, far, right here", "Pin down where something is.", 12, dir2),
    ]

    # Preserve hand-tuned exercises for first two lessons
    exercises_hand = [
        {
            "id": "ex-greet-flash-1",
            "lesson_id": "lesson-greetings-1",
            "learning_item_id": "item-namaskara",
            "exercise_type": "vocabulary_flashcard",
            "sort_order": 1,
            "prompt": {"instruction": "Learn this greeting."},
        },
        {
            "id": "ex-greet-mcq-1",
            "lesson_id": "lesson-greetings-1",
            "learning_item_id": "item-namaskara",
            "exercise_type": "listen_identify",
            "sort_order": 2,
            "prompt": {
                "instruction": "What does this phrase mean?",
                "choices": ["Thank you", "Hello (formal greeting)", "Good night", "Where are you going?"],
                "correct_index": 1,
            },
        },
        {
            "id": "ex-greet-en-kn-1",
            "lesson_id": "lesson-greetings-1",
            "learning_item_id": "item-dhanyavada",
            "exercise_type": "english_to_kannada",
            "sort_order": 3,
            "prompt": {"instruction": "How do you say 'Thank you' in Kannada?"},
        },
        {
            "id": "ex-greet-kn-en-1",
            "lesson_id": "lesson-greetings-1",
            "learning_item_id": "item-sari",
            "exercise_type": "kannada_to_english",
            "sort_order": 4,
            "prompt": {
                "instruction": "Choose the best English meaning.",
                "choices": ["No", "Please wait", "Okay / all right", "How are you?"],
                "correct_index": 2,
            },
        },
        {
            "id": "ex-greet-fill-1",
            "lesson_id": "lesson-greetings-1",
            "learning_item_id": "item-chennagi-idini",
            "exercise_type": "fill_blank",
            "sort_order": 5,
            "prompt": {
                "instruction": "Complete the reply: 'I am fine'",
                "blanked_transliteration": "cennāgi _____",
                "accepted": ["iddīni", "iddini"],
            },
        },
        {
            "id": "ex-greet-convo-1",
            "lesson_id": "lesson-greetings-1",
            "exercise_type": "scripted_conversation",
            "sort_order": 6,
            "prompt": {
                "instruction": "Short exchange at a neighbourhood shop.",
                "steps": [
                    {
                        "narration": "The shopkeeper greets you.",
                        "partner": {"kannada": "ನಮಸ್ಕಾರ", "transliteration": "namaskāra", "english": "Hello"},
                    },
                    {
                        "narration": "Reply with the same polite greeting.",
                        "choices": [
                            {"label": "namaskāra", "hint": "Hello (formal)", "correct": True},
                            {"label": "illa", "hint": "No", "correct": False},
                            {"label": "dhanyavāda", "hint": "Thank you", "correct": False},
                        ],
                        "explanation": "Mirror a greeting with namaskāra before you ask for anything.",
                    },
                    {
                        "narration": "They ask how you are.",
                        "partner": {"kannada": "ಹೇಗಿದ್ದೀರಾ?", "transliteration": "hēgiddīrā?", "english": "How are you?"},
                    },
                    {
                        "narration": "Choose a natural reply.",
                        "choices": [
                            {"label": "cennāgi iddīni", "hint": "I am fine", "correct": True},
                            {"label": "sari", "hint": "Okay", "correct": False},
                            {"label": "āṭō biḍi", "hint": "Stop the auto", "correct": False},
                        ],
                        "explanation": "cennāgi iddīni is the usual polite answer.",
                    },
                ],
            },
        },
        {
            "id": "ex-auto-flash-1",
            "lesson_id": "lesson-auto-1",
            "learning_item_id": "item-auto-bidu",
            "exercise_type": "vocabulary_flashcard",
            "sort_order": 1,
            "prompt": {"instruction": "Phrase for stopping your auto."},
        },
        {
            "id": "ex-auto-mcq-1",
            "lesson_id": "lesson-auto-1",
            "learning_item_id": "item-meter-prati",
            "exercise_type": "listen_identify",
            "sort_order": 2,
            "prompt": {
                "instruction": "What does this mean for your ride?",
                "choices": ["Stop here", "By the meter (fare)", "Turn left", "I don't know"],
                "correct_index": 1,
            },
        },
        {
            "id": "ex-auto-en-kn-1",
            "lesson_id": "lesson-auto-1",
            "learning_item_id": "item-auto-bidu",
            "exercise_type": "english_to_kannada",
            "sort_order": 3,
            "prompt": {"instruction": "Say: 'Stop the auto here'."},
        },
        {
            "id": "ex-auto-order-1",
            "lesson_id": "lesson-auto-1",
            "learning_item_id": "item-auto-bidu",
            "exercise_type": "sentence_construction",
            "sort_order": 4,
            "prompt": {
                "instruction": "Arrange the words (transliteration tiles).",
                "tiles": ["biḍi", "āṭō"],
                "solution": ["āṭō", "biḍi"],
            },
        },
        {
            "id": "ex-auto-repeat-1",
            "lesson_id": "lesson-auto-1",
            "learning_item_id": "item-meter-prati",
            "exercise_type": "listen_repeat",
            "sort_order": 5,
            "prompt": {"instruction": "Listen and repeat aloud. Mark how you did."},
        },
        {
            "id": "ex-auto-convo-1",
            "lesson_id": "lesson-auto-1",
            "exercise_type": "scripted_conversation",
            "sort_order": 6,
            "prompt": {
                "instruction": "You're in an auto — pick what to say next.",
                "steps": [
                    {
                        "narration": "The driver quotes a flat fare.",
                        "partner": {"kannada": "ಐವತ್ತು ರೂಪಾಯಿ", "transliteration": "aivattu rūpāyi", "english": "Fifty rupees"},
                    },
                    {
                        "narration": "Ask to use the meter instead.",
                        "choices": [
                            {"label": "mīṭar prakāra", "hint": "By the meter", "correct": True},
                            {"label": "illa", "hint": "No", "correct": False},
                            {"label": "namaskāra", "hint": "Hello", "correct": False},
                        ],
                        "explanation": "mīṭar prakāra politely asks for meter fare.",
                    },
                    {
                        "narration": "You're near your stop.",
                        "partner": {"kannada": "ಎಲ್ಲಿ ಇಳಿಯಬೇಕು?", "transliteration": "elli iḷiyabēku?", "english": "Where should you get down?"},
                    },
                    {
                        "narration": "Tell the driver to stop here.",
                        "choices": [
                            {"label": "āṭō biḍi", "hint": "Stop the auto here", "correct": True},
                            {"label": "ellige hōgabēku?", "hint": "Where to go?", "correct": False},
                            {"label": "aidu nimisha bēku", "hint": "Five minutes please", "correct": False},
                        ],
                        "explanation": "āṭō biḍi is what locals say to stop the ride.",
                    },
                ],
            },
        },
    ]

    generated_exercises: list[dict[str, Any]] = []
    convo_specs: dict[str, dict[str, Any]] = {
        "lesson-greetings-2": {
            "instruction": "Wrap up a short chat politely.",
            "steps": [
                {"narration": "You need to leave.", "partner": {"kannada": "ಹೋಗಬೇಕಾ?", "transliteration": "hōgabēkā?", "english": "Do you need to go?"}},
                {
                    "narration": "Say yes politely.",
                    "choices": [
                        {"label": "houdu", "hint": "Yes", "correct": True},
                        {"label": "illa", "hint": "No", "correct": False},
                        {"label": "eshtu?", "hint": "How much?", "correct": False},
                    ],
                    "explanation": "houdu confirms without sounding abrupt.",
                },
                {
                    "narration": "Say goodbye.",
                    "choices": [
                        {"label": "matte sigōna", "hint": "See you again", "correct": True},
                        {"label": "kṣamisi", "hint": "Sorry", "correct": False},
                        {"label": "bill koḍi", "hint": "Give the bill", "correct": False},
                    ],
                    "explanation": "matte sigōna is a warm way to close.",
                },
            ],
        },
        "lesson-auto-2": {
            "instruction": "Steer the driver when the route looks wrong.",
            "steps": [
                {"narration": "The driver takes a long detour.", "partner": {"kannada": "ಇಲ್ಲಿ ರಸ್ತೆ ಸುಲಭ", "transliteration": "illi raste sulabha", "english": "This road is easy"}},
                {
                    "narration": "Ask if there is another route.",
                    "choices": [
                        {"label": "bēre vāte ideyā?", "hint": "Another route?", "correct": True},
                        {"label": "ondu idli", "hint": "One idli", "correct": False},
                        {"label": "śubha rātri", "hint": "Good night", "correct": False},
                    ],
                },
                {
                    "narration": "You're finally close.",
                    "choices": [
                        {"label": "illi nilli", "hint": "Stop here", "correct": True},
                        {"label": "tumba dūra", "hint": "Very far", "correct": False},
                        {"label": "bala", "hint": "Right", "correct": False},
                    ],
                },
            ],
        },
        "lesson-numbers-1": {
            "instruction": "Count items at a tea stall.",
            "steps": [
                {"narration": "Vendor asks how many cups.", "partner": {"kannada": "ಎಷ್ಟು?", "transliteration": "eshtu?", "english": "How many?"}},
                {
                    "narration": "You want two.",
                    "choices": [
                        {"label": "eraḍu", "hint": "Two", "correct": True},
                        {"label": "ondu", "hint": "One", "correct": False},
                        {"label": "hattu", "hint": "Ten", "correct": False},
                    ],
                },
            ],
        },
        "lesson-numbers-2": {
            "instruction": "Ask the price at a fruit cart.",
            "steps": [
                {"narration": "You point at the mangoes.", "partner": {"kannada": "ಇವು ಚೆನ್ನಾಗಿ ಇವೆ", "transliteration": "ivu cennāgi ive", "english": "These are good"}},
                {
                    "narration": "Ask how much.",
                    "choices": [
                        {"label": "eshtu?", "hint": "How much?", "correct": True},
                        {"label": "bēḍa", "hint": "Don't want", "correct": False},
                        {"label": "nēra", "hint": "Straight", "correct": False},
                    ],
                },
            ],
        },
        "lesson-food-1": {
            "instruction": "Order at a busy darshini counter.",
            "steps": [
                {"narration": "The server looks at you.", "partner": {"kannada": "ಏನು ಬೇಕು?", "transliteration": "ēnu bēku?", "english": "What do you want?"}},
                {
                    "narration": "Order one dosa.",
                    "choices": [
                        {"label": "ondu dōse", "hint": "One dosa — use dōse", "correct": True},
                        {"label": "bill koḍi", "hint": "Give the bill", "correct": False},
                        {"label": "eḍa", "hint": "Left", "correct": False},
                    ],
                    "explanation": "ondu idli / ondu chahā follow the same pattern.",
                },
            ],
        },
        "lesson-food-2": {
            "instruction": "Finish a meal politely.",
            "steps": [
                {"narration": "You finished eating.", "partner": {"kannada": "ಬಿಲ್ ಬೇಕಾ?", "transliteration": "bill bēkā?", "english": "Need the bill?"}},
                {
                    "narration": "Yes — ask for the bill.",
                    "choices": [
                        {"label": "bill koḍi", "hint": "Give the bill", "correct": True},
                        {"label": "houdu", "hint": "Yes", "correct": False},
                        {"label": "hattira", "hint": "Near", "correct": False},
                    ],
                },
            ],
        },
        "lesson-shop-1": {
            "instruction": "At a kirana shop counter.",
            "steps": [
                {"narration": "You point at biscuits.", "partner": {"kannada": "ಇದಾ?", "transliteration": "idā?", "english": "This one?"}},
                {
                    "narration": "Say you want it.",
                    "choices": [
                        {"label": "bēku", "hint": "Want / need", "correct": True},
                        {"label": "illa", "hint": "No", "correct": False},
                        {"label": "dūra", "hint": "Far", "correct": False},
                    ],
                },
                {
                    "narration": "Ask the price.",
                    "choices": [
                        {"label": "eshtu bēla?", "hint": "What's the price?", "correct": True},
                        {"label": "matte sigōna", "hint": "See you", "correct": False},
                        {"label": "śākāhāri", "hint": "Vegetarian", "correct": False},
                    ],
                },
            ],
        },
        "lesson-shop-2": {
            "instruction": "The quote feels high.",
            "steps": [
                {"narration": "Seller says a number.", "partner": {"kannada": "ಐನೂರು ರೂಪಾಯಿ", "transliteration": "ainūru rūpāyi", "english": "Five hundred rupees"}},
                {
                    "narration": "Say it's too expensive.",
                    "choices": [
                        {"label": "tumba jāsti", "hint": "Too expensive", "correct": True},
                        {"label": "cennāgi iddīni", "hint": "I am fine", "correct": False},
                        {"label": "āru", "hint": "Six", "correct": False},
                    ],
                },
            ],
        },
        "lesson-dir-1": {
            "instruction": "Someone gives you directions.",
            "steps": [
                {"narration": "You ask where the metro is.", "partner": {"kannada": "ಮೆಟ್ರೋ ಎಲ್ಲಿದೆ?", "transliteration": "metro elligide?", "english": "Where is the metro?"}},
                {
                    "narration": "They say turn right.",
                    "partner": {"kannada": "ಬಲ ತಿರುಗಿ", "transliteration": "bala tirugi", "english": "Turn right"},
                },
                {
                    "narration": "Repeat the direction word.",
                    "choices": [
                        {"label": "bala", "hint": "Right", "correct": True},
                        {"label": "eḍa", "hint": "Left", "correct": False},
                        {"label": "ondu", "hint": "One", "correct": False},
                    ],
                },
            ],
        },
        "lesson-dir-2": {
            "instruction": "You're almost there.",
            "steps": [
                {"narration": "A neighbour points.", "partner": {"kannada": "ಅಲ್ಲಿ", "transliteration": "alli", "english": "There"}},
                {
                    "narration": "Confirm it's close.",
                    "choices": [
                        {"label": "hattira", "hint": "Near", "correct": True},
                        {"label": "dūra", "hint": "Far", "correct": False},
                        {"label": "bēḍa", "hint": "Don't want", "correct": False},
                    ],
                },
                {
                    "narration": "Say it's right here.",
                    "choices": [
                        {"label": "illiyē", "hint": "Right here", "correct": True},
                        {"label": "tumba dūra", "hint": "Very far", "correct": False},
                        {"label": "mīṭar prakāra", "hint": "By meter", "correct": False},
                    ],
                },
            ],
        },
    }

    fill_specs: dict[str, dict[str, Any]] = {
        "lesson-greetings-2": {
            "item_id": "item-dayavittu",
            "instruction": "Complete: 'Please'",
            "blank": "dayavi____",
            "accepted": ["ttu", "vittu"],
        },
        "lesson-numbers-1": {
            "item_id": "item-mooru",
            "instruction": "Complete the number: Three",
            "blank": "mū___",
            "accepted": ["ru", "ooru"],
        },
        "lesson-numbers-2": {
            "item_id": "item-eshtu",
            "instruction": "How much?",
            "blank": "esh___?",
            "accepted": ["tu"],
        },
        "lesson-food-1": {
            "item_id": "item-swasthi",
            "instruction": "I want this — nanagē idu ____",
            "blank": "nanagē idu _____",
            "accepted": ["bēku", "beku"],
        },
        "lesson-shop-1": {
            "item_id": "item-beku",
            "instruction": "Want / need",
            "blank": "bē___",
            "accepted": ["ku", "eku"],
        },
        "lesson-dir-1": {
            "item_id": "item-nera",
            "instruction": "Straight ahead",
            "blank": "nē___",
            "accepted": ["ra"],
        },
    }

    tile_specs: dict[str, dict[str, Any]] = {
        "lesson-auto-2": {
            "item_id": "item-illi-nilli",
            "tiles": ["nilli", "illi"],
            "solution": ["illi", "nilli"],
        },
        "lesson-food-2": {
            "item_id": "item-bili-kodi",
            "tiles": ["koḍi", "bill"],
            "solution": ["bill", "koḍi"],
        },
        "lesson-shop-2": {
            "item_id": "item-swalpa-kami",
            "tiles": ["kadi me", "svalpa"],
            "solution": ["svalpa", "kadi me"],
        },
        "lesson-dir-2": {
            "item_id": "item-dayavittu-helu",
            "tiles": ["hēḷi", "dayavittu"],
            "solution": ["dayavittu", "hēḷi"],
        },
    }

    skip_lessons = {"lesson-greetings-1", "lesson-auto-1"}
    for lid, _uid, _ord, _title, _desc, _mins, core in lessons_meta:
        if lid in skip_lessons:
            continue
        slug = lid.replace("lesson-", "")
        generated_exercises.extend(
            lesson_exercises(
                lid,
                slug,
                core,
                convo_specs[lid],
                fill=fill_specs.get(lid),
                tiles=tile_specs.get(lid),
            )
        )

    all_items = list(L.values())
    audio: list[dict[str, Any]] = []
    for it in all_items:
        audio.extend(audio_for(it["id"]))
    # keep AI variation on sari from v3
    audio.append(
        {
            "id": "audio-item-sari-ai-variation",
            "learning_item_id": "item-sari",
            "source": "ai",
            "speaking_speed": "normal",
            "review_status": "approved",
            "duration_ms": 450,
            "file_format": "wav",
            "relative_path": "content/audio/item-sari-normal.wav",
        }
    )

    lesson_items: list[dict[str, Any]] = []
    lessons_json: list[dict[str, Any]] = []
    for lid, uid, ord_, title, desc, mins, core in lessons_meta:
        lessons_json.append(
            {
                "id": lid,
                "unit_id": uid,
                "ordinal": ord_,
                "title": title,
                "description": desc,
                "estimated_minutes": mins,
            }
        )
        lesson_items.extend(
            [{"lesson_id": lid, "learning_item_id": it["id"], "sort_order": n + 1} for n, it in enumerate(core)]
        )

    bundle = {
        "content_version": 4,
        "course": {
            "id": "course-kannada-quest",
            "title": "Kannada Quest",
            "description": "Practical spoken Bengaluru Kannada for everyday situations.",
        },
        "levels": [
            {
                "id": "level-1-survival",
                "course_id": "course-kannada-quest",
                "ordinal": 1,
                "title": "Survival Kannada",
                "description": "Greetings, yes/no, numbers, food, shopping, travel, and directions.",
            }
        ],
        "units": [
            {"id": "unit-1-greetings", "level_id": "level-1-survival", "ordinal": 1, "title": "Greetings & basics", "description": "Start every conversation politely."},
            {"id": "unit-2-travel", "level_id": "level-1-survival", "ordinal": 2, "title": "Auto & directions", "description": "Phrases for cabs and finding your way."},
            {"id": "unit-3-numbers", "level_id": "level-1-survival", "ordinal": 3, "title": "Numbers & prices", "description": "Count and ask how much."},
            {"id": "unit-4-food", "level_id": "level-1-survival", "ordinal": 4, "title": "Food & cafes", "description": "Order tea, idli, and pay the bill."},
            {"id": "unit-5-shopping", "level_id": "level-1-survival", "ordinal": 5, "title": "Shopping", "description": "Want this, what's the price, a little less."},
            {"id": "unit-6-directions", "level_id": "level-1-survival", "ordinal": 6, "title": "On foot", "description": "Left, right, near, and far."},
        ],
        "lessons": lessons_json,
        "learning_items": all_items,
        "audio_assets": audio,
        "lesson_items": lesson_items,
        "exercises": exercises_hand + generated_exercises,
    }
    return bundle


def main() -> None:
    bundle = build()
    OUT.write_text(json.dumps(bundle, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    n_lessons = len(bundle["lessons"])
    n_items = len(bundle["learning_items"])
    n_ex = len(bundle["exercises"])
    print(f"Wrote {OUT.name}: {n_items} items, {n_lessons} lessons, {n_ex} exercises (v{bundle['content_version']})")


if __name__ == "__main__":
    main()