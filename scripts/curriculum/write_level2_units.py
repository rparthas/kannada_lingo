#!/usr/bin/env python3
"""Write Level 2 unit spec files (run once when authoring; output is committed)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent.parent
UNITS_DIR = ROOT / "content" / "curriculum" / "specs" / "units"
LEVEL_ID = "level-2-everyday"

Phrase = dict[str, Any]
UnitSpec = dict[str, Any]


def phrase(
    pid: str,
    kn: str,
    tr: str,
    en: str,
    *,
    note: str | None = None,
    register: str = "informal",
    tags: list[str] | None = None,
    difficulty: int = 2,
    accepted: list[str] | None = None,
) -> Phrase:
    row: Phrase = {
        "id": pid,
        "kannada_text": kn,
        "transliteration": tr,
        "english_meaning": en,
        "register": register,
        "tags": tags or ["level2"],
        "difficulty": difficulty,
        "validation_status": "approved",
    }
    if note:
        row["context_note"] = note
    if accepted:
        row["accepted_answers"] = accepted
    return row


def lesson(
    lid: str,
    ordinal: int,
    title: str,
    description: str,
    phrase_ids: list[str],
    convo_instruction: str,
    partner_kn: str,
    partner_tr: str,
    partner_en: str,
    correct_label: str,
    correct_hint: str,
    fill_item: str,
    fill_en: str,
    fill_blank: str,
    fill_accepted: list[str],
) -> dict[str, Any]:
    return {
        "id": lid,
        "ordinal": ordinal,
        "title": title,
        "description": description,
        "estimated_minutes": 14,
        "phrase_ids": phrase_ids,
        "exercise_mode": "generated",
        "convo": {
            "instruction": convo_instruction,
            "steps": [
                {
                    "narration": "Your conversation partner speaks.",
                    "partner": {
                        "kannada": partner_kn,
                        "transliteration": partner_tr,
                        "english": partner_en,
                    },
                },
                {
                    "narration": "Pick the best reply.",
                    "choices": [
                        {"label": correct_label, "hint": correct_hint, "correct": True},
                        {"label": "illa", "hint": "No", "correct": False},
                        {"label": "dhanyavada", "hint": "Thank you", "correct": False},
                    ],
                },
            ],
        },
        "fill": {
            "item_id": fill_item,
            "instruction": fill_en,
            "blank": fill_blank,
            "accepted": fill_accepted,
        },
    }


UNITS: list[UnitSpec] = [
    {
        "id": "unit-l2-01-work-deeper",
        "ordinal": 1,
        "title": "Deeper work chat",
        "description": "Standups, deadlines, and polite pushback at the office.",
        "phrases": [
            phrase("item-l2-standup", "ಸ್ಟ್ಯಾಂಡಪ್ ಎಷ್ಟ್?", "sṭyāṇḍap eṣṭ?", "What time is standup?", note="Common in IT offices.", tags=["work", "level2"]),
            phrase("item-l2-deadline", "ಡೆಡ್‌ಲೈನ್ ಟೈಟ್", "ḍeḍlain ṭaiṭ", "The deadline is tight", difficulty=3),
            phrase("item-l2-blocked", "ನಾನು ಬ್ಲಾಕ್ ಆಗಿದ್ದೀನಿ", "nānu blāk āgiddīni", "I'm blocked", note="Explaining why work is stuck."),
            phrase("item-l2-update-kodi", "ಅಪ್ಡೇಟ್ ಕೊಡಿ", "apḍēṭ koḍi", "Give an update", register="formal"),
            phrase("item-l2-meeting-reach", "ಮೀಟಿಂಗ್‌ಗೆ ರೀಚ್ ಆಗಲಿಲ್ಲ", "mīṭiṅg ge rīc āgalilla", "Couldn't join the meeting", difficulty=3),
            phrase("item-l2-slide-share", "ಸ್ಲೈಡ್ ಶೇರ್ ಮಾಡ್ತೀನಿ", "slaiḍ śēr māḍtīni", "I'll share the slide", tags=["work", "level2"]),
            phrase("item-l2-followup", "ಫಾಲೋ ಅಪ್ ಮಾಡೋಣ", "phālō ap māḍōṇa", "Let's follow up", difficulty=3),
            phrase("item-l2-ping-later", "ಸಾಯಂಕಾಲ ತಾನೇ ಪಿಂಗ್ ಮಾಡ್ತೀನಿ", "sāyaṅkāla tāne piṅg māḍtīni", "I'll ping you this evening", difficulty=3),
            phrase("item-l2-agree-partial", "ಸರಿ, ಆದರೆ ಸಮಯ ಬೇಕು", "sari, ādare samaya bēku", "Okay, but I need time", note="Soft disagreement."),
            phrase("item-l2-eod", "ಇವತ್ತು EOD ಗೆ ಕಳಿಸ್ತೀನಿ", "ivattu EOD ge kaḷistīni", "I'll send it by EOD today", difficulty=3),
        ],
        "lessons": [
            lesson(
                "lesson-l2-work-1", 1, "Standups & status", "Updates and blockers.",
                [f"item-l2-standup", "item-l2-blocked", "item-l2-update-kodi", "item-l2-deadline", "item-l2-meeting-reach"],
                "During morning standup.",
                "ಆಪ್ಡೇಟ್?", "apḍēṭ?", "Update?",
                "nānu blāk", "I'm blocked",
                "item-l2-blocked", "I'm blocked", "nānu blāk _____", ["āgiddīni"],
            ),
            lesson(
                "lesson-l2-work-2", 2, "Deadlines & follow-up", "Sharing slides and pushing deadlines gently.",
                ["item-l2-slide-share", "item-l2-followup", "item-l2-ping-later", "item-l2-agree-partial", "item-l2-eod"],
                "After a planning call.",
                "ಇಂದು ಕಳಿಸ್ತೀರಾ?", "indu kaḷistīrā?", "Will you send today?",
                "ivattu EOD", "By EOD today",
                "item-l2-eod", "I'll send by EOD", "ivattu EOD ge _____", ["kaḷistīni"],
            ),
        ],
    },
    {
        "id": "unit-l2-02-neighborhood",
        "ordinal": 2,
        "title": "Neighborhood & society",
        "description": "Gate passes, complaints, and polite asks to neighbors.",
        "phrases": [
            phrase("item-l2-guest-coming", "ಅತಿಥಿ ಬರುತ್ತಾರೆ", "atithi baruttāre", "Guests are coming"),
            phrase("item-l2-gate-pass", "ಗೇಟ್ ಪಾಸ್ ಬೇಕು", "gēṭ pās bēku", "Need a gate pass"),
            phrase("item-l2-vehicle-number", "ವಾಹನ ಸಂಖ್ಯೆ ಇದೆ", "vāhana sankhye ide", "I have the vehicle number"),
            phrase("item-l2-noise", "ಸ್ವಲ್ಪ ಶಬ್ದ ಕಮ್ಮಿ ಮಾಡಿ", "svalpa śabda kummi māḍi", "Please reduce the noise a bit", register="formal"),
            phrase("item-l2-parking", "ಪಾರ್ಕಿಂಗ್ ಇಲ್ಲೀನಾ?", "pārkiṅg illīnā?", "Is parking allowed here?"),
            phrase("item-l2-elevator", "ಲಿಫ್ಟ್ ಹಾಳಾಗಿದೆ", "liṭ hāḷāgide", "The lift is broken"),
            phrase("item-l2-water-tank", "ವಾಟರ್ ಟ್ಯಾಂಕ್ ಖಾಲಿ", "vāṭar ṭyāṅk khāli", "Water tank is empty"),
            phrase("item-l2-morning-walk", "ಬೆಳಗ್ಗೆ ವಾಕ್ ಹೋಗ್ತೀನಿ", "beḷagge vāk hōgtīni", "I go for a walk in the morning"),
            phrase("item-l2-help-carry", "ಸಹಾಯ ಮಾಡ್ತೀರಾ?", "sahāya māḍtīrā?", "Can you help?", register="formal"),
            phrase("item-l2-society-meeting", "ಸೊಸೈಟಿ ಮೀಟಿಂಗ್ ಯಾವಾಗ?", "sosaiṭi mīṭiṅg yāvāga?", "When is the society meeting?", difficulty=3),
        ],
        "lessons": [
            lesson(
                "lesson-l2-neighbor-1", 1, "Gate & guests", "Visitors and security desk.",
                ["item-l2-guest-coming", "item-l2-gate-pass", "item-l2-vehicle-number", "item-l2-help-carry", "item-l2-parking"],
                "At the apartment gate.",
                "ಯಾರು ಬರುತ್ತಾರೆ?", "yāru baruttāre?", "Who is coming?",
                "atithi baruttāre", "Guests are coming",
                "item-l2-gate-pass", "Need a gate pass", "gēṭ pās _____", ["bēku"],
            ),
            lesson(
                "lesson-l2-neighbor-2", 2, "Building life", "Lift, water, and society notices.",
                ["item-l2-noise", "item-l2-elevator", "item-l2-water-tank", "item-l2-morning-walk", "item-l2-society-meeting"],
                "Talking to a neighbor in the corridor.",
                "ನೀರಿಲ್ಲ ಇಂದು.", "nīrilla indu.", "No water today.",
                "vāṭar ṭyāṅk khāli", "Tank is empty",
                "item-l2-water-tank", "Water tank empty", "vāṭar ṭyāṅk _____", ["khāli"],
            ),
        ],
    },
    {
        "id": "unit-l2-03-deliveries",
        "ordinal": 3,
        "title": "Deliveries & couriers",
        "description": "Swiggy, Amazon, and mismatched orders.",
        "phrases": [
            phrase("item-l2-order-placed", "ಆರ್ಡರ್ ಮಾಡಿದ್ದೀನಿ", "ārḍar māḍiddīni", "I placed an order"),
            phrase("item-l2-otp-share", "OTP ಹೇಳ್ತೀನಿ", "OTP hēḷtīni", "I'll tell you the OTP"),
            phrase("item-l2-wrong-item", "ತಪ್ಪು ಐಟಮ್ ಬಂದಿದೆ", "tappu aiṭam bandide", "Wrong item arrived"),
            phrase("item-l2-leave-door", "ಬಾಗಿಲ ಬಳಿ ಇಟ್ಟುಬಿಡಿ", "bāgila baḷi iṭṭubiḍi", "Leave it by the door", register="formal"),
            phrase("item-l2-delivery-late", "ತುಂಬಾ ಲೇಟ್ ಆಯ್ತು", "tumbā lēṭ āytu", "It was very late"),
            phrase("item-l2-call-on-arrival", "ಬಂದ ಮೇಲೆ ಕಾಲ್ ಮಾಡಿ", "banda mēle kāl māḍi", "Call when you arrive", register="formal"),
            phrase("item-l2-package-damaged", "ಪ್ಯಾಕೇಜ್ ಹಾನಿಯಾಗಿದೆ", "pyākēj hāniyāgide", "Package is damaged", difficulty=3),
            phrase("item-l2-refund", "ರಿಫಂಡ್ ಬೇಕು", "riphaṇḍ bēku", "I need a refund"),
            phrase("item-l2-security-desk", "ಸೆಕ್ಯುರಿಟಿ ಡೆಸ್ಕ್‌ನಲ್ಲಿ ಇದೆ", "sekyuriṭi desk nalli ide", "It's at the security desk"),
            phrase("item-l2-floor-number", "ಮೂರನೇ ಫ್ಲೋರ್", "mūranē phlōr", "Third floor"),
        ],
        "lessons": [
            lesson(
                "lesson-l2-delivery-1", 1, "Receiving orders", "OTP, floor, and door drop.",
                ["item-l2-order-placed", "item-l2-otp-share", "item-l2-call-on-arrival", "item-l2-leave-door", "item-l2-floor-number"],
                "Delivery partner at the gate.",
                "OTP ಹೇಳಿ.", "OTP hēḷi.", "Tell the OTP.",
                "OTP hēḷtīni", "I'll share OTP",
                "item-l2-otp-share", "I'll share OTP", "OTP _____", ["hēḷtīni"],
            ),
            lesson(
                "lesson-l2-delivery-2", 2, "When things go wrong", "Wrong item, damage, refund.",
                ["item-l2-wrong-item", "item-l2-delivery-late", "item-l2-package-damaged", "item-l2-refund", "item-l2-security-desk"],
                "Customer support call.",
                "ಸಮಸ್ಯೆ ಏನು?", "samasya ēnu?", "What is the problem?",
                "tappu aiṭam bandide", "Wrong item came",
                "item-l2-wrong-item", "Wrong item arrived", "tappu aiṭam _____", ["bandide"],
            ),
        ],
    },
    {
        "id": "unit-l2-04-festivals",
        "ordinal": 4,
        "title": "Festivals with neighbors",
        "description": "Invites, sweets, and polite declines.",
        "phrases": [
            phrase("item-l2-festival-wishes", "ಹಬ್ಬದ ಶುಭಾಶಯಗಳು", "habbada śubhāśayagaḷu", "Festival greetings", register="formal"),
            phrase("item-l2-invite-home", "ಮನೆಗೆ ಬನ್ನಿ", "manege banni", "Please come home", register="formal"),
            phrase("item-l2-sweets-share", "ಸ್ವೀಟ್ಸ್ ತೆಗೆದುಕೊಳ್ಳಿ", "svīṭs tegedukoḷḷi", "Please take some sweets", register="formal"),
            phrase("item-l2-sorry-busy", "ಕ್ಷಮಿಸಿ, ಇವತ್ತು ಬಿಸಿ", "kṣamisi, ivattu bisi", "Sorry, I'm busy today", note="Polite decline."),
            phrase("item-l2-decorate", "ಅಲಂಕರಿಸ್ತಿದ್ದೇವೆ", "alaṅkaristiddēve", "We are decorating"),
            phrase("item-l2-prayers", "ಪೂಜೆ ಇದೆ ಸಾಯಂಕಾಲ", "pūje ide sāyaṅkāla", "Puja is in the evening"),
            phrase("item-l2-dress-traditional", "ಪಾರಂಪರಿಕ ಉಡುಗೆ ಹಾಕಿದ್ದೀನಿ", "pāraṁparika uḍuge hākiddīni", "I'm wearing traditional dress", difficulty=3),
            phrase("item-l2-kids-excited", "ಮಕ್ಕಳಿಗೆ ತುಂಬಾ ಖುಷಿ", "makkaḷige tumba khuṣi", "Kids are very excited"),
            phrase("item-l2-gift-brought", "ಸಣ್ಣ ಉಡುಗೊರೆ ತಂದಿದ್ದೀನಿ", "saṇṇa uḍugore tandididdīni", "I brought a small gift", register="formal"),
            phrase("item-l2-see-you-event", "ಈವೆಂಟ್‌ನಲ್ಲಿ ಸಿಗೋಣ", "īvèṇṭ nalli sigōṇa", "See you at the event"),
        ],
        "lessons": [
            lesson(
                "lesson-l2-fest-1", 1, "Invitations", "Greet and invite neighbors.",
                ["item-l2-festival-wishes", "item-l2-invite-home", "item-l2-sweets-share", "item-l2-gift-brought", "item-l2-see-you-event"],
                "Festival day in the corridor.",
                "ಶುಭಾಶಯಗಳು!", "śubhāśayagaḷu!", "Greetings!",
                "habbada śubhāśayagaḷu", "Festival greetings",
                "item-l2-festival-wishes", "Festival greetings", "habbada _____", ["śubhāśayagaḷu"],
            ),
            lesson(
                "lesson-l2-fest-2", 2, "Busy but kind", "Declining without offending.",
                ["item-l2-sorry-busy", "item-l2-decorate", "item-l2-prayers", "item-l2-dress-traditional", "item-l2-kids-excited"],
                "Neighbor invites you inside.",
                "ಒಂದು ಚುಮುದು.", "ondu cumudu.", "A bite to eat?",
                "ivattu bisi", "Busy today",
                "item-l2-sorry-busy", "Sorry busy today", "ivattu _____", ["bisi"],
            ),
        ],
    },
    {
        "id": "unit-l2-05-home-services",
        "ordinal": 5,
        "title": "Home services",
        "description": "Plumber, electrician, and repair visits.",
        "phrases": [
            phrase("item-l2-leak", "ವಾಟರ್ ಲೀಕ್ ಆಗಿದೆ", "vāṭar līk āgide", "There is a water leak"),
            phrase("item-l2-plumber-call", "ಪ್ಲಂಬರ್ ಕರೆ ಮಾಡಿದ್ದೀನಿ", "plambar kare māḍiddīni", "I called a plumber"),
            phrase("item-l2-when-come", "ಎಷ್ಟ್ ಹೊತ್ತಿಗೆ ಬರುತ್ತೀರಾ?", "eṣṭ hottige baruttīrā?", "What time will you come?", register="formal"),
            phrase("item-l2-fuse-gone", "ಫ್ಯೂಜ್ ಹೋಗಿದೆ", "phyūj hōgide", "The fuse is blown"),
            phrase("item-l2-power-cut", "ಕರೆಂಟ್ ಹೋಗಿದೆ", "kareṇṭ hōgide", "Power is out"),
            phrase("item-l2-repair-cost", "ರಿಪೇರಿ ಎಷ್ಟು?", "ripēri eṣṭu?", "How much for the repair?"),
            phrase("item-l2-cash-or-upi", "ಕ್ಯಾಶ್ ಅಥವಾ UPI?", "kyāś athavā UPI?", "Cash or UPI?"),
            phrase("item-l2-works-now", "ಇದೀಗ ಸರಿ ಆಯ್ತು", "idīga sari āytu", "It works fine now"),
            phrase("item-l2-come-tomorrow", "ನಾಳೆ ಬನ್ನಿ", "nāḷe banni", "Come tomorrow", register="formal"),
            phrase("item-l2-spare-parts", "ಸ್ಪೇರ್ ಪಾರ್ಟ್ಸ್ ಬೇಕು", "spēr pārṭs bēku", "Need spare parts"),
        ],
        "lessons": [
            lesson(
                "lesson-l2-service-1", 1, "Plumber visit", "Leaks and timing.",
                ["item-l2-leak", "item-l2-plumber-call", "item-l2-when-come", "item-l2-come-tomorrow", "item-l2-works-now"],
                "Plumber at the door.",
                "ಸಮಸ್ಯೆ ಏನು?", "samasya ēnu?", "What's the problem?",
                "vāṭar līk", "Water leak",
                "item-l2-leak", "Water leak", "vāṭar līk _____", ["āgide"],
            ),
            lesson(
                "lesson-l2-service-2", 2, "Electrician & payment", "Fuse, cost, UPI.",
                ["item-l2-fuse-gone", "item-l2-power-cut", "item-l2-repair-cost", "item-l2-cash-or-upi", "item-l2-spare-parts"],
                "After fixing wiring.",
                "ಪೇಮೆಂಟ್?", "pēmeṇṭ?", "Payment?",
                "kyāś athavā UPI", "Cash or UPI",
                "item-l2-cash-or-upi", "Cash or UPI", "kyāś _____", ["athavā UPI"],
            ),
        ],
    },
    {
        "id": "unit-l2-06-travel-cab",
        "ordinal": 6,
        "title": "Cabs & short trips",
        "description": "Ride-hailing, directions, and fare talk.",
        "phrases": [
            phrase("item-l2-cab-booked", "ಕ್ಯಾಬ್ ಬುಕ್ ಮಾಡಿದ್ದೀನಿ", "kyāb buk māḍiddīni", "I booked a cab"),
            phrase("item-l2-pickup-point", "ಪಿಕಪ್ ಪಾಯಿಂಟ್ ಇಲ್ಲಿ", "pikap pāyiṇṭ illi", "Pickup point is here"),
            phrase("item-l2-traffic-heavy", "ಟ್ರಾಫಿಕ್ ತುಂಬಾ ಇದೆ", "ṭrāphik tumba ide", "Traffic is heavy"),
            phrase("item-l2-faster-route", "ಬೇಗದ ರಸ್ತೆ ಹೋಗಿ", "bēgada raste hōgi", "Take the faster route", register="formal"),
            phrase("item-l2-meter-on", "ಮೀಟರ್ ಆನ್ ಮಾಡಿ", "mīṭar ān māḍi", "Turn the meter on", register="formal"),
            phrase("item-l2-stop-here", "ಇಲ್ಲೇ ನಿಲ್ಲಿ", "illē nilli", "Stop here"),
            phrase("item-l2-fare-high", "ಫೇರ್ ಜಾಸ್ತಿ", "phēr jāsti", "Fare is too high"),
            phrase("item-l2-receipt-need", "ರಸೀದಿ ಬೇಕು", "rasīdi bēku", "I need a receipt"),
            phrase("item-l2-ac-on", "ಎಸಿ ಆನ್ ಮಾಡಿ", "esi ān māḍi", "Turn AC on", register="formal"),
            phrase("item-l2-reach-safe", "ಸೇಫ್ ಆಗಿ ಹೋಗಿ", "sēph āgi hōgi", "Go safely", register="formal"),
        ],
        "lessons": [
            lesson(
                "lesson-l2-cab-1", 1, "Pickup & route", "Traffic and directions.",
                ["item-l2-cab-booked", "item-l2-pickup-point", "item-l2-traffic-heavy", "item-l2-faster-route", "item-l2-stop-here"],
                "Getting into a cab.",
                "ಎಲ್ಲಿ ಹೋಗಬೇಕು?", "elli hōgabēku?", "Where to go?",
                "illi nillesi", "Stop here",
                "item-l2-stop-here", "Stop here", "illē _____", ["nilli"],
            ),
            lesson(
                "lesson-l2-cab-2", 2, "Fare & comfort", "Meter, AC, receipt.",
                ["item-l2-meter-on", "item-l2-fare-high", "item-l2-receipt-need", "item-l2-ac-on", "item-l2-reach-safe"],
                "Near the end of the ride.",
                "ಫೇರ್ ಎಷ್ಟು?", "phēr eṣṭu?", "What's the fare?",
                "rasīdi bēku", "Need receipt",
                "item-l2-receipt-need", "Need receipt", "rasīdi _____", ["bēku"],
            ),
        ],
    },
    {
        "id": "unit-l2-07-school",
        "ordinal": 7,
        "title": "Kids & school",
        "description": "Parent–teacher lines and pickup chat.",
        "phrases": [
            phrase("item-l2-parent-meeting", "ಪೇರೆಂಟ್ಸ್ ಮೀಟಿಂಗ್ ಇದೆ", "pēreṇṭs mīṭiṅg ide", "There is a parents' meeting"),
            phrase("item-l2-homework-done", "ಹೋಮ್‌ವರ್ಕ್ ಮುಗಿಸಿದ್ದಾರೆ", "hōm vark mugisiddāre", "They finished homework"),
            phrase("item-l2-pickup-time", "ಇನ್ನೂ ಐದು ನಿಮಿಷ", "innū aidu nimisha", "Five more minutes", tags=["school", "level2"]),
            phrase("item-l2-bus-missed", "ಬಸ್ ಮಿಸ್ ಆಯ್ತು", "bas mis āytu", "Missed the bus"),
            phrase("item-l2-feeling-sick", "ಮಗು ಸ್ವಲ್ಪ ಅಸ್ವಸ್ಥ", "magu svalpa asvastha", "Child is a bit unwell"),
            phrase("item-l2-leave-note", "ಲೀವ್ ನೋಟ್ ಕೊಟ್ಟಿದ್ದೀನಿ", "līv nōṭ koṭṭiddīni", "I gave a leave note"),
            phrase("item-l2-teacher-call", "ಟೀಚರ್ ಕರೆ ಮಾಡ್ತಾರೆ", "ṭīcar kare māḍtāre", "Teacher will call"),
            phrase("item-l2-exam-next-week", "ನೆಕ್ಸ್ಟ್ ವೀಕ್ ಎಗ್ಸಾಂ", "nekst vīk eg sām", "Exam next week"),
            phrase("item-l2-playground", "ಗ್ರೌಂಡ್‌ನಲ್ಲಿ ಆಡ್ತಾರೆ", "grauṇḍ nalli āḍtāre", "They play in the ground"),
            phrase("item-l2-thank-teacher", "ಟೀಚರ್ ಗೆ ಧನ್ಯವಾದ", "ṭīcar ge dhanyavāda", "Thanks to the teacher", register="formal"),
        ],
        "lessons": [
            lesson(
                "lesson-l2-school-1", 1, "At school gate", "Pickup and timing.",
                ["item-l2-pickup-time", "item-l2-bus-missed", "item-l2-playground", "item-l2-feeling-sick", "item-l2-thank-teacher"],
                "Another parent at pickup.",
                "ಮಗು ಬಂದಿದೆಯಾ?", "magu bandideyā?", "Has your child come?",
                "innū aidu nimisha", "Five more minutes",
                "item-l2-pickup-time", "Five more minutes", "innū aidu _____", ["nimisha"],
            ),
            lesson(
                "lesson-l2-school-2", 2, "Teacher updates", "Meetings, homework, exams.",
                ["item-l2-parent-meeting", "item-l2-homework-done", "item-l2-leave-note", "item-l2-teacher-call", "item-l2-exam-next-week"],
                "Quick chat with teacher.",
                "ಹೋಮ್‌ವರ್ಕ್ ಆಯ್ತಾ?", "hōm vark āytā?", "Homework done?",
                "mugisiddāre", "They finished",
                "item-l2-homework-done", "Finished homework", "hōm vark _____", ["mugisiddāre"],
            ),
        ],
    },
    {
        "id": "unit-l2-08-etiquette",
        "ordinal": 8,
        "title": "Etiquette & register",
        "description": "nimma/neenu, soft refusals, and Bengaluru politeness.",
        "phrases": [
            phrase("item-l2-nimma-peru", "ನಿಮ್ಮ ಹೆಸರು ಏನು?", "nimma hesaru ēnu?", "What is your name? (formal)", register="formal", note="Use with elders or strangers."),
            phrase("item-l2-neenu-barta", "ನೀನು ಬರ್ತಿಯಾ?", "nīnu bartiyā?", "Will you come? (informal)", register="informal", note="Close friends only."),
            phrase("item-l2-nimma-manaige", "ನಿಮ್ಮ ಮನೆಗೆ ಬರೋಣ", "nimma manege barōṇa", "Shall we come to your home?", register="formal"),
            phrase("item-l2-soft-no", "ಇದೀಗ ಸಾಧ್ಯ ಇಲ್ಲ", "idīga sādhy illa", "Not possible right now", note="Softer than a blunt 'illa'."),
            phrase("item-l2-maybe-later", "ನೋಡೊಣ, ಸಾಯಂಕಾಲ", "nōḍōṇa, sāyaṅkāla", "Let's see, evening"),
            phrase("item-l2-respect-elder", "ನಿಮಗೆ ಗೌರವ", "nimage gaurava", "Respect to you", register="formal", difficulty=3),
            phrase("item-l2-please-wait", "ಒಂದು ನಿಮಿಷ ಕಾಯಿರಿ", "ondu nimisha kāyiri", "Please wait a minute", register="formal"),
            phrase("item-l2-after-you", "ನೀವು ಮೊದಲು", "nīvu modalu", "You first", register="formal"),
            phrase("item-l2-no-worries", "ಪರವಾಗಿಲ್ಲ", "paravāgilla", "No worries / it's fine"),
            phrase("item-l2-see-you-soon", "ಬೇಗಾ ಸಿಗೋಣ", "bēgā sigōṇa", "See you soon"),
        ],
        "lessons": [
            lesson(
                "lesson-l2-etiq-1", 1, "nimma vs nīnu", "Match formality to the person.",
                ["item-l2-nimma-peru", "item-l2-neenu-barta", "item-l2-nimma-manaige", "item-l2-please-wait", "item-l2-after-you"],
                "Meeting a neighbor's parent.",
                "ಹೆಸರು?", "hesaru?", "Name?",
                "nimma hesaru", "Your name (formal)",
                "item-l2-nimma-peru", "What is your name", "nimma hesaru _____", ["ēnu"],
            ),
            lesson(
                "lesson-l2-etiq-2", 2, "Soft refusals", "Decline without sounding rude.",
                ["item-l2-soft-no", "item-l2-maybe-later", "item-l2-respect-elder", "item-l2-no-worries", "item-l2-see-you-soon"],
                "Friend asks you out last minute.",
                "ಇವತ್ತು ಬರುತ್ತಿಯಾ?", "ivattu baruttiyā?", "Coming today?",
                "idīga sādhy illa", "Not possible now",
                "item-l2-soft-no", "Not possible now", "idīga sādhy _____", ["illa"],
            ),
        ],
    },
]


def main() -> None:
    for spec in UNITS:
        unit: UnitSpec = {
            "id": spec["id"],
            "level_id": LEVEL_ID,
            "ordinal": spec["ordinal"],
            "title": spec["title"],
            "description": spec["description"],
            "phrases": spec["phrases"],
            "lessons": spec["lessons"],
        }
        path = UNITS_DIR / f"{spec['id']}.json"
        path.write_text(json.dumps(unit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Wrote {path.name} ({len(spec['phrases'])} phrases)")


if __name__ == "__main__":
    main()