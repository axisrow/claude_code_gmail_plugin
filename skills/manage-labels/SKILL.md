---
name: manage-labels
description: "Manage Gmail labels: list, create, delete. Use when user asks about Gmail labels, tags, categories, wants to create/delete/list labels, or organize email labels."
argument-hint: "[list | create <name> | delete <label_id>]"
allowed-tools: [Bash]
---

# Manage Gmail Labels

List, create, and delete Gmail labels.

## Arguments

`$ARGUMENTS` — subcommand: `list` (default), `create <name>`, or `delete <label_id>`.

## Subcommand: list (default)

Use the Gmail MCP tool `gmail_list_labels` to get all labels.

Display in two sections:

**System labels** with localized names:
- INBOX → Входящие / Inbox
- SENT → Отправленные / Sent
- DRAFT → Черновики / Drafts
- TRASH → Корзина / Trash
- SPAM → Спам / Spam
- STARRED → Помеченные / Starred
- IMPORTANT → Важные / Important
- CATEGORY_PERSONAL → Личные / Personal
- CATEGORY_SOCIAL → Соцсети / Social
- CATEGORY_PROMOTIONS → Промоакции / Promotions
- CATEGORY_UPDATES → Обновления / Updates
- CATEGORY_FORUMS → Форумы / Forums

**User labels** — show name and ID (needed for tagging operations).

## Subcommand: create <name>

Run:
```bash
python3 ~/.claude/scripts/gmail-analyzer/create_label.py "<name>"
```

Report the created label's name and ID.

## Subcommand: delete <label_id>

**IMPORTANT**: Ask user for confirmation before deleting. Show the label name and ID.

After confirmation, run:
```bash
python3 ~/.claude/scripts/gmail-analyzer/delete_label.py "<label_id>"
```

**Respond in the user's language.**
