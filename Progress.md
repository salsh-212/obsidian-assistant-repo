# Project Progress Log

## Session 1 — 23 April 2026

### What I did
- Installed Claude Code via PowerShell
- Pointed Claude Code at a local Obsidian vault containing my personal notes (1300 markdown files!)
- Connected Claude Code to a Notion DB via the Notion API
- Claude Code built a Python script (add_to_notion.py) that logs questions, answers, sources and tags into Notion from the command line
- Successfully tested a live entry appearing in Notion

### What I learned
- How to navigate Claude Code in the terminal
- How APIs work in practice — the Notion API required an integration token and explicit database permissions
- Claude Code writes and executes code autonomously when given clear instructions
- The difference between prompting Claude in a browser vs. giving it real tools and file access

### Next steps
- Build a single script that queries the vault AND logs to Notion automatically. Current functionality doesn't do that automatically.
- It requires me to prompt Claude with the quesiton, copy that answer and then prompt Claude again to push add all of it to add_to_notion.py
  before it pushes it to DB.

```

Basic usage (only question is required):  python add_to_notion.py --question "What is are some recurring topics within the vault?"
Full usage:
  python add_to_notion.py \
    --question "What is are some recurring topics within the vault?" \
    --answer "Some recurring topics are ........." \
    --source "source md file it got info from" \
    --date "2026-04-23" \
    --tags "relevant tag info"

```
