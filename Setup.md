# Setup Instructions

## Prerequisites
- Claude Code installed and running
- Python installed
- Notion account
- Obsidian vault stored locally on your machine

---

## Steps

### Step 1: Launch Claude Code in your Obsidian vault folder

---

### Step 2: Create your Notion Integration
1. Go to notion.so/my-integrations
2. Click **New Integration**
3. Name it `Claude Assistant`
4. Select your workspace
5. Click **Submit**
6. Copy the **Internal Integration Token** — it starts with `secret_...`

---

### Step 3: Create your Notion Database
1. Open Notion and click **New Page**
2. Select **Empty Database**
3. Title it **Knowledge Assistant — Outputs**
4. Set up the following columns or edit them to suit your needs:

| Column Name | Type |
|-------------|------|
| Question | Title (default) |
| Answer | Text |
| Source Notes | Text |
| Date | Date |
| Tags | Multi-select |

---

### Step 4: Connect your Integration to the Database
1. Open your Notion database
2. Click the **...** menu in the top right
3. Click **Connect to** and select `Claude Assistant`

---

### Step 5: Get your Database ID
Open your Notion database in a browser. 
The long string of characters before the `?v=` in the URL is your database ID. Copy it.

---

### Step 6: Prompt Claude Code to build the Notion script
In PowerShell type: 
```
I want to connect to a Notion database. My notion API token is XXXXXXX .
Help me wrtie a script that takes a question and answer as input and creates a new row in this notion database. 
The database is now shared with the integration. The database ID is XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX and the column
names are: Question (title), Answer (text), Source Notes (text), Date (date), Tags (multi-select)

```
Claude Code will update and finalise the script for the exact schema.

---

### Step 7: Test it
Run this command in PowerShell to confirm everything is connected:

```
python add_to_notion.py --question "What is a common theme in the most recent 10 files?"
--answer "The most common themes are xxxxx"
--source "23Feb26, 09Jan26, xxxxxx"
--tags "Journal, Notes"

```


