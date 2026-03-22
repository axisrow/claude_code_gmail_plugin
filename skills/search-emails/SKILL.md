---
name: search-emails
description: "Search Gmail emails by query. Use when user asks to find emails, search inbox, look for messages from someone, filter by sender/subject/date, find invoices, receipts, or specific emails."
argument-hint: "<gmail_query> [--max N]"
allowed-tools: [Bash]
---

# Search Gmail Emails

Search emails using Gmail query syntax and display results.

## Arguments

`$ARGUMENTS` — Gmail search query. Supports standard Gmail operators:
- `from:sender@example.com` — by sender
- `subject:keyword` — by subject
- `after:2024/01/01 before:2024/02/01` — by date range
- `newer_than:2m` — relative date
- `is:unread` — unread only
- `has:attachment` — with attachments
- `label:LabelName` — by label
- Combined: `from:github.com subject:PR newer_than:1w`

## Step 1: Execute search

Use the Gmail MCP tool `gmail_search_messages` with the query from `$ARGUMENTS`. Default max results: 20.

## Step 2: Display results

For each result, show:
- Number (1, 2, 3...)
- **From**: sender name and email
- **Date**: when sent
- **Subject**: email subject
- Brief body excerpt (first 150-200 chars)

## Step 3: Offer next actions

After displaying results, suggest possible actions:
- Analyze these emails with `/gmail-analyzer:analyze-emails`
- Auto-tag them with `/gmail-analyzer:auto-tag`
- Read a specific email in full
- Refine search with different criteria

**Respond in the user's language.**
