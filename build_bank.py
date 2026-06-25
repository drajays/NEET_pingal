#!/usr/bin/env python3
"""Merge Vol I + Vol II JSON into one sanitized bank.json for the app."""

from __future__ import annotations

import csv
import json
import re
import sys
import time
import uuid
from pathlib import Path

COPYRIGHT_TAG_MARKERS = ("pearson",)
COPYRIGHT_FIELDS = (
    "source",
    "source_question_number",
    "source_section",
    "question_image_url",
    "explanation_image_url",
)

# Normalize chapter names from supplementary sources to the canonical
# Pearson chapter titles so every question merges into the 38-chapter tree.
TOPIC_ALIASES = {
    "Animal Kingdom": "Animal Classification",
    "Sexual Reproduction in Flowering Plants": "Reproduction in Flowering Plant",
    "Cell-The Unit of Life": "Cell: The Unit of Life",
    "Morphology of Flowering Plants": "Plant Morphology",
    "Human Health and Diseases": "Human Health and Disease",
    "Chemical Coordination and Integration": "Co-ordination and Integration",
    "Structural Organisation in Animals": "Structural Organization in Animals",
    "Biotechnology: Principles and Processes": "Biotechnology Principles and Processes",
    "Neural Control and Coordination": "Neural Control and Co-ordination",
    "Biotechnology and Its Applications": "Biotechnology and Its Application",
    "Biotechnology and its Applications": "Biotechnology and Its Application",
    "Excretory Products and Their Elimination": "Products and Their Elimination",
    "The Living World": "Living World",
}


def load_questions(path: Path) -> list:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    return data.get("questions", [])


def load_csv_questions(path: Path) -> list:
    questions: list = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            question = (row.get("question") or "").strip()
            if not question:
                continue
            tags = row.get("tags") or ""
            if isinstance(tags, str):
                tags = [part.strip() for part in tags.split(";") if part.strip()]
            questions.append(
                {
                    "id": row.get("id") or f"csv_{uuid.uuid4().hex[:10]}",
                    "question": question,
                    "option_a": (row.get("option_a") or "").strip(),
                    "option_b": (row.get("option_b") or "").strip(),
                    "option_c": (row.get("option_c") or "").strip(),
                    "option_d": (row.get("option_d") or "").strip(),
                    "answer": (row.get("answer") or "").strip().upper(),
                    "explanation": (row.get("explanation") or "").strip(),
                    "why_wrong_a": (row.get("why_wrong_a") or "").strip(),
                    "why_wrong_b": (row.get("why_wrong_b") or "").strip(),
                    "why_wrong_c": (row.get("why_wrong_c") or "").strip(),
                    "why_wrong_d": (row.get("why_wrong_d") or "").strip(),
                    "subject": (row.get("subject") or "Biology").strip(),
                    "topic": (row.get("topic") or "").strip(),
                    "subtopic": (row.get("subtopic") or "").strip(),
                    "tags": tags,
                }
            )
    return questions


