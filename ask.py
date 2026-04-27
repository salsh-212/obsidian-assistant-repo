#!/usr/bin/env python3
"""
ask.py — Ask a question, search the Bible study vault, and log to Notion.
Runs entirely within Claude Code — no separate API key needed.

Usage:
    python ask.py "What does Hebrews say about the priesthood of Jesus?"
"""

import sys
import os
import re
import json
import subprocess
from datetime import date
from pathlib import Path

# Force UTF-8 output so Unicode in answers doesn't crash on Windows
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ── Config ────────────────────────────────────────────────────────────────────

VAULT_DIR = Path(__file__).parent
NOTION_SCRIPT = VAULT_DIR / "add_to_notion.py"

TOP_K_FILES = 10
MAX_CHARS_PER_FILE = 4000

STOP_WORDS = {
    "what", "how", "why", "when", "who", "where", "which", "does", "did",
    "do", "is", "are", "was", "were", "be", "been", "being", "have", "has",
    "had", "the", "a", "an", "in", "of", "to", "and", "or", "for", "with",
    "about", "from", "that", "this", "it", "me", "tell", "say", "says",
    "mean", "means", "explain", "according", "can", "its", "bible", "says",
}

# Maps well-known passage names → specific chapter files to load directly
# Used when the question names a passage whose title doesn't appear in the Bible text itself
TOPIC_FILE_MAP = {
    "sermon on the mount":  ["40 - Matthew/Matt-05.md", "40 - Matthew/Matt-06.md", "40 - Matthew/Matt-07.md"],
    "beatitudes":           ["40 - Matthew/Matt-05.md"],
    "lord's prayer":        ["40 - Matthew/Matt-06.md", "42 - Luke/Luke-11.md"],
    "our father":           ["40 - Matthew/Matt-06.md", "42 - Luke/Luke-11.md"],
    "great commission":     ["40 - Matthew/Matt-28.md"],
    "last supper":          ["40 - Matthew/Matt-26.md", "42 - Luke/Luke-22.md"],
    "ten commandments":     ["02 - Exodus/Exod-20.md", "05 - Deuteronomy/Deut-05.md"],
    "hall of faith":        ["58 - Hebrews/Heb-11.md"],
    "faith chapter":        ["58 - Hebrews/Heb-11.md"],
    "love chapter":         ["46 - 1 Corinthians/1 Cor-13.md"],
    "fruit of the spirit":  ["48 - Galatians/Gal-05.md"],
    "armor of god":         ["49 - Ephesians/Ephes-06.md"],
    "bread of life":        ["43 - John/John-06.md"],
    "good shepherd":        ["43 - John/John-10.md"],
    "prodigal son":         ["42 - Luke/Luke-15.md"],
    "good samaritan":       ["42 - Luke/Luke-10.md"],
    "triumphal entry":      ["40 - Matthew/Matt-21.md", "43 - John/John-12.md"],
}

# Maps question keywords → vault folder name under Christianity/BIBLE/
BOOK_MAP = {
    "genesis": "01 - Genesis",
    "exodus": "02 - Exodus",
    "leviticus": "03 - Leviticus",
    "numbers": "04 - Numbers",
    "deuteronomy": "05 - Deuteronomy",
    "joshua": "06 - Joshua",
    "judges": "07 - Judges",
    "ruth": "08 - Ruth",
    "1 samuel": "09 - 1 Samuel",
    "2 samuel": "10 - 2 Samuel",
    "1 kings": "11 - 1 Kings",
    "2 kings": "12 - 2 Kings",
    "1 chronicles": "13 - 1 Chronicles",
    "2 chronicles": "14 - 2 Chronicles",
    "ezra": "15 - Ezra",
    "nehemiah": "16 - Nehemiah",
    "esther": "17 - Esther",
    "job": "18 - Job",
    "psalm": "19 - Psalm",
    "psalms": "19 - Psalm",
    "proverbs": "20 - Proverbs",
    "ecclesiastes": "21 - Ecclesiastes",
    "song of solomon": "22 - Song of Solomon",
    "isaiah": "23 - Isaiah",
    "jeremiah": "24 - Jeremiah",
    "lamentations": "25 - Lamentations",
    "ezekiel": "26 - Ezekiel",
    "daniel": "27 - Daniel",
    "hosea": "28 - Hosea",
    "joel": "29 - Joel",
    "amos": "30 - Amos",
    "obadiah": "31 - Obadiah",
    "jonah": "32 - Jonah",
    "micah": "33 - Micah",
    "nahum": "34 - Nahum",
    "habakkuk": "35 - Habakkuk",
    "zephaniah": "36 - Zephaniah",
    "haggai": "37 - Haggai",
    "zechariah": "38 - Zechariah",
    "malachi": "39 - Malachi",
    "matthew": "40 - Matthew",
    "mark": "41 - Mark",
    "luke": "42 - Luke",
    "john": "43 - John",
    "acts": "44 - Acts",
    "romans": "45 - Romans",
    "1 corinthians": "46 - 1 Corinthians",
    "2 corinthians": "47 - 2 Corinthians",
    "galatians": "48 - Galatians",
    "ephesians": "49 - Ephesians",
    "philippians": "50 - Philippians",
    "colossians": "51 - Colossians",
    "1 thessalonians": "52 - 1 Thessalonians",
    "2 thessalonians": "53 - 2 Thessalonians",
    "1 timothy": "54 - 1 Timothy",
    "2 timothy": "55 - 2 Timothy",
    "titus": "56 - Titus",
    "philemon": "57 - Philemon",
    "hebrews": "58 - Hebrews",
    "james": "59 - James",
    "1 peter": "60 - 1 Peter",
    "2 peter": "61 - 2 Peter",
    "1 john": "62 - 1 John",
    "2 john": "63 - 2 John",
    "3 john": "64 - 3 John",
    "jude": "65 - Jude",
    "revelation": "66 - Revelation",
}

