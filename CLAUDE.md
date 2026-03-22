# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Claude Code plugin for Gmail email analysis. Extends Gmail MCP with 5-category classification, auto-tagging, search, and label management. Also includes standalone CLI (`main.py`) using Claude Agent SDK.

**Two modes of operation:**
- **Plugin (skills)** — works inside Claude Code session via Gmail MCP tools + helper scripts
- **Standalone CLI (`main.py`)** — runs outside Claude Code via Claude Agent SDK (cannot run inside Claude Code due to nested session restriction)

## Plugin Architecture

```
.claude-plugin/plugin.json     # plugin manifest ("gmail-analyzer")
skills/
  analyze-emails/SKILL.md      # 5-category email classification
  search-emails/SKILL.md       # Gmail query search
  manage-labels/SKILL.md       # label CRUD
  auto-tag/SKILL.md            # analyze + apply labels with confirmation
scripts/
  modify_labels.py             # apply label changes (stdin JSON)
  create_label.py              # create label (CLI arg)
  delete_label.py              # delete label (CLI arg)
  top_senders.py               # sender analytics (CLI args)
```

### Skills ↔ MCP ↔ Scripts

Skills use **Gmail MCP tools** for read operations:
- `gmail_search_messages`, `gmail_read_message`, `gmail_list_labels`

Skills use **scripts** (via Bash) for write operations not available in MCP:
- `modify_labels.py` — add/remove labels from messages
- `create_label.py` / `delete_label.py` — label CRUD

Scripts communicate via JSON (stdin/stdout) and import `gmail_client.py` via `sys.path`.

### Email categories

- 🟢 Personal / Личное
- 🔵 Useful Newsletter / Полезная рассылка
- 🟡 Important Notification / Важное уведомление
- 🟠 Noise / Шум
- 🔴 Spam / Мусор

### Tagging JSON format

```json
{"actions": [{"message_id": "...", "add": ["Label_ID"], "remove": ["Label_ID"]}]}
```

## gmail_client.py

Gmail API client with three backends (auto-selected): gcloud ADC → gws CLI → credentials.json.

Key functions:
- `get_emails(max_results, label_ids)` — fetch emails (no query support)
- `get_top_senders(max_results, query)` — sender Counter via Batch API (supports Gmail query)
- `label_messages_by_query(label_id, query)` — bulk label by Gmail query
- `get_labels()`, `create_label()`, `delete_label()`, `modify_message_labels()` — label management
- `_get_service()` — get Gmail API service object for direct API calls

## Setup

See README.md for detailed setup instructions. Three auth options: gcloud ADC (recommended), gws CLI, credentials.json (OAuth fallback).

Quick start: `pip install -r requirements.txt` + configure one auth backend.

## Development

Test plugin locally:
```bash
claude --plugin-dir /Users/axisrow/Projects/claude_code_gmail_plugin
```

Test individual skills: `/gmail-analyzer:analyze-emails`, `/gmail-analyzer:search-emails`, etc.

Test scripts directly:
```bash
python scripts/top_senders.py --max 100
python scripts/create_label.py "Test Label"
echo '{"actions":[]}' | python scripts/modify_labels.py
```

## Key Details

- Language: Russian (prompts, UI), skill descriptions in English (i18n), skill prompts respond in user's language
- Email bodies truncated at 2000 chars
- Backend auto-selection: gcloud ADC → gws CLI → credentials.json
- Scope: `gmail.modify` (read + label management)
- Re-authorization: delete `token.json` if switching scopes
- Plugin deps (`requirements.txt`): `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`
- SDK deps (`requirements-sdk.txt`): + `claude-agent-sdk`, `openpyxl` (only for standalone main.py)
- No tests exist currently
