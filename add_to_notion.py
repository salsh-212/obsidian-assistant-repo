#!/usr/bin/env python3
"""
Add a question/answer row to the Bible Study Notion database.

Usage:
    python add_to_notion.py --question "..." --answer "..." [--source "..."] [--date "YYYY-MM-DD"] [--tags "Tag1,Tag2"]

All flags except --question are optional.

Setup:
    pip install requests
    Set NOTION_TOKEN as an environment variable (recommended), or hardcode it below.
"""

import sys
import os
import argparse
import json
from datetime import date
import requests

NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "XXXXXXXXXXXXXXX")
DATABASE_ID = "XXXXXXXXXXXXXXXXXXXXXXXXXXX"

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}


def rich_text(value: str) -> list:
    return [{"type": "text", "text": {"content": value}}]


def add_row(question: str, answer: str = "", source_notes: str = "", entry_date: str = "", tags: list[str] = []):
    properties = {
        "Question": {"title": rich_text(question)},
    }

    if answer:
        properties["Answer"] = {"rich_text": rich_text(answer)}

    if source_notes:
        properties["Source Notes"] = {"rich_text": rich_text(source_notes)}

    if entry_date:
        properties["Date"] = {"date": {"start": entry_date}}

    if tags:
        properties["Tags"] = {"multi_select": [{"name": t.strip()} for t in tags]}

    payload = {"parent": {"database_id": DATABASE_ID}, "properties": properties}

    response = requests.post("https://api.notion.com/v1/pages", headers=HEADERS, data=json.dumps(payload))
    if not response.ok:
        print(f"Error {response.status_code}: {response.text}")
        sys.exit(1)

    page = response.json()
    print(f"Row created: {page.get('url', page['id'])}")
    return page


def main():
    parser = argparse.ArgumentParser(description="Add a row to the Notion database.")
    parser.add_argument("--question", required=True, help="The question (required)")
    parser.add_argument("--answer", default="", help="The answer")
    parser.add_argument("--source", default="", help="Source notes (e.g. 'Hebrews 11:1')")
    parser.add_argument("--date", default=str(date.today()), help="Date in YYYY-MM-DD format (defaults to today)")
    parser.add_argument("--tags", default="", help="Comma-separated tags (e.g. 'Faith,Hebrews,OT')")

    args = parser.parse_args()
    tags = [t for t in args.tags.split(",") if t.strip()] if args.tags else []

    add_row(
        question=args.question,
        answer=args.answer,
        source_notes=args.source,
        entry_date=args.date,
        tags=tags,
    )


if __name__ == "__main__":
    main()