# ── Step 1: Search ─────────────────────────────────────────────────────────────

def extract_keywords(question: str) -> list[str]:
    words = re.findall(r"[a-zA-Z']+", question.lower())
    return [w for w in words if w not in STOP_WORDS and len(w) > 2]


def detect_topic(question: str) -> list[Path] | None:
    """Return specific file paths if the question names a well-known passage."""
    q = question.lower()
    for phrase in sorted(TOPIC_FILE_MAP, key=len, reverse=True):
        if phrase in q:
            bible_dir = VAULT_DIR / "Christianity" / "BIBLE"
            paths = [bible_dir / p for p in TOPIC_FILE_MAP[phrase]]
            return [p for p in paths if p.exists()]
    return None


def detect_book(question: str) -> str | None:
    """Return the vault folder name if a Bible book is named in the question."""
    q = question.lower()
    # Check multi-word book names first (e.g. "1 corinthians" before "corinthians")
    for name in sorted(BOOK_MAP, key=len, reverse=True):
        if name in q:
            return BOOK_MAP[name]
    return None


def score_files(paths, keywords: list[str]) -> list[tuple[Path, int]]:
    scores = {}
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore").lower()
        except OSError:
            continue
        score = sum(text.count(kw) for kw in keywords)
        if score > 0:
            scores[path] = score
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)


def search_vault(question: str) -> list[tuple[Path, int]]:
    keywords = extract_keywords(question)
    if not keywords:
        return []

    # 1. Named passage (e.g. "Sermon on the Mount") → load specific files directly
    topic_files = detect_topic(question)
    if topic_files:
        # Score the topic files, then pad with keyword-ranked global results
        ranked = score_files(topic_files, keywords)
        # Give topic files a floor score so they always appear even with low keyword hits
        ranked = [(p, max(s, 1)) for p, s in ranked]
        # Add any topic files that scored 0 (keyword not present but still relevant)
        ranked_paths = {p for p, _ in ranked}
        for p in topic_files:
            if p not in ranked_paths:
                ranked.append((p, 1))
        if len(ranked) < TOP_K_FILES:
            extra = score_files(
                (p for p in VAULT_DIR.rglob("*.md") if p not in {r for r, _ in ranked}),
                keywords,
            )
            ranked = ranked + extra[: TOP_K_FILES - len(ranked)]
        return ranked[:TOP_K_FILES]

    # 2. Named book (e.g. "Hebrews") → search within that book
    book_folder = detect_book(question)
    if book_folder:
        book_dir = VAULT_DIR / "Christianity" / "BIBLE" / book_folder
        if book_dir.exists():
            ranked = score_files(book_dir.rglob("*.md"), keywords)
            if len(ranked) < TOP_K_FILES:
                book_paths = {p for p, _ in ranked}
                global_ranked = score_files(
                    (p for p in VAULT_DIR.rglob("*.md") if p not in book_paths),
                    keywords,
                )
                ranked = ranked + global_ranked[: TOP_K_FILES - len(ranked)]
            return ranked[:TOP_K_FILES]

    # 3. General question → global keyword search
    return score_files(VAULT_DIR.rglob("*.md"), keywords)[:TOP_K_FILES]


