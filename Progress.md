# Project Progress Log

## Session 1 — 23 April 2026

### What I did
- Installed Claude Code via PowerShell
- Pointed Claude Code at a local Obsidian vault containing my personal notes (1300+ markdown files)
- Connected Claude Code to a Notion DB via the Notion API
- Claude Code built a Python script (add_to_notion.py) that logs questions, answers, sources and tags into Notion Database
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
- How APIs work in practice. The Notion API required an integration token and explicit database permissions. Obsidian didn't need an MCP. files are stored locally.
- The difference between prompting Claude in a browser vs. giving it real tools and file access

### Next steps
- Build a single script that queries the vault AND logs to Notion automatically. Current functionality doesn't do that automatically.
- It requires me to prompt Claude with the quesiton, copy that answer and then prompt Claude again to push add all of it to add_to_notion.py before it pushes it to DB. Current functionality shown below:
  
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
- Prompted Claude to create a  script ask.py that will allow me to query Claude in natural language and then the answer and any relevant tags, sources etc will automatically be logged in Notion DB. End prompt will look something like:

  ```
  python ask.py "Insert the question in here"

  ```
  So flow is as follows:
    Prompt -> ask.py -> Obsidian valut -> Notion DB (via add_to_notion.py).
    The only part I need to be involved in is the beginning prompt!

### What I learned
- /btw to ask a side question while Claude is running
- How to chain two scripts together so that one automatically triggers the other in sequence
- Claude initially wrote ask.py to make a call to Anthropic API. Learnt to prompt Claude to exclude this API approach and instead run this script using Claude Code only. It already had everything it needed to run. This led me to learn a bit about the benefits and usecases for API use. Automatic without needing my consistent input. Scale.

### Next steps
- Brainstorm of some future implementation/addition ideas:
    - Claude code that generates a calendar tracker that shows when i add new files to my vault
    - So far Claude is reading .md files natively but can i get it to read pdf's? Might need to convert .pdf into text file.

