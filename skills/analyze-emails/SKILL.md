---
name: analyze-emails
description: "Analyze Gmail emails with 5-category classification (Personal, Newsletter, Important, Noise, Spam). Use when user asks to check email, analyze inbox, review messages, triage mail, or classify emails."
argument-hint: "[query]"
allowed-tools: [Bash]
---

# Analyze Gmail Emails

Fetch and analyze emails using the 5-category classification system.

## Arguments

`$ARGUMENTS` — optional Gmail search query (e.g., `newer_than:1d`, `from:github.com`). If empty, fetch recent INBOX messages.

## Step 1: Fetch emails

Use the Gmail MCP tool `gmail_search_messages` to fetch emails. If `$ARGUMENTS` contains a query, use it. Otherwise search for `in:inbox` with a reasonable limit (10-20).

For each message, use `gmail_read_message` to get full content if needed.

## Step 2: Classify each email

For each email, assign one of 5 categories:

- 🟢 **PERSONAL / ЛИЧНОЕ** — addressed personally, requires response or attention
- 🔵 **USEFUL NEWSLETTER / ПОЛЕЗНАЯ РАССЫЛКА** — consciously subscribed content, worth reading
- 🟡 **IMPORTANT NOTIFICATION / ВАЖНОЕ УВЕДОМЛЕНИЕ** — transactional, worth reading (mentions, security alerts, PR reviews, billing)
- 🟠 **NOISE / ШУМ** — repetitive alerts, CI/CD crashes, mass GitHub pushes, deploy notifications — useful in theory but clutters inbox
- 🔴 **SPAM / МУСОР** — marketing, promotions, unsolicited mail

For each email provide:
1. Category (one of the five above with emoji)
2. Brief summary (1 sentence)
3. Recommendation: keep / unsubscribe / set up filter

## Step 3: Summary

At the end, provide a summary table: how many emails in each category and an overall recommendation for inbox cleanup.

**Respond in the user's language.**
