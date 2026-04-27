# Project Progress Log

## Session 1 — 23 April 2026

### What I did
- Installed Claude Code via PowerShell
- Pointed Claude Code at a local Obsidian vault containing my personal notes (1300+ markdown files)
- Connected Claude Code to a Notion DB via the Notion API
- Claude Code built a Python script (add_to_notion.py) that logs questions, answers, sources and tags into Notion from the command line
- Successfully tested a live entry appearing in Notion

#### Notion Database Schema

| Column Name | Type | Description |
|-------------|------|-------------|
| **Question** | Title | The question asked to Claude in natural language |
| **Answer** | Text | Claude's response generated from reading the Obsidian vault |
| **Source Notes** | Text | The specific files Claude pulled from to generate the answer |
| **Date** | Date | Automatically populated with today's date when the script runs |
| **Tags** | Multi-select | Key themes extracted from the answer e.g. "Psalms, Worship, OT" |


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

## Session 2 — 26 April 2026

### What I did
- Prompted Claude to create a single cript ask.py that will allow me to query Claude in natural language and then the answer and any relevant tags, sources etc
  will automatically be logged in Notion DB. Ideal prompt will look something like:

  ```
  python ask.py "Insert the question in here"

  ```

### What I learned
- /btw to ask a side question while Claude is running
- 

### Next steps
- Build a single script that queries the vault AND logs to Notion automatically. Current functionality doesn't do that automatically.
- It requires me to prompt Claude with the quesiton, copy that answer and then prompt Claude again to push add all of it to add_to_notion.py
  before it pushes it to DB.

