---
name: auto-tag
description: "Analyze and auto-tag Gmail emails with labels. Use when user asks to tag emails, auto-label, categorize inbox, apply labels automatically, classify and tag mail, or organize inbox with labels."
argument-hint: "[query]"
allowed-tools: [Bash]
---

# Auto-Tag Gmail Emails

Analyze emails and apply label recommendations with user confirmation.

## Arguments

`$ARGUMENTS` — optional Gmail search query. If empty, use recent INBOX messages.

## Step 1: Fetch emails and labels

1. Use Gmail MCP `gmail_search_messages` to fetch emails (use query from `$ARGUMENTS` or `in:inbox`, limit 10-20)
2. Use Gmail MCP `gmail_list_labels` to get available user labels
3. For each email, use `gmail_read_message` to get full content and current labels

## Step 2: Classify with tagging context

For each email, classify into one of 5 categories:

- 🟢 **PERSONAL / ЛИЧНОЕ** — addressed personally, requires response
- 🔵 **USEFUL NEWSLETTER / ПОЛЕЗНАЯ РАССЫЛКА** — consciously subscribed content
- 🟡 **IMPORTANT NOTIFICATION / ВАЖНОЕ УВЕДОМЛЕНИЕ** — transactional, worth reading
- 🟠 **NOISE / ШУМ** — repetitive alerts, noise
- 🔴 **SPAM / МУСОР** — marketing, promotions, spam

For each email provide:
1. Category (with emoji)
2. Brief summary
3. Recommendation
4. Suggested labels from the available user label list

## Step 3: Generate tagging proposal

Create a summary table of proposed changes:
- For each email: abbreviated subject, current labels, proposed new labels (by name)
- Only propose labels that are NOT already on the email

## Step 4: Confirm with user

Ask the user to confirm: "Apply these tags? (y/n)"

**Do NOT proceed without explicit user confirmation.**

## Step 5: Apply tags (only after confirmation)

After user confirms, construct JSON and pipe to the apply script:

```bash
echo '{"actions": [{"message_id": "MSG_ID", "add": ["Label_ID"]}]}' | python3 ${CLAUDE_PLUGIN_ROOT}/scripts/modify_labels.py
```

Report results: how many emails were tagged successfully.

If user declines, report "Cancelled." and do not apply.

**Respond in the user's language.**
