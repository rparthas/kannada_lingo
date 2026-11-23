#!/usr/bin/env python3
"""Regenerate content/curriculum/beginner-path.json from JSON unit specs."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "content" / "curriculum" / "beginner-path.json"

sys.path.insert(0, str(ROOT / "scripts" / "curriculum"))

from assemble import assemble_bundle  # noqa: E402
from load import load_curriculum_data  # noqa: E402


def build() -> dict:
    return assemble_bundle(load_curriculum_data())


def main() -> None:
    bundle = build()
    OUT.write_text(json.dumps(bundle, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        f"Wrote {OUT.name}: {len(bundle['learning_items'])} items, "
        f"{len(bundle['lessons'])} lessons, {len(bundle['exercises'])} exercises "
        f"(v{bundle['content_version']})"
    )


if __name__ == "__main__":
    main()