# ── Step 2: Build context ──────────────────────────────────────────────────────

def build_context(ranked: list[tuple[Path, int]]) -> str:
    parts = []
    for path, _score in ranked:
        content = path.read_text(encoding="utf-8", errors="ignore")
        if len(content) > MAX_CHARS_PER_FILE:
            content = content[:MAX_CHARS_PER_FILE] + "\n…[truncated]"
        rel = path.relative_to(VAULT_DIR)
        parts.append(f"### Source: {rel}\n\n{content}")
    return "\n\n---\n\n".join(parts)


# ── Step 3: Ask Claude (via Claude Code CLI) ───────────────────────────────────

PROMPT_TEMPLATE = """\
You are a Bible study assistant. The following excerpts are from a personal Bible study vault.

Using ONLY the vault content below, answer the question. Then identify:
- The specific source files and verse numbers your answer draws from.
- 3–5 concise theological tags capturing the key themes (e.g. "Priesthood", "Atonement", "Covenant").

Respond with ONLY valid JSON — no markdown fences, no extra text:
{{
  "answer": "A clear, thorough answer grounded in the vault content.",
  "source_notes": "e.g. '58 - Hebrews/Heb-07.md (v1–3, v26–28); Heb-09.md (v11–14)'",
  "tags": ["Tag1", "Tag2", "Tag3"]
}}

Question: {question}

Vault content:
{context}"""


def ask_claude(question: str, context: str) -> dict:
    prompt = PROMPT_TEMPLATE.format(question=question, context=context)

    # Pass prompt via stdin to avoid Windows MAX_PATH / command-line length limits
    cmd = ["claude", "--print", "--output-format", "json"]
    result = subprocess.run(cmd, input=prompt, capture_output=True, text=True, encoding="utf-8")

    if result.returncode != 0:
        print(f"Claude Code error:\n{result.stderr.strip()}")
        sys.exit(1)

    try:
        cli_output = json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"Could not parse Claude Code CLI output:\n{result.stdout[:500]}")
        sys.exit(1)

    if cli_output.get("is_error"):
        print(f"Claude returned an error: {cli_output.get('result', '')}")
        sys.exit(1)

    response_text = cli_output.get("result", "").strip()

    # Strip markdown fences if Claude adds them despite instructions
    response_text = re.sub(r"^```(?:json)?\s*", "", response_text)
    response_text = re.sub(r"\s*```$", "", response_text.strip())

    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if match:
            return json.loads(match.group())
        print(f"Could not parse JSON from Claude's response:\n{response_text}")
        sys.exit(1)


# ── Step 4: Log to Notion ──────────────────────────────────────────────────────

def log_to_notion(question: str, answer: str, source_notes: str, tags: list[str]):
    cmd = [
        sys.executable, str(NOTION_SCRIPT),
        "--question", question,
        "--answer", answer,
        "--source", source_notes,
        "--date", str(date.today()),
        "--tags", ",".join(tags),
    ]
    env = {**os.environ, "PYTHONUTF8": "1"}
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", env=env)
    if result.returncode != 0:
        print(f"Notion error: {result.stderr.strip()}")
    else:
        print(result.stdout.strip())


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print('Usage: python ask.py "Your question here"')
        sys.exit(1)

    question = " ".join(sys.argv[1:])

    # 1. Search vault
    print(f"\nSearching vault for: {question}")
    ranked = search_vault(question)
    if not ranked:
        print("No relevant files found in the vault.")
        sys.exit(1)

    topic = detect_topic(question)
    book  = detect_book(question)
    if topic:
        print(f"Topic detected: loading specific passage files")
    elif book:
        print(f"Book detected: {book}")
    print(f"Top {len(ranked)} file(s) selected:")
    for path, score in ranked:
        print(f"  [{score:>4} hits]  {path.relative_to(VAULT_DIR)}")

    # 2. Build context
    context = build_context(ranked)

    # 3. Ask Claude via Claude Code CLI
    print("\nAsking Claude...")
    result = ask_claude(question, context)

    answer      = result.get("answer", "")
    source_notes = result.get("source_notes", "")
    tags        = result.get("tags", [])

    print(f"\n{'-' * 60}")
    print(f"Answer:\n{answer}")
    print(f"\nSources:  {source_notes}")
    print(f"Tags:     {', '.join(tags)}")
    print(f"{'-' * 60}")

    # 4. Log to Notion
    print("\nLogging to Notion...")
    log_to_notion(question, answer, source_notes, tags)


if __name__ == "__main__":
    main()
