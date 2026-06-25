#!/usr/bin/env python3
"""Convert reNEET 2026 biology_FINAL.json into NEET MCQ Practice app format.

Usage:
  python3 tools/convert_reneet2026.py
  python3 tools/convert_reneet2026.py --input /path/to/biology_FINAL.json --images /path/to/images
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import sys
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from convert_pearson_md import (  # noqa: E402
    NUMERIC_OPTION_MARKERS,
    clean_text,
    extract_options_by_markers,
    map_option_letter,
    sanitize_option_source,
)

DEFAULT_INPUT = Path("/Users/dr.ajayshukla/rennet2026/biology/biology_FINAL.json")
DEFAULT_IMAGES = Path("/Users/dr.ajayshukla/rennet2026/biology/images")
DEFAULT_MANIFEST = Path("/Users/dr.ajayshukla/rennet2026/biology/biology_images_manifest.json")
OUTPUT = ROOT / "reneet2026_biology.json"

TOPIC = "NEET 2026 Re-Exam"
SUBTOPIC = "reNEET 2026"
TAGS = ["reNEET2026", "2026", "PYQ"]

IMG_SRC = re.compile(r"""<img[^>]+src=["']([^"']+)["'][^>]*/?>""", re.IGNORECASE)
IMG_BLOCK = re.compile(r"<div[^>]*>.*?</div>", re.IGNORECASE | re.DOTALL)
HTML_TAG = re.compile(r"<[^>]+>")
TABLE_ROW = re.compile(r"<tr[^>]*>(.*?)</tr>", re.IGNORECASE | re.DOTALL)
TABLE_CELL = re.compile(r"<t[dh][^>]*>(.*?)</t[dh]>", re.IGNORECASE | re.DOTALL)
CHOOSE_SPLIT = re.compile(
    r"choose the correct answer from the options given below\s*:?",
    re.IGNORECASE,
)

# Known OCR gaps in the integrated FINAL set (code 50 base).
QUESTION_OVERRIDES: dict[int, str] = {
    167: (
        "Which of the following enzymes synthesizes precursor mRNA?\n\n"
        "(1) RNA polymerase II\n\n(2) RNA polymerase III\n\n"
        "(3) DNA polymerase\n\n(4) RNA polymerase I"
    ),
    178: (
        "Which of the following statements are Correct?\n\n"
        "(a) Energy flow from producers to consumers is unidirectional\n\n"
        "(b) Energy pyramid can never be inverted\n\n"
        "(c) Transfer of energy follows the 1% law\n\n"
        "Choose the correct answer from the options given below :\n\n"
        "(1) (a), (b) and (c)\n\n(2) (a) and (b) only\n\n"
        "(3) (a) and (c) only\n\n(4) (b) and (c) only"
    ),
    148: (
        "Match List-I with List-II.\n\n"
        "(A) Excess growth hormone\n(B) Luteinizing hormone\n"
        "(C) Vasopressin\n(D) Oxytocin\n\n"
        "List-I\nList-II\n"
        "(I) Reabsorption of water and electrolytes in kidney\n"
        "(II) Contraction of uterus during child birth\n"
        "(III) Acromegaly\n(IV) Ovulation\n\n"
        "Choose the correct answer from the options given below:\n\n"
        "(1) A-III, B-IV, C-I, D-II\n(2) A-II, B-IV, C-I, D-III\n"
        "(3) A-IV, B-III, C-I, D-II\n(4) A-III, B-IV, C-II, D-I"
    ),
}

# Disputed / bonus items where the FINAL answer key is not a plain 1–4.
ANSWER_OVERRIDES: dict[int, str] = {
    157: "4",  # marked * in paper — option (4) per official errata
}


def table_to_text(html: str) -> str:
    rows: list[str] = []
    for row_html in TABLE_ROW.findall(html):
        cells = [clean_text(unescape(HTML_TAG.sub(" ", cell))) for cell in TABLE_CELL.findall(row_html)]
        cells = [cell for cell in cells if cell and cell.lower() not in {"list-i", "list-ii"}]
        if cells:
            rows.append(" | ".join(cells))
    return "\n".join(rows)


def strip_html_tables(text: str) -> str:
    def replace_table(match: re.Match[str]) -> str:
        converted = table_to_text(match.group(0))
        return f"\n{converted}\n" if converted else "\n"

    return re.sub(r"<table[^>]*>.*?</table>", replace_table, text, flags=re.IGNORECASE | re.DOTALL)


def strip_html(text: str) -> str:
    text = strip_html_tables(text)
    text = IMG_BLOCK.sub(" ", text)
    text = IMG_SRC.sub(" ", text)
    text = re.sub(r"<div[^>]*>|</div>", "\n", text, flags=re.IGNORECASE)
    text = HTML_TAG.sub(" ", text)
    return clean_text(text)


def build_code_to_final_map(items: list[dict]) -> dict[tuple[str, int], int]:
    mapping: dict[tuple[str, int], int] = {}
    for item in items:
        number = int(item.get("number") or 0)
        code = str(item.get("source_code") or "")
        if code:
            mapping[(code, number)] = number
        for alt_code, alt_number in (item.get("also_appears_as") or {}).items():
            mapping[(str(alt_code), int(alt_number))] = number
    return mapping


def build_image_map(
    manifest_path: Path,
    final_items: list[dict],
    images_dir: Path,
) -> dict[int, list[dict]]:
    """Map canonical FINAL question number -> manifest image entries."""
    if not manifest_path.exists():
        return {}

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    code_to_final = build_code_to_final_map(final_items)
    by_final: dict[int, list[dict]] = {}

    for entry in manifest.get("images", []):
        code = str(entry.get("code") or "")
        question = int(entry.get("question") or 0)
        final_num = code_to_final.get((code, question))
        if not final_num and code == "50":
            final_num = question
        if not final_num:
            continue
        filename = entry.get("filename") or Path(entry.get("local_path", "")).name
        path = images_dir / filename
        by_final.setdefault(final_num, []).append({**entry, "filename": filename, "path": path})

    return by_final


def pick_image_entry(entries: list[dict], source_code: str, images_dir: Path) -> dict | None:
    if not entries:
        return None

    usable = [entry for entry in entries if entry["path"].exists()]
    if not usable:
        return None

    for entry in usable:
        if str(entry.get("code") or "") == source_code:
            return entry

    return max(usable, key=lambda entry: entry["path"].stat().st_size)


def split_stem_and_options(text: str) -> tuple[str, dict[str, str]]:
    text = strip_html_tables(text)
    choose = CHOOSE_SPLIT.search(text)
    option_block = text[choose.end() :] if choose else text
    stem_source = text[: choose.start()] if choose else text

    # Do not run sanitize_option_source on the option block: it rewrites (1)–(4)
    # to {1}–{4} when statement markers (a)–(d) appear inside option text.
    matches = list(NUMERIC_OPTION_MARKERS.finditer(option_block))
    if len(matches) < 4:
        matches = list(NUMERIC_OPTION_MARKERS.finditer(text))
        stem_source = text
        option_block = text

    options = extract_options_by_markers(option_block if len(matches) >= 4 else text, matches)
    if len(options) < 4:
        return "", {}

    if choose:
        stem = strip_html(stem_source)
    else:
        stem_end = text.find(matches[0].group(0))
        stem = strip_html(text[:stem_end])

    return stem, options


def parse_answer(raw: str, status: str) -> tuple[str, list[str]]:
    extra_tags: list[str] = []
    value = (raw or "").strip()
    if status == "bonus_or_multiple":
        extra_tags.append("bonus")
    if value in {"", "*"}:
        return "", extra_tags
    if "/" in value:
        parts = [part.strip().rstrip("*") for part in value.split("/") if part.strip()]
        letters = [map_option_letter(part) for part in parts if map_option_letter(part)]
        if letters:
            extra_tags.append("multiple-answers")
            return letters[0] or "", extra_tags
    letter = map_option_letter(value.rstrip("*"))
    return letter or "", extra_tags


def clean_solution(text: str) -> tuple[str, str]:
    image_path = ""
    for match in IMG_SRC.finditer(text or ""):
        image_path = match.group(1)
        break

    cleaned = text or ""
    cleaned = re.sub(r"^#+\s*", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"^Answer\s*\([^)]+\)\s*", "", cleaned, flags=re.IGNORECASE | re.MULTILINE)
    cleaned = re.sub(r"^Sol\.\s*", "", cleaned, flags=re.IGNORECASE | re.MULTILINE)
    cleaned = strip_html(cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    return cleaned, image_path


def load_image_data_url(images_dir: Path, relative_path: str) -> str:
    if not relative_path:
        return ""
    path = images_dir / Path(relative_path).name
    if not path.exists():
        return ""
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/jpeg;base64,{data}"


def image_fields(
    number: int,
    source_code: str,
    question_md: str,
    solution_md: str,
    item_images: list[dict],
    image_map: dict[int, list[dict]],
    images_dir: Path,
) -> tuple[str, str]:
    """Return (questionImage, explanationImage) as data URLs."""
    question_image = ""
    explanation_image = ""

    manifest_entries = image_map.get(number, [])
    picked = pick_image_entry(manifest_entries, source_code, images_dir)

    for rel in IMG_SRC.findall(question_md or ""):
        question_image = load_image_data_url(images_dir, rel)
        if question_image:
            break

    solution_rel = ""
    for rel in IMG_SRC.findall(solution_md or ""):
        solution_rel = rel
        break
    if not solution_rel and item_images:
        solution_rel = item_images[0].get("local_path") or item_images[0].get("filename") or ""
    if picked and not solution_rel:
        solution_rel = picked.get("filename") or ""

    explanation_image = load_image_data_url(images_dir, solution_rel)
    if not explanation_image and picked:
        explanation_image = load_image_data_url(images_dir, picked["filename"])

    if picked:
        context = (picked.get("context") or "solution").lower()
        if context == "question" and not question_image:
            question_image = load_image_data_url(images_dir, picked["filename"])
        elif context == "solution" and not explanation_image:
            explanation_image = load_image_data_url(images_dir, picked["filename"])

    return question_image, explanation_image


def convert_item(
    item: dict,
    images_dir: Path,
    image_map: dict[int, list[dict]],
) -> dict | None:
    number = int(item.get("number") or 0)
    question_md = QUESTION_OVERRIDES.get(number, item.get("question_md") or "")
    stem, options = split_stem_and_options(question_md)
    if not stem or len(options) < 4:
        return None

    answer, extra_tags = parse_answer(item.get("answer") or "", item.get("answer_status") or "single")
    if not answer and number in ANSWER_OVERRIDES:
        answer, override_tags = parse_answer(ANSWER_OVERRIDES[number], "single")
        extra_tags.extend(override_tags)
    if not answer:
        return None

    explanation, _ = clean_solution(item.get("solution_md") or "")
    source_code = str(item.get("source_code") or "")
    question_image, explanation_image = image_fields(
        number,
        source_code,
        question_md,
        item.get("solution_md") or "",
        item.get("images") or [],
        image_map,
        images_dir,
    )

    ordered = [options[letter] for letter in "ABCD"]
    tags = TAGS + extra_tags
    if item.get("answer_status") == "bonus_or_multiple":
        tags.append("bonus_or_multiple")

    return {
        "id": f"reneet2026_bio_{number}",
        "question": stem,
        "option_a": ordered[0],
        "option_b": ordered[1],
        "option_c": ordered[2],
        "option_d": ordered[3],
        "options": ordered,
        "answer": answer,
        "explanation": explanation,
        "why_wrong_a": "",
        "why_wrong_b": "",
        "why_wrong_c": "",
        "why_wrong_d": "",
        "subject": "Biology",
        "topic": TOPIC,
        "subtopic": SUBTOPIC,
        "tags": tags,
        "questionImage": question_image,
        "explanationImage": explanation_image,
        "source_question_number": number,
        "source_code": source_code,
    }


def convert_file(input_path: Path, images_dir: Path, manifest_path: Path) -> list[dict]:
    data = json.loads(input_path.read_text(encoding="utf-8"))
    items = data.get("questions", data if isinstance(data, list) else [])
    image_map = build_image_map(manifest_path, items, images_dir)
    converted: list[dict] = []
    skipped: list[int] = []

    for item in items:
        row = convert_item(item, images_dir, image_map)
        if row:
            converted.append(row)
        else:
            skipped.append(int(item.get("number") or 0))

    if skipped:
        print(f"Skipped {len(skipped)} questions: {skipped}", file=sys.stderr)

    with_images = sum(
        1 for row in converted if row.get("questionImage") or row.get("explanationImage")
    )
    print(f"Attached images to {with_images} questions", file=sys.stderr)
    return converted


def copy_images(images_dir: Path, dest_dir: Path) -> int:
    if not images_dir.exists():
        return 0
    dest_dir.mkdir(parents=True, exist_ok=True)
    copied = 0
    for path in sorted(images_dir.glob("*.jpg")):
        target = dest_dir / path.name
        if not target.exists() or target.stat().st_size != path.stat().st_size:
            target.write_bytes(path.read_bytes())
        copied += 1
    return copied


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert reNEET 2026 biology JSON for NEET MCQ Practice")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--images", type=Path, default=DEFAULT_IMAGES)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--copy-images-to", type=Path, default=ROOT / "images" / "reneet2026")
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Input not found: {args.input}", file=sys.stderr)
        return 1

    copied = copy_images(args.images, args.copy_images_to)
    if copied:
        print(f"Copied {copied} images to {args.copy_images_to}", file=sys.stderr)

    questions = convert_file(args.input, args.images, args.manifest)
    payload = {
        "app": "NEET MCQ Practice",
        "source": "reNEET 2026 Biology",
        "questionCount": len(questions),
        "questions": questions,
    }
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {args.output} ({len(questions)} questions)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
