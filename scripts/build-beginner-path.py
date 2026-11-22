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

    neigh1 = [
        reg("item-nanu-vasisutteni", "ನಾನು ಇಲ್ಲಿಯೇ ವಾಸಿಸುತ್ತೇನೆ", "nānu illiyē vāsisuttēne", "I live right here", tags=["home", "neighbours"], difficulty=2),
        reg("item-security-helu", "ಸೆಕ್ಯುರಿಟಿಗೆ ಹೇಳಿ", "sekyuriti ge hēḷi", "Tell security", tags=["home"], difficulty=2),
        reg("item-yavaga-barthira", "ಯಾವಾಗ ಬರುತ್ತೀರಾ?", "yāvāga baruttīrā?", "When will you come?", tags=["home", "question"], difficulty=2),
        reg("item-parcel-ide", "ಪಾರ್ಸೆಲ್ ಬಂದಿದೆ", "pārsel bandide", "A parcel has arrived", tags=["home"], difficulty=2),
    ]
    neigh2 = [
        reg("item-sahaya-beku", "ಸಹಾಯ ಬೇಕು", "sahāya bēku", "I need help", tags=["home", "neighbours"], difficulty=2),
        reg("item-neeru-illa", "ನೀರು ಇಲ್ಲ", "nīru illa", "No water", tags=["home"], difficulty=2),
        reg("item-current-illa", "ಕರೆಂಟ್ ಇಲ್ಲ", "kareṇṭ illa", "No power", tags=["home"], difficulty=2),
        reg("item-olleyavaru", "ತುಂಬಾ ಒಳ್ಳೆಯವರು", "tumba oḷḷeyavaru", "You are very kind", tags=["neighbours", "politeness"], difficulty=2),
    ]

    health1 = [
        reg("item-vaidyara-bheti", "ವೈದ್ಯರ ಭೇಟಿ", "vaidyara bhēṭi", "Doctor's appointment", tags=["health"], difficulty=3),
        reg("item-tumba-novu", "ತುಂಬಾ ನೋವು", "tumba nōvu", "A lot of pain", tags=["health"], difficulty=2),
        reg("item-maththu-kodi", "ಮದ್ದು ಕೊಡಿ", "maddu koḍi", "Give medicine", tags=["health", "pharmacy"], difficulty=2),
        reg("item-fever-ide", "ಜ್ವರ ಇದೆ", "jvara ide", "I have a fever", tags=["health"], difficulty=2),
    ]
    health2 = [
        reg("item-hospital-ellige", "ಆಸ್ಪತ್ರೆ ಎಲ್ಲಿಗೆ?", "āspatre ellige?", "Where is the hospital?", tags=["health", "directions"], difficulty=2),
        reg("item-visranti-beku", "ವಿಶ್ರಾಂತಿ ಬೇಕು", "viśrānti bēku", "I need rest", tags=["health"], difficulty=2),
        reg("item-weak-iddini", "ದುರ್ಬಲವಾಗಿದ್ದೀನಿ", "durbalavāgiddīni", "I feel weak", tags=["health"], difficulty=3),
        reg("item-naale-beku", "ನಾಳೆ ಬೇಕು", "nāḷe bēku", "I need it tomorrow", tags=["health", "time"], difficulty=2),
    ]

    work1 = [
        reg("item-meeting-ide", "ಮೀಟಿಂಗ್ ಇದೆ", "mīṭiṅg ide", "There is a meeting", tags=["work"], difficulty=2),
        reg("item-office-ge-hogi", "ಆಫೀಸ್‌ಗೆ ಹೋಗಿ", "āfīs ge hōgi", "Go to the office", tags=["work"], difficulty=2),
        reg("item-samayakke-banni", "ಸಮಯಕ್ಕೆ ಬನ್ನಿ", "samayakke banni", "Come on time", tags=["work"], difficulty=2),
        reg("item-report-kalsi", "ರಿಪೋರ್ಟ್ ಕಳಿಸಿ", "ripōrṭ kaḷisi", "Send the report", tags=["work"], difficulty=3),
    ]
    work2 = [
        reg("item-manager-ondu", "ಒಂದು ನಿಮಿಷ", "ondu nimisha", "One minute", context="Hold on — common with colleagues.", tags=["work"], difficulty=1),
        reg("item-email-beku", "ಇಮೇಲ್ ಬೇಕು", "imēl bēku", "I need an email", tags=["work"], difficulty=2),
        reg("item-call-madthini", "ಕಾಲ್ ಮಾಡ್ತೀನಿ", "kāl māḍtīni", "I'll make a call", tags=["work"], difficulty=2),
        reg("item-work-aitu", "ಕೆಲಸ ಆಯ್ತು", "kelasa āytu", "Work is done", tags=["work", "response"], difficulty=2),
    ]

    money1 = [
        reg("item-atm-ellige", "ATM ಎಲ್ಲಿದೆ?", "ATM elligide?", "Where is the ATM?", tags=["money"], difficulty=2),
        reg("item-upi-madthini", "UPI ಮಾಡ್ತೀನಿ", "UPI māḍtīni", "I'll pay by UPI", tags=["money"], difficulty=2),
        reg("item-account-number", "ಖಾತೆ ಸಂಖ್ಯೆ", "khāte sankhye", "Account number", tags=["money", "bank"], difficulty=3),
        reg("item-withdraw-beku", "ಹಣ ತೆಗೆದುಕೊಳ್ಳಬೇಕು", "haṇa tegedukoḷḷabēku", "I need to withdraw cash", tags=["money"], difficulty=3),
    ]
    money2 = [
        reg("item-suttu-kodi", "ಸುತ್ತು ಕೊಡಿ", "suttu koḍi", "Give change", tags=["money"], difficulty=2),
        reg("item-receipt-kodi", "ರಶೀದಿ ಕೊಡಿ", "raśīdi koḍi", "Give the receipt", tags=["money", "shopping"], difficulty=2),
        reg("item-card-swipe", "ಕಾರ್ಡ್ ಸ್ವೈಪ್ ಮಾಡಿ", "kārḍ svāip māḍi", "Swipe the card", tags=["money"], difficulty=2),
        reg("item-paisa-kammi", "ಹಣ ಕಡಿಮೆ", "haṇa kadi me", "Short on money", tags=["money"], difficulty=2),
    ]

    phone1 = [
        reg("item-phone-elli", "ಫೋನ್ ಎಲ್ಲಿದೆ?", "phōn elligide?", "Where's the phone?", tags=["phone"], difficulty=2),
        reg("item-call-bantu", "ಕಾಲ್ ಬರುತ್ತಿದೆ", "kāl baruttide", "A call is coming in", tags=["phone"], difficulty=2),
        reg("item-message-kalsi", "ಮೆಸೇಜ್ ಕಳಿಸಿ", "mesēj kaḷisi", "Send a message", tags=["phone"], difficulty=2),
        reg("item-network-illa", "ನೆಟ್‌ವರ್ಕ್ ಇಲ್ಲ", "neṭvark illa", "No network signal", tags=["phone"], difficulty=2),
    ]
    phone2 = [
        reg("item-tumba-late", "ತುಂಬಾ ಲೇಟ್ ಆಯ್ತು", "tumba lēṭ āytu", "Got very late", tags=["phone", "time"], difficulty=2),
        reg("item-callback-madthini", "ಕಾಲ್ ಬ್ಯಾಕ್ ಮಾಡ್ತೀನಿ", "kāl byāk māḍtīni", "I'll call you back", tags=["phone"], difficulty=2),
        reg("item-voice-clear-illa", "ಧ್ವನಿ ಸ್ಪಷ್ಟವಿಲ್ಲ", "dhvani spaṣṭavilla", "Voice isn't clear", tags=["phone"], difficulty=3),
        reg("item-badige-hogi", "ಬ್ಯಾಡಗೆ ಹೋಗಿ", "byāḍige hōgi", "Go offline / hang up", context="Colloquial way to say the call dropped.", tags=["phone"], difficulty=3),
    ]

    school1 = [
        reg("item-school-ge", "ಸ್ಕೂಲ್‌ಗೆ ಹೋಗೋಣ", "skūl ge hōgōṇa", "Let's go to school", tags=["family", "school"], difficulty=2),
        reg("item-magu-elli", "ಮಗು ಎಲ್ಲಿದೆ?", "magu elligide?", "Where is the child?", tags=["family"], difficulty=2),
        reg("item-pickup-beku", "ಪಿಕಪ್ ಬೇಕು", "pikap bēku", "Need a pickup", accepted=["pickup beku"], tags=["family", "school"], difficulty=2),
        reg("item-banni-ready", "ಬನ್ನಿ ರೆಡಿ", "banni reḍi", "Come on, get ready", tags=["family"], difficulty=2),
    ]
    school2 = [
        reg("item-homework-ide", "ಹೋಮ್ ವರ್ಕ್ ಇದೆ", "hōm vark ide", "There is homework", tags=["family", "school"], difficulty=2),
        reg("item-exam-ide", "ಪರೀಕ್ಷೆ ಇದೆ", "parīkṣe ide", "There is an exam", tags=["family", "school"], difficulty=2),
        reg("item-tiffin-beku", "ಟಿಫಿನ್ ಬೇಕು", "ṭifin bēku", "Need a lunch box", tags=["family"], difficulty=2),
        reg("item-bus-bidalu", "ಬಸ್ ಬಿಡಲು", "bas biḍalu", "To drop at the bus", tags=["family", "school"], difficulty=2),
    ]

    social1 = [
        reg("item-malleyagide", "ಮಳೆಯಾಗ್ತಿದೆ", "maḷeyāgtide", "It is raining", tags=["social", "weather"], difficulty=2),
        reg("item-tumba-bisi", "ತುಂಬಾ ಬಿಸಿ", "tumba bisi", "Very hot (weather)", tags=["social", "weather"], difficulty=2),
        reg("item-coffee-kudiyona", "ಕಾಫಿ ಕುಡಿಯೋಣ?", "kāfi kuḍiyōṇa?", "Shall we have coffee?", tags=["social"], difficulty=2),
        reg("item-visheshave-illa", "ವಿಶೇಷವೇ ಇಲ್ಲ", "viśeṣavē illa", "Nothing special", tags=["social", "response"], difficulty=2),
    ]
    social2 = [
        reg("item-happy-aytu", "ಖುಶಿಯಾಯ್ತು", "khusiyāytu", "I'm happy about it", tags=["social"], difficulty=2),
        reg("item-avaga-bartini", "ಅವಾಗ ಬರ್ತೀನಿ", "avāga bartīni", "I'll come then", tags=["social", "time"], difficulty=2),
        reg("item-festival-shubha", "ಹಬ್ಬದ ಶುಭಾಶಯಗಳು", "habbada śubhāśayagaḷu", "Festival greetings", tags=["social"], difficulty=3),
        reg("item-madodu-en", "ಮಾಡೋದು ಏನು?", "māḍōdu ēnu?", "What shall we do?", tags=["social"], difficulty=2),
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
        ("lesson-neigh-1", "unit-7-home", 1, "Flat and security", "Deliveries, guards, and telling people you live here.", 12, neigh1),
        ("lesson-neigh-2", "unit-7-home", 2, "Asking neighbours", "Power, water, and quick favours.", 12, neigh2),
        ("lesson-health-1", "unit-8-health", 1, "Doctor and pharmacy", "Pain, fever, and medicine.", 14, health1),
        ("lesson-health-2", "unit-8-health", 2, "Feeling unwell", "Rest, hospital directions, and timing.", 14, health2),
        ("lesson-work-1", "unit-9-work", 1, "Office basics", "Meetings, reports, and being on time.", 14, work1),
        ("lesson-work-2", "unit-9-work", 2, "Quick work phrases", "Email, calls, and wrapping up tasks.", 12, work2),
        ("lesson-money-1", "unit-10-money", 1, "ATM and UPI", "Cash, accounts, and digital pay.", 12, money1),
        ("lesson-money-2", "unit-10-money", 2, "Receipts and cards", "Change, receipts, and swiping.", 12, money2),
        ("lesson-phone-1", "unit-11-phone", 1, "Calls and texts", "Ringing, messages, and signal.", 12, phone1),
        ("lesson-phone-2", "unit-11-phone", 2, "Call problems", "Late, callback, and bad connection.", 12, phone2),
        ("lesson-school-1", "unit-12-family", 1, "School run", "Getting kids ready and pickup.", 12, school1),
        ("lesson-school-2", "unit-12-family", 2, "Homework and bus", "Exams, tiffin, and the bus stop.", 12, school2),
        ("lesson-social-1", "unit-13-social", 1, "Weather and coffee", "Rain, heat, and casual invites.", 12, social1),
        ("lesson-social-2", "unit-13-social", 2, "Plans and festivals", "Happy news, timing, and wishes.", 12, social2),
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
        "lesson-neigh-1": {
            "instruction": "Parcel at the gate.",
            "steps": [
                {
                    "narration": "Security asks who you are.",
                    "partner": {"kannada": "ಯಾರು?", "transliteration": "yāru?", "english": "Who is it?"},
                },
                {
                    "narration": "Say you live here.",
                    "choices": [
                        {"label": "nānu illiyē vāsisuttēne", "hint": "I live right here", "correct": True},
                        {"label": "bill koḍi", "hint": "Give the bill", "correct": False},
                        {"label": "ondu", "hint": "One", "correct": False},
                    ],
                },
            ],
        },
        "lesson-neigh-2": {
            "instruction": "Knock on a neighbour's door.",
            "steps": [
                {
                    "narration": "You need help at home.",
                    "partner": {"kannada": "ಏನಾಯ್ತು?", "transliteration": "ēnāytu?", "english": "What happened?"},
                },
                {
                    "narration": "Explain no power.",
                    "choices": [
                        {"label": "kareṇṭ illa", "hint": "No power", "correct": True},
                        {"label": "dōse", "hint": "Dosa", "correct": False},
                        {"label": "āṭō biḍi", "hint": "Stop the auto", "correct": False},
                    ],
                },
            ],
        },
        "lesson-health-1": {
            "instruction": "At the pharmacy counter.",
            "steps": [
                {
                    "narration": "Pharmacist asks what you need.",
                    "partner": {"kannada": "ಏನು ಬೇಕು?", "transliteration": "ēnu bēku?", "english": "What do you need?"},
                },
                {
                    "narration": "Ask for medicine.",
                    "choices": [
                        {"label": "maddu koḍi", "hint": "Give medicine", "correct": True},
                        {"label": "ripōrṭ kaḷisi", "hint": "Send report", "correct": False},
                        {"label": "bala", "hint": "Right", "correct": False},
                    ],
                },
            ],
        },
        "lesson-health-2": {
            "instruction": "You feel weak today.",
            "steps": [
                {
                    "narration": "Friend checks on you.",
                    "partner": {"kannada": "ಏನಾಯ್ತು?", "transliteration": "ēnāytu?", "english": "What happened?"},
                },
                {
                    "narration": "Say you need rest.",
                    "choices": [
                        {"label": "viśrānti bēku", "hint": "I need rest", "correct": True},
                        {"label": "kelasa āytu", "hint": "Work is done", "correct": False},
                        {"label": "eshtu bēla?", "hint": "Price?", "correct": False},
                    ],
                },
            ],
        },
        "lesson-work-1": {
            "instruction": "Before a team meeting.",
            "steps": [
                {
                    "narration": "Colleague pings you.",
                    "partner": {"kannada": "ಮೀಟಿಂಗ್?", "transliteration": "mīṭiṅg?", "english": "Meeting?"},
                },
                {
                    "narration": "Confirm and ask them to be on time.",
                    "choices": [
                        {"label": "samayakke banni", "hint": "Come on time", "correct": True},
                        {"label": "nīru illa", "hint": "No water", "correct": False},
                        {"label": "ombattu", "hint": "Nine", "correct": False},
                    ],
                },
            ],
        },
        "lesson-work-2": {
            "instruction": "Wrapping up a task.",
            "steps": [
                {
                    "narration": "Manager asks for status.",
                    "partner": {"kannada": "ಆಯ್ತಾ?", "transliteration": "āytā?", "english": "Is it done?"},
                },
                {
                    "narration": "Say work is finished.",
                    "choices": [
                        {"label": "kelasa āytu", "hint": "Work is done", "correct": True},
                        {"label": "jvara ide", "hint": "I have fever", "correct": False},
                        {"label": "tumba jāsti", "hint": "Too expensive", "correct": False},
                    ],
                },
            ],
        },
        "lesson-money-1": {
            "instruction": "Paying at a shop with UPI.",
            "steps": [
                {
                    "narration": "Shopkeeper asks cash or UPI.",
                    "partner": {"kannada": "UPI ಇದೆಯಾ?", "transliteration": "UPI ideyā?", "english": "Do you have UPI?"},
                },
                {
                    "narration": "Say you'll pay by UPI.",
                    "choices": [
                        {"label": "UPI māḍtīni", "hint": "I'll pay by UPI", "correct": True},
                        {"label": "suttu koḍi", "hint": "Give change", "correct": False},
                        {"label": "skūl ge hōgōṇa", "hint": "Go to school", "correct": False},
                    ],
                },
            ],
        },
        "lesson-money-2": {
            "instruction": "At the counter after paying.",
            "steps": [
                {
                    "narration": "You paid cash.",
                    "partner": {"kannada": "ಸರಿ", "transliteration": "sari", "english": "Okay"},
                },
                {
                    "narration": "Ask for the receipt.",
                    "choices": [
                        {"label": "raśīdi koḍi", "hint": "Give the receipt", "correct": True},
                        {"label": "ATM elligide?", "hint": "Where is ATM?", "correct": False},
                        {"label": "maḷeyāgtide", "hint": "It is raining", "correct": False},
                    ],
                },
            ],
        },
        "lesson-phone-1": {
            "instruction": "Your phone rings in a meeting.",
            "steps": [
                {
                    "narration": "Colleague hears it.",
                    "partner": {"kannada": "ನಿಮ್ಮ ಫೋನ್", "transliteration": "nimma phōn", "english": "Your phone"},
                },
                {
                    "narration": "Say a call is coming.",
                    "choices": [
                        {"label": "kāl baruttide", "hint": "A call is coming in", "correct": True},
                        {"label": "neṭvark illa", "hint": "No network", "correct": False},
                        {"label": "ṭifin bēku", "hint": "Need lunch box", "correct": False},
                    ],
                },
            ],
        },
        "lesson-phone-2": {
            "instruction": "Bad connection on a call.",
            "steps": [
                {
                    "narration": "You can barely hear them.",
                    "partner": {"kannada": "ಕೇಳಿಸ್ತಾ?", "transliteration": "kēḷistā?", "english": "Can you hear?"},
                },
                {
                    "narration": "Say the voice isn't clear.",
                    "choices": [
                        {"label": "dhvani spaṣṭavilla", "hint": "Voice isn't clear", "correct": True},
                        {"label": "khusiyāytu", "hint": "I'm happy", "correct": False},
                        {"label": "parīkṣe ide", "hint": "Exam coming", "correct": False},
                    ],
                },
            ],
        },
        "lesson-school-1": {
            "instruction": "School morning rush.",
            "steps": [
                {
                    "narration": "You need to leave soon.",
                    "partner": {"kannada": "ಏನ್ ಮಾಡೋದು?", "transliteration": "ēn māḍōdu?", "english": "What to do?"},
                },
                {
                    "narration": "Suggest going to school.",
                    "choices": [
                        {"label": "skūl ge hōgōṇa", "hint": "Let's go to school", "correct": True},
                        {"label": "kāfi kuḍiyōṇa?", "hint": "Coffee?", "correct": False},
                        {"label": "kārḍ svāip māḍi", "hint": "Swipe card", "correct": False},
                    ],
                },
            ],
        },
        "lesson-school-2": {
            "instruction": "After school pickup.",
            "steps": [
                {
                    "narration": "Parent asks about school.",
                    "partner": {"kannada": "ಏನ್ ಆಯ್ತು?", "transliteration": "ēn āytu?", "english": "How did it go?"},
                },
                {
                    "narration": "Mention homework.",
                    "choices": [
                        {"label": "hōm vark ide", "hint": "There is homework", "correct": True},
                        {"label": "habbada śubhāśayagaḷu", "hint": "Festival greetings", "correct": False},
                        {"label": "haṇa kadi me", "hint": "Short on money", "correct": False},
                    ],
                },
            ],
        },
        "lesson-social-1": {
            "instruction": "Small talk about weather.",
            "steps": [
                {
                    "narration": "Friend looks outside.",
                    "partner": {"kannada": "ಮಳೆಯಾಗ್ತಿದೆ", "transliteration": "maḷeyāgtide", "english": "It is raining"},
                },
                {
                    "narration": "Agree it's raining.",
                    "choices": [
                        {"label": "maḷeyāgtide", "hint": "It is raining", "correct": True},
                        {"label": "tumba bisi", "hint": "Very hot", "correct": False},
                        {"label": "māḍōdu ēnu?", "hint": "What shall we do?", "correct": False},
                    ],
                },
                {
                    "narration": "Invite for coffee.",
                    "choices": [
                        {"label": "kāfi kuḍiyōṇa?", "hint": "Shall we have coffee?", "correct": True},
                        {"label": "bas biḍalu", "hint": "Bus drop", "correct": False},
                        {"label": "khāte sankhye", "hint": "Account number", "correct": False},
                    ],
                },
            ],
        },
        "lesson-social-2": {
            "instruction": "Making plans after good news.",
            "steps": [
                {
                    "narration": "Friend shares happy news.",
                    "partner": {"kannada": "ಖುಷಿ ಆಯ್ತು!", "transliteration": "khusi āytu!", "english": "So happy!"},
                },
                {
                    "narration": "React positively.",
                    "choices": [
                        {"label": "khusiyāytu", "hint": "I'm happy about it", "correct": True},
                        {"label": "viśeṣavē illa", "hint": "Nothing special", "correct": False},
                        {"label": "pikap bēku", "hint": "Need pickup", "correct": False},
                    ],
                },
                {
                    "narration": "Say when you'll come.",
                    "choices": [
                        {"label": "avāga bartīni", "hint": "I'll come then", "correct": True},
                        {"label": "kāl byāk māḍtīni", "hint": "Call back", "correct": False},
                        {"label": "mesēj kaḷisi", "hint": "Send message", "correct": False},
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
        "lesson-neigh-1": {
            "item_id": "item-security-helu",
            "instruction": "Tell security — sekyuriti ge ____",
            "blank": "sekyuriti ge _____",
            "accepted": ["hēḷi", "heli"],
        },
        "lesson-health-1": {
            "item_id": "item-fever-ide",
            "instruction": "I have a fever",
            "blank": "jvara _____",
            "accepted": ["ide"],
        },
        "lesson-work-1": {
            "item_id": "item-meeting-ide",
            "instruction": "There is a meeting",
            "blank": "mīṭiṅg _____",
            "accepted": ["ide"],
        },
        "lesson-money-1": {
            "item_id": "item-atm-ellige",
            "instruction": "Where is the ATM?",
            "blank": "ATM ell____?",
            "accepted": ["igide", "elligide"],
        },
        "lesson-phone-1": {
            "item_id": "item-message-kalsi",
            "instruction": "Send a message",
            "blank": "mesēj _____",
            "accepted": ["kaḷisi", "kalisi"],
        },
        "lesson-school-1": {
            "item_id": "item-magu-elli",
            "instruction": "Where is the child?",
            "blank": "magu ell____?",
            "accepted": ["igide", "elligide"],
        },
        "lesson-social-1": {
            "item_id": "item-malleyagide",
            "instruction": "It is raining",
            "blank": "maḷeyāg____",
            "accepted": ["tide", "gtide"],
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
        "lesson-neigh-2": {
            "item_id": "item-sahaya-beku",
            "tiles": ["bēku", "sahāya"],
            "solution": ["sahāya", "bēku"],
        },
        "lesson-health-2": {
            "item_id": "item-hospital-ellige",
            "tiles": ["ellige?", "āspatre"],
            "solution": ["āspatre", "ellige?"],
        },
        "lesson-work-2": {
            "item_id": "item-call-madthini",
            "tiles": ["māḍtīni", "kāl"],
            "solution": ["kāl", "māḍtīni"],
        },
        "lesson-money-2": {
            "item_id": "item-card-swipe",
            "tiles": ["māḍi", "kārḍ svāip"],
            "solution": ["kārḍ svāip", "māḍi"],
        },
        "lesson-phone-2": {
            "item_id": "item-callback-madthini",
            "tiles": ["māḍtīni", "kāl byāk"],
            "solution": ["kāl byāk", "māḍtīni"],
        },
        "lesson-school-2": {
            "item_id": "item-tiffin-beku",
            "tiles": ["bēku", "ṭifin"],
            "solution": ["ṭifin", "bēku"],
        },
        "lesson-social-2": {
            "item_id": "item-festival-shubha",
            "tiles": ["śubhāśayagaḷu", "habbada"],
            "solution": ["habbada", "śubhāśayagaḷu"],
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
        "content_version": 6,
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
                "description": "Travel, home, health, work, money, phone, family, and social chat.",
            }
        ],
        "units": [
            {"id": "unit-1-greetings", "level_id": "level-1-survival", "ordinal": 1, "title": "Greetings & basics", "description": "Start every conversation politely."},
            {"id": "unit-2-travel", "level_id": "level-1-survival", "ordinal": 2, "title": "Auto & directions", "description": "Phrases for cabs and finding your way."},
            {"id": "unit-3-numbers", "level_id": "level-1-survival", "ordinal": 3, "title": "Numbers & prices", "description": "Count and ask how much."},
            {"id": "unit-4-food", "level_id": "level-1-survival", "ordinal": 4, "title": "Food & cafes", "description": "Order tea, idli, and pay the bill."},
            {"id": "unit-5-shopping", "level_id": "level-1-survival", "ordinal": 5, "title": "Shopping", "description": "Want this, what's the price, a little less."},
            {"id": "unit-6-directions", "level_id": "level-1-survival", "ordinal": 6, "title": "On foot", "description": "Left, right, near, and far."},
            {"id": "unit-7-home", "level_id": "level-1-survival", "ordinal": 7, "title": "Home & neighbours", "description": "Security, deliveries, and asking next door."},
            {"id": "unit-8-health", "level_id": "level-1-survival", "ordinal": 8, "title": "Health", "description": "Doctor, pharmacy, and feeling unwell."},
            {"id": "unit-9-work", "level_id": "level-1-survival", "ordinal": 9, "title": "Work", "description": "Meetings, email, and quick office chat."},
            {"id": "unit-10-money", "level_id": "level-1-survival", "ordinal": 10, "title": "Money & bank", "description": "ATM, UPI, receipts, and change."},
            {"id": "unit-11-phone", "level_id": "level-1-survival", "ordinal": 11, "title": "Phone", "description": "Calls, texts, and bad signal."},
            {"id": "unit-12-family", "level_id": "level-1-survival", "ordinal": 12, "title": "Family & school", "description": "School run, homework, and pickup."},
            {"id": "unit-13-social", "level_id": "level-1-survival", "ordinal": 13, "title": "Social chat", "description": "Weather, coffee, plans, and festivals."},
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