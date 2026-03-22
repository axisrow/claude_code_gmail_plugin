# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Gmail email analyzer using Claude Agent SDK. Fetches emails via gws CLI or google-api-python-client (fallback), sends them to Claude for analysis (importance rating, summary, action required). Claude auto-tags emails with user-defined labels.

## Architecture

- `main.py` — Entry point. Uses `ClaudeSDKClient` with async streaming to send emails to Claude for analysis. Parses tagging JSON from Claude's response, applies labels after user confirmation. CLI for label CRUD.
- `gmail_client.py` — Gmail client with three backends: gcloud ADC (priority), gws CLI, credentials.json (fallback). Auto-selects available backend. Provides label management (get/create/delete) and message label modification.

### Email categories
Claude classifies emails into 5 categories: Personal 🟢, Useful Newsletter 🔵, Important Notification 🟡, Noise 🟠, Spam 🔴.

### Tagging JSON format
Claude returns tagging as JSON block after analysis:
```json
{"tagging": [{"message_id": "...", "add_labels": ["Label_ID"], "remove_labels": ["Label_ID"]}]}
```

## Setup

### Option 1: gcloud ADC

1. Install gcloud CLI: https://cloud.google.com/sdk/docs/install
2. Need `client_secret.json` (OAuth Client ID from GCP Console)
3. `gcloud auth application-default login --client-id-file=client_secret.json --scopes=https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/gmail.modify`

### Option 2: gws CLI

1. Install gws CLI: `npm install -g @googleworkspace/cli`
2. Authorize: `gws auth login -s gmail`
3. Verify: `gws gmail +triage --max 3`

### Option 3: credentials.json

1. Create OAuth credentials in GCP Console, download `credentials.json` to project root
2. On first run, browser will open for authorization (creates `token.json`)

## Running

```bash
pip install -r requirements.txt
python main.py                              # analyze only (INBOX)
python main.py --tag                        # analyze + auto-tag
python main.py --tag --label CATEGORY_X     # auto-tag emails with specific label
python main.py --label CATEGORY_UPDATES     # analyze emails with specific label
python main.py top [N]                      # top-N newsletter senders (default 10)
python main.py mark <Label_ID> <emails>     # label messages from specific senders
python main.py mark-query <Label_ID> <query># label messages by Gmail search query
python main.py labels                       # list all labels
python main.py labels create Name           # create user label
python main.py labels delete Label_ID       # delete user label
python main.py --help                       # show usage help
```

## gmail_client.py — API справочник

### Получение писем
- `get_emails(max_results=10, label_ids=None)` — основной метод, авто-выбор бэкенда. Фильтрация только по label_ids, **не поддерживает query**
- `get_emails_via_api(max_results, creds, label_ids)` — через Google API (ADC или credentials.json)
- `get_emails_via_gws(max_results, label_ids)` — через gws CLI

### Поиск и аналитика (поддерживают Gmail query syntax)
- `get_top_senders(max_results=5000, query="category:promotions OR category:updates ...")` — Counter отправителей
- `get_subjects_by_senders(senders, max_per_sender=10, query_base=...)` — темы писем по списку отправителей

### Пометка писем (поддерживают Gmail query syntax)
- `label_messages_by_query(label_id, query)` — пометить все письма по query → int
- `label_messages_from_senders(label_id, senders, query_base=...)` — пометить по отправителям → {sender: count}

### Label management
- `get_labels()`, `create_label(name)`, `delete_label(label_id)`, `modify_message_labels(msg_id, add, remove)`

### Прямой доступ к Gmail API
Для произвольных запросов (например, поиск инвойсов):
```python
creds = gmail_client._try_adc()
service = build('gmail', 'v1', credentials=creds)
results = service.users().messages().list(userId='me', q='subject:invoice newer_than:2m', maxResults=50).execute()
```

## Dependencies

`claude-agent-sdk`, `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`

## Key Details

- Language: Russian (prompts, UI messages, output)
- Email bodies truncated at 2000 chars
- Default fetch: 10 most recent INBOX messages
- Backend auto-selection: gcloud ADC → gws CLI → credentials.json → error with instructions
- Scope: `gmail.modify` (read + label management)
- Claude returns tagging recommendations as JSON after text analysis; user confirms before applying
- Re-authorization: delete `token.json` if switching from `gmail.readonly` to `gmail.modify` scope
- No tests exist currently
