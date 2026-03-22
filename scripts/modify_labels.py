#!/usr/bin/env python3
"""Apply label changes to Gmail messages. Reads JSON from stdin.

Input format:
{"actions": [{"message_id": "...", "add": ["LabelID"], "remove": ["LabelID"]}]}
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gmail_client  # noqa: E402

data = json.loads(sys.stdin.read())
results = []

for action in data.get("actions", []):
    msg_id = action["message_id"]
    add = action.get("add", [])
    remove = action.get("remove", [])
    try:
        gmail_client.modify_message_labels(msg_id, add_label_ids=add or None, remove_label_ids=remove or None)
        results.append({"message_id": msg_id, "status": "ok"})
    except Exception as e:
        results.append({"message_id": msg_id, "status": "error", "error": str(e)})

print(json.dumps({"results": results}, ensure_ascii=False))