def load_chapter_dir(directory: Path) -> list:
    """Load NCERT chapter-wise MCQ files (one JSON array per chapter).

    Each item looks like:
        {"chapter": "Chapter 1: The Living World", "question": ...,
         "options": {"A": ..., "B": ..., "C": ..., "D": ...},
         "correct_answer": "C", "explanation": ...}
    """
    questions: list = []
    for path in sorted(directory.glob("chapter_*_mcqs.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        items = data if isinstance(data, list) else data.get("questions", [])
        for item in items:
            opts = item.get("options") or {}
            chapter = (item.get("chapter") or "").strip()
            topic = re.sub(r"^\s*Chapter\s+\d+\s*:\s*", "", chapter).strip()
            questions.append(
                {
                    "id": f"ncert_{uuid.uuid4().hex[:10]}",
                    "question": (item.get("question") or "").strip(),
                    "option_a": str(opts.get("A") or "").strip(),
                    "option_b": str(opts.get("B") or "").strip(),
                    "option_c": str(opts.get("C") or "").strip(),
                    "option_d": str(opts.get("D") or "").strip(),
                    "answer": (item.get("correct_answer") or "").strip().upper(),
                    "explanation": (item.get("explanation") or "").strip(),
                    "subject": "Biology",
                    "topic": topic,
                    "subtopic": "NCERT",
                    "tags": ["NCERT"],
                }
            )
    return questions


def is_gradeable(item: dict) -> bool:
    """A usable MCQ needs a valid answer key and four complete options."""
    if (item.get("answer") or "").strip().upper() not in ("A", "B", "C", "D"):
        return False
    return all((item.get(f"option_{o}") or "").strip() for o in ("a", "b", "c", "d"))


def sanitize_question(item: dict) -> dict:
    cleaned = dict(item)
    for field in COPYRIGHT_FIELDS:
        cleaned.pop(field, None)

    topic = (cleaned.get("topic") or "").strip()
    cleaned["topic"] = TOPIC_ALIASES.get(topic, topic)

    tags = cleaned.get("tags") or []
    if isinstance(tags, str):
        tags = [part.strip() for part in tags.split(";") if part.strip()]
    cleaned["tags"] = [
        tag
        for tag in tags
        if tag and not any(marker in tag.lower() for marker in COPYRIGHT_TAG_MARKERS)
    ]
    return cleaned


def main() -> int:
    root = Path(__file__).parent
    sources = [
        root / "pearson_biology_vol1.json",
        root / "pearson_biology_vol2.json",
        root / "recovered_questions.json",
    ]
    extra_csv = root / "neet_biology_questions.csv"
    reneet_json = root / "reneet2026_biology.json"
    chapter_dirs = [
        root / "ncert_mcqs" / "bio11",
        root / "ncert_mcqs" / "bio12",
    ]
    output = root / "bank.json"

    missing = [p for p in sources if not p.exists()]
    if missing:
        print("Missing source files:", ", ".join(str(p) for p in missing), file=sys.stderr)
        print("Run convert_pearson_md.py for each volume first.", file=sys.stderr)
        return 1

    merged: list = []
    seen: set[str] = set()
    duplicates = 0
    skipped_invalid = 0

    for path in sources:
        for item in load_questions(path):
            key = (item.get("question") or "").strip().lower()
            if not key or key in seen:
                duplicates += 1
                continue
            cleaned = sanitize_question(item)
            if not is_gradeable(cleaned):
                skipped_invalid += 1
                continue
            seen.add(key)
            merged.append(cleaned)

    if extra_csv.exists():
        csv_added = 0
        for item in load_csv_questions(extra_csv):
            key = (item.get("question") or "").strip().lower()
            if not key or key in seen:
                duplicates += 1
                continue
            cleaned = sanitize_question(item)
            if not is_gradeable(cleaned):
                skipped_invalid += 1
                continue
            seen.add(key)
            merged.append(cleaned)
            csv_added += 1
        if csv_added:
            print(f"Added {csv_added} unique questions from {extra_csv.name}")

    if reneet_json.exists():
        # reNEET 2026 is a fixed official paper (Q91-180). Keep the full set even
        # when generic stems (e.g. "Which of the following is incorrect?") collide
        # with the text-based dedup used for the rest of the bank. Dedup by id only.
        reneet_added = 0
        seen_ids = {q.get("id") for q in merged}
        for item in load_questions(reneet_json):
            qid = item.get("id")
            if qid in seen_ids:
                duplicates += 1
                continue
            cleaned = sanitize_question(item)
            if not is_gradeable(cleaned):
                skipped_invalid += 1
                continue
            key = (item.get("question") or "").strip().lower()
            if key:
                seen.add(key)
            seen_ids.add(qid)
            merged.append(cleaned)
            reneet_added += 1
        if reneet_added:
            print(f"Added {reneet_added} unique questions from {reneet_json.name}")

    for directory in chapter_dirs:
        if not directory.exists():
            continue
        ncert_added = 0
        for item in load_chapter_dir(directory):
            key = (item.get("question") or "").strip().lower()
            if not key or key in seen:
                duplicates += 1
                continue
            cleaned = sanitize_question(item)
            if not is_gradeable(cleaned):
                skipped_invalid += 1
                continue
            seen.add(key)
            merged.append(cleaned)
            ncert_added += 1
        if ncert_added:
            print(f"Added {ncert_added} unique questions from {directory.name}")

    payload = {
        "app": "NEET MCQ Practice",
        "version": 1,
        "updatedAt": int(time.time() * 1000),
        "questionCount": len(merged),
        "questions": merged,
    }
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Built {output}")
    print(f"Questions: {len(merged)}")
    print(f"Duplicates skipped: {duplicates}")
    print(f"Invalid (no answer / incomplete options) skipped: {skipped_invalid}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
