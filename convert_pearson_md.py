#!/usr/bin/env python3
"""Convert Pearson NEET OCR markdown into NEET MCQ Practice app import files.

Uses the PaddleOCR page JSON (when provided) to repair single-line question blocks
and resolve image URLs, while the markdown file supplies chapter structure and
answer keys.

Outputs:
  - JSON envelope (recommended import — supports image URLs in tags)
  - CSV (text fields for quick import)

Usage:
  python3 convert_pearson_md.py
  python3 convert_pearson_md.py --input path/to/file.md --paddle-json path/to/file.json
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import uuid
from dataclasses import dataclass, field
from html import unescape
from pathlib import Path
from typing import Dict, List, Optional, Tuple

CHAPTER_HEADERS_VOL1 = [
    "Living World",
    "Biological Classification",
    "Plant Kingdom",
    "Animal Classification",
    "Plant Morphology",
    "Anatomy of Flowering Plants",
    "Structural Organization in Animals",
    "Cell: The Unit of Life",
    "Biomolecules",
    "Cell Cycle and Cell Division",
    "Transport in Plants",
    "Mineral Nutrition",
    "Photosynthesis in Higher Plants",
    "Respiration in Plants",
    "Plant Growth and Development",
    "Digestion and Absorption",
    "Breathing and Exchange of Gases",
    "Body Fluids and Circulation",
    "Products and Their Elimination",
    "Locomotion and Movement",
    "Neural Control and Co-ordination",
    "Co-ordination and Integration",
]

CHAPTER_HEADERS_VOL2 = [
    "Reproduction in Organisms",
    "Reproduction in Flowering Plant",
    "Human Reproduction",
    "Reproductive Health",
    "Principles of Inheritance and Variation",
    "Molecular Basis of Inheritance",
    "Evolution",
    "Human Health and Disease",
    "Strategies for Enhancement in Food Production",
    "Microbes in Human Welfare",
    "Biotechnology Principles and Processes",
    "Biotechnology and Its Application",
    "Organisms and Populations",
    "Ecosystem",
    "Biodiversity and Conservation",
    "Environmental Issues",
]

CHAPTER_HEADERS_BY_VOLUME = {
    1: CHAPTER_HEADERS_VOL1,
    2: CHAPTER_HEADERS_VOL2,
}

SOURCE_BY_VOLUME = {
    1: "Pearson Objective Biology Vol I 2019",
    2: "Pearson Objective Biology Vol II 2019",
}

SECTION_ALIASES = {
    "practice questions": "practice",
    "assertion and reason questions": "assertion",
    "previous year questions": "pyq",
    "ncert exemplar questions": "ncert",
}

TAG_BY_SECTION = {
    "practice": ["Pearson 2019", "Practice"],
    "assertion": ["Pearson 2019", "Assertion-Reason"],
    "pyq": ["Pearson 2019", "PYQ"],
    "ncert": ["Pearson 2019", "NCERT Exemplar"],
}

DEFAULT_ASSERTION_OPTIONS = {
    "A": "Both assertion and reason are true and reason is the correct explanation of assertion.",
    "B": "Both assertion and reason are true but reason is not the correct explanation of assertion.",
    "C": "Assertion is true but reason is false.",
    "D": "Both assertion and reason are false.",
}

OPTION_MARKERS = re.compile(
    r"\(\s*([a-d])\s*\)\s*",
    re.IGNORECASE,
)
NUMERIC_OPTION_MARKERS = re.compile(
    r"\(\s*([1-4])\s*\)\s*",
    re.IGNORECASE,
)
QUESTION_START = re.compile(r"^#{0,2}(\d+)\.\s*(.*)$")
ANSWER_CELL = re.compile(r"(\d+)\.\s*\(\s*([a-d])\s*\)", re.IGNORECASE)
ANSWER_TABLE_HINT = re.compile(
    r"Answer\s*Keys|Practice\s*Questions|Previous\s*Year|NCERT\s*Exemplar|Assertion\s*and\s*Reason",
    re.IGNORECASE,
)
IMG_SRC = re.compile(r"""<img[^>]+src=["']([^"']+)["']""", re.IGNORECASE)
EXAM_TAG = re.compile(
    r"\[(?:NEET|AIPMT|AIIMS)[^\]]*?(?:\d{4})?[^\]]*\]",
    re.IGNORECASE,
)
WHITESPACE = re.compile(r"\s+")
NESTED_BOTH_OPTIONS = re.compile(
    r"\bBoth\s*\(([a-d])\)\s*and\s*\(([a-d])\)",
    re.IGNORECASE,
)
NESTED_PAIR_OPTIONS = re.compile(
    r"\(([a-d])\)\s*and\s*\(([a-d])\)",
    re.IGNORECASE,
)
SUSPICIOUS_OPTION = re.compile(
    r"^(and|or|both|only|in|of|the|a|an|\d+)$",
    re.IGNORECASE,
)


@dataclass
class RawQuestion:
    number: int
    section: str
    chapter: str
    stem_lines: List[str] = field(default_factory=list)
    option_lines: List[str] = field(default_factory=list)
    image_urls: List[str] = field(default_factory=list)
    exam_refs: List[str] = field(default_factory=list)

    def stem_text(self) -> str:
        return WHITESPACE.sub(" ", " ".join(self.stem_lines)).strip()

    def options_blob(self) -> str:
        return " ".join(self.option_lines)


def clean_text(value: str) -> str:
    value = unescape(value or "")
    value = value.replace("\u2018", "'").replace("\u2019", "'")
    value = value.replace("\u201c", '"').replace("\u201d", '"')
    value = value.replace("\u2013", "-").replace("\u2014", "-")
    value = WHITESPACE.sub(" ", value).strip()
    return value


def sanitize_option_source(text: str) -> str:
    """Prevent nested markers like 'Both (a) and (b)' from breaking option parsing."""
    text = clean_text(text)
    text = NESTED_BOTH_OPTIONS.sub(r"Both \1 and \2", text)
    text = NESTED_PAIR_OPTIONS.sub(r"\1 and \2", text)
    # Statement lists like (1)...(4) before real options (a)...(d).
    if re.search(r"\(\s*[a-d]\s*\)", text, re.IGNORECASE) and re.search(r"\(\s*[1-4]\s*\)", text):
        text = re.sub(r"\(\s*([1-4])\s*\)", r"{\1}", text)
    return text


def options_are_suspicious(options: Dict[str, str]) -> bool:
    if len(options) < 4:
        return True
    for letter in "ABCD":
        value = options.get(letter, "")
        if not value or len(value) < 2 or SUSPICIOUS_OPTION.match(value.strip()):
            return True
    return False


def prettify_option_text(text: str) -> str:
    return re.sub(r"\{(\d)\}", r"(\1)", text)


def options_quality_score(options: Dict[str, str]) -> int:
    if len(options) < 4:
        return 0
    score = 0
    for letter in "ABCD":
        value = options.get(letter, "")
        if not value:
            return 0
        score += min(len(value), 40)
        if SUSPICIOUS_OPTION.match(value.strip()):
            score -= 20
    return score


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_")


def map_option_letter(letter: str) -> Optional[str]:
    letter = letter.lower()
    if letter in "abcd":
        return letter.upper()
    if letter in "1234":
        return "ABCD"[int(letter) - 1]
    return None


def extract_options_by_markers(text: str, matches: List[re.Match[str]]) -> Dict[str, str]:
    options: Dict[str, str] = {}
    for index, match in enumerate(matches):
        token = match.group(1)
        letter = map_option_letter(token)
        if not letter:
            continue
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        value = clean_text(text[start:end])
        if value:
            options[letter] = value
    return options


def extract_options_positional(text: str) -> Dict[str, str]:
    """Map the first four option markers to A–D by order (handles OCR duplicate/wrong letters)."""
    text = sanitize_option_source(text)
    if not text:
        return {}

    matches = list(OPTION_MARKERS.finditer(text))
    if len(matches) < 4:
        matches = list(NUMERIC_OPTION_MARKERS.finditer(text))
    if len(matches) < 4:
        return {}

    options: Dict[str, str] = {}
    for index, match in enumerate(matches[:4]):
        letter = "ABCD"[index]
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        value = clean_text(text[start:end])
        if value:
            options[letter] = value
    return options if len(options) == 4 else {}


def extract_options(text: str) -> Dict[str, str]:
    text = sanitize_option_source(text)
    if not text:
        return {}

    matches = list(OPTION_MARKERS.finditer(text))
    if not matches:
        matches = list(NUMERIC_OPTION_MARKERS.finditer(text))

    return extract_options_by_markers(text, matches)


def is_noise_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return True
    if stripped.startswith("<div") or stripped.startswith("</div"):
        return True
    if stripped.startswith("<table") or stripped.startswith("</table"):
        return True
    if stripped.startswith("<tr") or stripped.startswith("</tr"):
        return True
    if stripped.startswith("<td") or stripped.startswith("</td"):
        return True
    if stripped.startswith("!["):
        return True
    if stripped in {"##### Options", "Options"}:
        return True
    if stripped.startswith("#####") and "underline" in stripped:
        return True
    if stripped.startswith("####") and "PRACTICE" not in stripped.upper():
        if any(
            key in stripped.upper()
            for key in (
                "STUDENTS NOTE",
                "PREVIOUS YEAR",
                "NCERT EXEMPLAR",
                "ASSERTION AND REASON",
                "KINGDOM",
                "DIVERSITY",
            )
        ):
            return False
        if stripped.startswith("####"):
            return True
    return False


def detect_section_header(line: str) -> Optional[str]:
    upper = line.strip().upper()
    if "PREVIOUS YEAR" in upper and "QUESTION" in upper:
        return "pyq"
    if "NCERT EXEMPLAR" in upper and "QUESTION" in upper:
        return "ncert"
    if "ASSERTION AND REASON" in upper:
        return "assertion"
    if "PRACTICE QUESTION" in upper:
        return "practice"
    return None


def get_chapter_headers(volume: int) -> List[str]:
    headers = CHAPTER_HEADERS_BY_VOLUME.get(volume)
    if not headers:
        raise ValueError(f"Unsupported volume: {volume}. Use 1 or 2.")
    return headers


def detect_chapter_header(line: str, chapter_headers: List[str]) -> Optional[str]:
    stripped = line.strip()
    if stripped.startswith("# "):
        title = stripped[2:].strip()
        if title in chapter_headers:
            return title
    return None


def resolve_markdown_images(text: str, image_map: Dict[str, str]) -> str:
    if not image_map:
        return text

    def replace_src(match: re.Match[str]) -> str:
        src = match.group(1)
        resolved = image_map.get(src, src)
        return match.group(0).replace(src, resolved)

    return IMG_SRC.sub(replace_src, text)


def load_paddle_pages(path: Path) -> List[dict]:
    data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    if not isinstance(data, list):
        raise ValueError("PaddleOCR JSON must be a list of page objects.")
    return data


def build_markdown_from_paddle(pages: List[dict]) -> str:
    chunks: List[str] = []
    for page in pages:
        markdown = page.get("markdown", {})
        if not isinstance(markdown, dict):
            continue
        text = markdown.get("text", "")
        if not text:
            continue
        image_map = markdown.get("images", {})
        chunks.append(resolve_markdown_images(text, image_map))
    return "\n\n".join(chunks)


def raw_from_paddle_text(content: str, chapter: str, section: str) -> Optional[RawQuestion]:
    flat = sanitize_option_source(content.replace("\n", " "))
    match = re.match(r"^(\d+)\.\s*(.*)$", flat)
    if not match:
        return None

    number = int(match.group(1))
    body = match.group(2).strip()
    section_name = section
    if "Assertion:" in body:
        section_name = "assertion"

    options = extract_options(flat)
    first_option = OPTION_MARKERS.search(flat)
    stem = clean_text(flat[: first_option.start()]) if first_option else body
    stem = re.sub(r"^(\d+)\.\s*", "", stem).strip()

    raw = RawQuestion(
        number=number,
        section=section_name,
        chapter=chapter,
        stem_lines=[stem] if stem else [],
    )
    if options:
        raw.option_lines = [flat[first_option.start() :]] if first_option else []
    return raw


def build_paddle_question_index(
    pages: List[dict],
    chapter_headers: List[str],
) -> Dict[Tuple[str, str, int], RawQuestion]:
    index: Dict[Tuple[str, str, int], RawQuestion] = {}
    current_chapter: Optional[str] = None
    current_section = "practice"
    pending_chapter_prefix: Optional[str] = None

    def apply_chapter_line(line: str) -> None:
        nonlocal current_chapter, pending_chapter_prefix
        stripped = line.strip()
        if not stripped:
            return
        if stripped == "# Strategies for":
            pending_chapter_prefix = "Strategies for"
            return
        if pending_chapter_prefix and stripped == "# Enhancement in Food Production":
            merged = f"{pending_chapter_prefix} Enhancement in Food Production"
            if merged in chapter_headers:
                current_chapter = merged
            pending_chapter_prefix = None
            return
        if pending_chapter_prefix and stripped.startswith("# "):
            pending_chapter_prefix = None
        chapter = detect_chapter_header(line, chapter_headers)
        if chapter:
            current_chapter = chapter

    for page in pages:
        blocks = page.get("prunedResult", {}).get("parsing_res_list", [])
        blocks = sorted(blocks, key=lambda item: item.get("block_id", 0))

        for block in blocks:
            label = block.get("block_label", "")
            content = block.get("block_content", "")
            if not content:
                continue

            if label in {"doc_title", "paragraph_title"}:
                apply_chapter_line(content)
                section = detect_section_header(content)
                if section:
                    current_section = section
                continue

            if label != "text" or not current_chapter:
                continue

            apply_chapter_line(content)
            if content.strip().startswith("# "):
                continue

            raw = raw_from_paddle_text(content, current_chapter, current_section)
            if not raw:
                continue

            key = (raw.chapter, raw.section, raw.number)
            existing = index.get(key)
            if not existing:
                index[key] = raw
                continue

            existing_options = extract_options(existing.options_blob())
            candidate_options = extract_options(raw.options_blob())
            if options_quality_score(candidate_options) > options_quality_score(existing_options):
                index[key] = raw

    return index


def merge_raw_with_paddle(raw: RawQuestion, paddle_index: Dict[Tuple[str, str, int], RawQuestion]) -> RawQuestion:
    paddle_raw = paddle_index.get((raw.chapter, raw.section, raw.number))
    if not paddle_raw:
        return raw

    markdown_options = extract_options(raw.options_blob() or raw.stem_text())
    paddle_options = extract_options(paddle_raw.options_blob() or paddle_raw.stem_text())

    if not paddle_options:
        return raw
    if options_quality_score(paddle_options) <= options_quality_score(markdown_options):
        return raw

    merged = RawQuestion(
        number=raw.number,
        section=raw.section,
        chapter=raw.chapter,
        stem_lines=list(paddle_raw.stem_lines or raw.stem_lines),
        option_lines=list(paddle_raw.option_lines or raw.option_lines),
        image_urls=list(raw.image_urls),
        exam_refs=list(raw.exam_refs),
    )
    return merged


def find_split_chapter_start(lines: List[str], start: int) -> Optional[Tuple[int, str]]:
    if lines[start].strip() != "# Strategies for":
        return None
    scan = start + 1
    while scan < len(lines) and not lines[scan].strip():
        scan += 1
    if scan < len(lines) and lines[scan].strip() == "# Enhancement in Food Production":
        return start, "Strategies for Enhancement in Food Production"
    return None


def split_chapters(text: str, chapter_headers: List[str]) -> List[Tuple[str, str]]:
    lines = text.splitlines()
    chapter_set = set(chapter_headers)
    indices: Dict[str, int] = {}
    index = 0
    while index < len(lines):
        split_match = find_split_chapter_start(lines, index)
        if split_match and split_match[1] in chapter_set:
            indices[split_match[1]] = split_match[0]
            index += 1
            continue
        stripped = lines[index].strip()
        if stripped.startswith("# "):
            title = stripped[2:].strip()
            if title in chapter_set:
                indices[title] = index
        index += 1

    chapters: List[Tuple[str, str]] = []
    found = [(title, indices[title]) for title in chapter_headers if title in indices]
    found.sort(key=lambda item: item[1])

    for idx, (title, start) in enumerate(found):
        end = found[idx + 1][1] if idx + 1 < len(found) else len(lines)
        chunk = "\n".join(lines[start:end])
        chapters.append((title, chunk))
    return chapters


def find_answer_tables(chunk: str) -> List[str]:
    tables = re.findall(r"<table[^>]*>.*?</table>", chunk, re.IGNORECASE | re.DOTALL)
    answer_tables = []
    for table in tables:
        if not ANSWER_CELL.search(table):
            continue
        if ANSWER_TABLE_HINT.search(table):
            answer_tables.append(table)
        elif answer_tables:
            # OCR sometimes splits one answer key across consecutive tables.
            answer_tables.append(table)
    return answer_tables


def split_questions_and_answer_tables(chunk: str) -> Tuple[str, List[str]]:
    tables = find_answer_tables(chunk)
    if not tables:
        return chunk, []

    first_table = tables[0]
    question_block = chunk.split(first_table, 1)[0]
    # Include any question text that appears before later tables in the same chapter.
    for table in tables[1:]:
        before, _, after = question_block.partition(table)
        if after:
            question_block = before + after
    return question_block, tables


def detect_section_from_row(row_text: str) -> Optional[str]:
    lowered = clean_text(row_text).lower()
    if not lowered or len(lowered) > 120:
        return None
    for alias, section in SECTION_ALIASES.items():
        if alias in lowered:
            return section
    return None


def parse_answer_table(table_html: str) -> Dict[str, Dict[int, str]]:
    blocks: List[Tuple[str, Dict[int, str]]] = []
    current_section = "practice"
    current_answers: Dict[int, str] = {}
    last_number = 0

    def flush_block() -> None:
        nonlocal current_answers, last_number
        if current_answers:
            blocks.append((current_section, current_answers))
        current_answers = {}
        last_number = 0

    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", table_html, re.IGNORECASE | re.DOTALL)
    for row in rows:
        row_text = clean_text(re.sub(r"<[^>]+>", " ", row))
        if not row_text:
            continue

        section = detect_section_from_row(row_text)
        if section:
            flush_block()
            current_section = section
            continue

        matches = ANSWER_CELL.findall(row_text)
        if not matches:
            continue

        for number_text, letter in matches:
            number = int(number_text)
            if last_number and number < last_number:
                flush_block()
                if current_section == "practice":
                    current_section = "assertion"
                elif current_section == "assertion":
                    current_section = "pyq"
                elif current_section == "pyq":
                    current_section = "ncert"

            # OCR sometimes labels the first large answer block as PYQ.
            if current_section == "pyq" and number > 40 and not current_answers:
                current_section = "practice"

            current_answers[number] = letter.upper()
            last_number = number

    flush_block()

    # OCR quirk: the first answer block is sometimes mislabeled PYQ but is actually practice.
    fixed_blocks: List[Tuple[str, Dict[int, str]]] = []
    for index, (section, answers) in enumerate(blocks):
        if (
            section == "pyq"
            and index == 0
            and answers
            and max(answers) > 100
        ):
            fixed_blocks.append(("practice", answers))
        else:
            fixed_blocks.append((section, answers))

    merged: Dict[str, Dict[int, str]] = {}
    for section, answers in fixed_blocks:
        merged.setdefault(section, {}).update(answers)
    return merged


def parse_answer_tables(tables: List[str]) -> Dict[str, Dict[int, str]]:
    merged: Dict[str, Dict[int, str]] = {}
    for table in tables:
        parsed = parse_answer_table(table)
        for section, answers in parsed.items():
            merged.setdefault(section, {}).update(answers)
    return merged


def parse_questions_block(chapter: str, block: str) -> Tuple[List[RawQuestion], Dict[str, str]]:
    questions: List[RawQuestion] = []
    current: Optional[RawQuestion] = None
    current_section = "practice"
    collecting_options = False
    assertion_template: Dict[str, str] = {}
    reading_assertion_template = False
    assertion_preamble_blob = ""

    for raw_line in block.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        section = detect_section_header(line)
        if section:
            if current:
                questions.append(current)
                current = None
            current_section = section
            collecting_options = False
            reading_assertion_template = section == "assertion"
            if section == "assertion":
                assertion_template = {}
                assertion_preamble_blob = ""
            continue

        if is_noise_line(line):
            if current and "<img" in line:
                for url in IMG_SRC.findall(line):
                    current.image_urls.append(url)
            continue

        for url in IMG_SRC.findall(line):
            if current:
                current.image_urls.append(url)
            line = IMG_SRC.sub("", line).strip()
            if not line:
                continue

        exam_refs = EXAM_TAG.findall(line)
        if exam_refs and current:
            current.exam_refs.extend(exam_refs)

        if reading_assertion_template and OPTION_MARKERS.search(line):
            assertion_preamble_blob = f"{assertion_preamble_blob} {line}".strip()
            parsed_template = extract_options(assertion_preamble_blob)
            if parsed_template:
                assertion_template = parsed_template
            if len(assertion_template) >= 4:
                reading_assertion_template = False
            continue

        question_match = QUESTION_START.match(line)
        if question_match:
            number = int(question_match.group(1))
            rest = question_match.group(2).strip()

            if current:
                current_options = extract_options(current.options_blob())
                if len(current_options) < 4 and number < current.number:
                    current.stem_lines.append(line)
                    continue
                questions.append(current)

            if "Assertion:" in rest:
                current_section = "assertion"
                reading_assertion_template = False

            current = RawQuestion(
                number=number,
                section=current_section,
                chapter=chapter,
                stem_lines=[rest] if rest else [],
            )
            collecting_options = bool(extract_options(rest))
            continue

        if not current:
            continue

        inline_options = extract_options(line)
        if inline_options or OPTION_MARKERS.search(line):
            current.option_lines.append(line)
            collecting_options = True
            continue

        if collecting_options and not line.startswith("("):
            # Some OCR wraps long options over multiple lines
            if current.option_lines:
                current.option_lines[-1] += " " + line
            else:
                current.stem_lines.append(line)
            continue

        current.stem_lines.append(line)

    if current:
        questions.append(current)

    if len(assertion_template) < 4:
        assertion_template = dict(DEFAULT_ASSERTION_OPTIONS)

    return questions, assertion_template


def lookup_answer(raw: RawQuestion, answers_by_section: Dict[str, Dict[int, str]]) -> Optional[str]:
    # Direct hit in the question's own section table.
    direct = answers_by_section.get(raw.section, {}).get(raw.number)
    if direct:
        return direct
    # Fallback: Assertion-Reason (and some other) questions are numbered
    # continuously with the chapter's master "practice" answer key, so their
    # answers live there even though they were tagged a different section.
    practice = answers_by_section.get("practice", {})
    if raw.number in practice:
        return practice[raw.number]
    # Last resort: the number appears in exactly one section table.
    hits = {
        answer
        for table in answers_by_section.values()
        for number, answer in table.items()
        if number == raw.number
    }
    if len(hits) == 1:
        return next(iter(hits))
    return None


def finalize_question(
    raw: RawQuestion,
    answer: Optional[str],
    assertion_template: Optional[Dict[str, str]] = None,
    source_label: str = SOURCE_BY_VOLUME[1],
) -> Optional[dict]:
    stem = raw.stem_text()
    if not stem:
        return None

    options = extract_options(raw.options_blob())
    if not options and raw.option_lines:
        options = extract_options(" ".join(raw.option_lines))

    if len(options) < 4:
        merged = extract_options(f"{stem} {raw.options_blob()}")
        if len(merged) >= len(options):
            options = merged

    if len(options) < 4:
        positional = extract_options_positional(raw.options_blob() or " ".join(raw.option_lines))
        if len(positional) >= len(options):
            options = positional

    if len(options) < 4 and raw.section == "assertion":
        template = assertion_template or DEFAULT_ASSERTION_OPTIONS
        options = {letter: template.get(letter, "") for letter in "ABCD"}

    if len(options) < 4:
        return None

    ordered = [prettify_option_text(options.get(letter, "")) for letter in "ABCD"]
    if any(not opt for opt in ordered):
        return None

    answer_letter = answer.upper() if answer else ""
    if answer_letter not in {"A", "B", "C", "D"}:
        return None

    tags = list(TAG_BY_SECTION.get(raw.section, ["Pearson 2019"]))
    for ref in raw.exam_refs:
        year_match = re.search(r"(20\d{2})", ref)
        if year_match:
            tags.append(year_match.group(1))
        if "NEET" in ref.upper():
            tags.append("NEET")
        if "AIPMT" in ref.upper():
            tags.append("AIPMT")

    tags = sorted(set(tags), key=str.lower)
    unique_tags = []
    seen = set()
    for tag in tags:
        key = tag.lower()
        if key in seen:
            continue
        seen.add(key)
        unique_tags.append(tag)

    explanation_parts = []
    if raw.image_urls:
        explanation_parts.append("Image reference: " + raw.image_urls[0])
    explanation = " ".join(explanation_parts)

    question_id = f"pearson_{slugify(raw.chapter)}_{raw.section}_{raw.number}_{uuid.uuid4().hex[:8]}"

    return {
        "id": question_id,
        "question": stem,
        "option_a": ordered[0],
        "option_b": ordered[1],
        "option_c": ordered[2],
        "option_d": ordered[3],
        "options": ordered,
        "answer": answer_letter,
        "explanation": explanation,
        "why_wrong_a": "",
        "why_wrong_b": "",
        "why_wrong_c": "",
        "why_wrong_d": "",
        "subject": "Biology",
        "topic": raw.chapter,
        "subtopic": raw.section.replace("_", " ").title(),
        "tags": unique_tags,
        "question_image_url": raw.image_urls[0] if raw.image_urls else "",
        "explanation_image_url": "",
        "source": source_label,
        "source_question_number": raw.number,
        "source_section": raw.section,
    }


def convert_markdown(
    md_text: str,
    paddle_index: Optional[Dict[Tuple[str, str, int], RawQuestion]] = None,
    *,
    chapter_headers: Optional[List[str]] = None,
    source_label: str = SOURCE_BY_VOLUME[1],
    volume: int = 1,
) -> Tuple[List[dict], dict]:
    all_questions: List[dict] = []
    headers = chapter_headers or get_chapter_headers(volume)
    report = {
        "volume": volume,
        "chapters": {},
        "parsed": 0,
        "skipped_no_answer": 0,
        "skipped_incomplete_options": 0,
        "duplicates_removed": 0,
        "paddle_enriched": 0,
        "paddle_index_size": len(paddle_index or {}),
    }

    for chapter_title, chunk in split_chapters(md_text, headers):
        question_block, answer_tables = split_questions_and_answer_tables(chunk)
        raw_questions, assertion_template = parse_questions_block(chapter_title, question_block)
        answers_by_section = parse_answer_tables(answer_tables) if answer_tables else {}

        chapter_stats = {
            "raw_found": len(raw_questions),
            "exported": 0,
            "missing_answer": 0,
            "bad_options": 0,
            "paddle_enriched": 0,
            "sections": {},
        }

        for raw in raw_questions:
            if paddle_index:
                before_score = options_quality_score(
                    extract_options(raw.options_blob() or raw.stem_text())
                )
                raw = merge_raw_with_paddle(raw, paddle_index)
                after_score = options_quality_score(
                    extract_options(raw.options_blob() or raw.stem_text())
                )
                if after_score > before_score:
                    report["paddle_enriched"] += 1
                    chapter_stats["paddle_enriched"] += 1

            answer = lookup_answer(raw, answers_by_section)
            if not answer:
                chapter_stats["missing_answer"] += 1
                report["skipped_no_answer"] += 1
                continue

            item = finalize_question(raw, answer, assertion_template, source_label)
            if not item:
                chapter_stats["bad_options"] += 1
                report["skipped_incomplete_options"] += 1
                continue

            chapter_stats["exported"] += 1
            chapter_stats["sections"].setdefault(raw.section, 0)
            chapter_stats["sections"][raw.section] += 1
            all_questions.append(item)

        report["chapters"][chapter_title] = chapter_stats

    # Deduplicate by normalized question text (OCR occasionally repeats)
    deduped: List[dict] = []
    seen_questions = set()
    for item in all_questions:
        key = item["question"].lower()
        if key in seen_questions:
            report["duplicates_removed"] += 1
            continue
        seen_questions.add(key)
        deduped.append(item)

    report["parsed"] = len(deduped)
    return deduped, report


def write_csv(path: Path, questions: List[dict]) -> None:
    headers = [
        "id",
        "question",
        "option_a",
        "option_b",
        "option_c",
        "option_d",
        "answer",
        "explanation",
        "why_wrong_a",
        "why_wrong_b",
        "why_wrong_c",
        "why_wrong_d",
        "subject",
        "topic",
        "subtopic",
        "tags",
        "question_image_url",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers, extrasaction="ignore")
        writer.writeheader()
        for item in questions:
            row = dict(item)
            row["tags"] = "; ".join(item.get("tags", []))
            writer.writerow(row)


def write_json(
    path: Path,
    questions: List[dict],
    *,
    used_paddle_json: bool = False,
    volume: int = 1,
) -> None:
    book = SOURCE_BY_VOLUME.get(volume, SOURCE_BY_VOLUME[1])
    source = f"{book} (OCR markdown"
    if used_paddle_json:
        source += " + PaddleOCR JSON"
    source += ")"
    payload = {
        "app": "NEET MCQ Practice",
        "version": 1,
        "source": source,
        "questionCount": len(questions),
        "questions": questions,
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert Pearson OCR markdown to NEET app import files.")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path(__file__).parent
        / "Objective-Biology-for-NEET-Vol-I-Pearson-Education-2019.pdf_by_PaddleOCR-VL-1.6.md",
        help="Path to PaddleOCR markdown file",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).parent,
        help="Directory for generated import files",
    )
    parser.add_argument(
        "--volume",
        type=int,
        choices=[1, 2],
        default=1,
        help="Pearson book volume (1 or 2)",
    )
    parser.add_argument(
        "--prefix",
        default=None,
        help="Output filename prefix (default: pearson_biology_vol{N})",
    )
    parser.add_argument(
        "--paddle-json",
        type=Path,
        default=None,
        help="PaddleOCR page JSON for higher-quality question blocks and image URLs",
    )
    args = parser.parse_args()

    if args.prefix is None:
        args.prefix = f"pearson_biology_vol{args.volume}"

    if args.paddle_json is None:
        defaults = {
            1: Path(__file__).parent
            / "Objective-Biology-for-NEET-Vol-I-Pearson-Education-2019.pdf_by_PaddleOCR-VL-1.6.json",
            2: Path(__file__).parent / "Objective-Biology-for-NEET2.json",
        }
        args.paddle_json = defaults[args.volume]

    if args.input == parser.get_default("input") and args.volume == 2:
        args.input = Path(__file__).parent / "Objective-Biology-for-NEET2.md"

    if not args.input.exists():
        print(f"Input file not found: {args.input}", file=sys.stderr)
        return 1

    md_text = args.input.read_text(encoding="utf-8", errors="ignore")
    paddle_index: Dict[Tuple[str, str, int], RawQuestion] = {}
    used_paddle_json = False

    chapter_headers = get_chapter_headers(args.volume)
    source_label = SOURCE_BY_VOLUME[args.volume]

    if args.paddle_json.exists():
        pages = load_paddle_pages(args.paddle_json)
        paddle_index = build_paddle_question_index(pages, chapter_headers)
        used_paddle_json = True
        image_map: Dict[str, str] = {}
        for page in pages:
            markdown = page.get("markdown", {})
            if isinstance(markdown, dict):
                image_map.update(markdown.get("images", {}))
        md_text = resolve_markdown_images(md_text, image_map)
        print(f"PaddleOCR JSON loaded: {len(paddle_index)} indexed question blocks")
    else:
        print(f"PaddleOCR JSON not found (skipped): {args.paddle_json}", file=sys.stderr)

    questions, report = convert_markdown(
        md_text,
        paddle_index,
        chapter_headers=chapter_headers,
        source_label=source_label,
        volume=args.volume,
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.output_dir / f"{args.prefix}.json"
    csv_path = args.output_dir / f"{args.prefix}.csv"
    report_path = args.output_dir / f"{args.prefix}_report.json"

    write_json(json_path, questions, used_paddle_json=used_paddle_json, volume=args.volume)
    write_csv(csv_path, questions)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"Parsed MCQs: {report['parsed']}")
    print(f"Paddle-enriched: {report.get('paddle_enriched', 0)}")
    print(f"Skipped (no answer): {report['skipped_no_answer']}")
    print(f"Skipped (bad options): {report['skipped_incomplete_options']}")
    print(f"Duplicates removed: {report['duplicates_removed']}")
    print(f"JSON: {json_path}")
    print(f"CSV:  {csv_path}")
    print(f"Report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
