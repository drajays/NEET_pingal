#!/usr/bin/env python3
"""Merge chapter notes + MCQ links into notes.json / note_links.json and verify."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def norm_key(q: str) -> str:
    return re.sub(r"\s+", " ", (q or "")).strip().lower()


def classify_item(item: dict, ruleset: list[tuple[str, str]], default: str) -> str:
    ans = (item.get("answer") or "").lower()
    at = item.get(f"option_{ans}", "") if ans in "abcd" else ""
    text = "\n".join(
        [item.get("question", ""), at, item.get("explanation", "")]
    ).lower()
    for sec, pat in ruleset:
        if re.search(pat, text):
            return sec
    return default


def build_links(questions: list[dict], ruleset: list[tuple[str, str]], default: str) -> dict[str, str]:
    links: dict[str, str] = {}
    for q in questions:
        links[norm_key(q["question"])] = classify_item(q, ruleset, default)
    return links


def upsert_chapter_notes(notes: dict, chapter: dict) -> None:
    notes["chapters"] = [c for c in notes["chapters"] if c["id"] != chapter["id"]] + [chapter]


def upsert_chapter_links(note_links: dict, cid: str, topic: str, links: dict[str, str]) -> None:
    note_links["chapters"] = [c for c in note_links["chapters"] if c["id"] != cid]
    note_links["chapters"].append(
        {"id": cid, "topic": topic, "linkCount": len(links), "links": links}
    )


def load_bank(topic: str) -> list[dict]:
    bank = json.loads((ROOT / "bank.json").read_text(encoding="utf-8"))
    return [q for q in bank["questions"] if q.get("topic") == topic]


def verify_all() -> list[str]:
    bank = json.loads((ROOT / "bank.json").read_text(encoding="utf-8"))
    notes = json.loads((ROOT / "notes.json").read_text(encoding="utf-8"))
    nl = json.loads((ROOT / "note_links.json").read_text(encoding="utf-8"))
    errors: list[str] = []
    notes_by_id = {c["id"]: c for c in notes["chapters"]}
    for ch in nl["chapters"]:
        qs = [q for q in bank["questions"] if q.get("topic") == ch["topic"]]
        sec_ids = {s["id"] for s in notes_by_id.get(ch["id"], {}).get("sections", [])}
        missing = sum(1 for q in qs if norm_key(q["question"]) not in ch["links"])
        orphan = sorted({v for v in ch["links"].values() if v not in sec_ids})
        if missing or orphan:
            errors.append(f"FAIL {ch['id']} missing={missing} orphan={orphan[:5]}")
        if ch["linkCount"] != len(ch["links"]):
            errors.append(f"FAIL {ch['id']} linkCount mismatch {ch['linkCount']} vs {len(ch['links'])}")
    return errors


def print_distribution(links: dict[str, str]) -> None:
    for sec, cnt in Counter(links.values()).most_common():
        print(f"  {cnt:4d} {sec}")


if __name__ == "__main__":
    errs = verify_all()
    if errs:
        for e in errs:
            print(e)
        sys.exit(1)
    print("All linked chapters pass verification.")
