#!/usr/bin/env python3
"""Delete a Gmail label. Usage: delete_label.py <label_id>"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gmail_client  # noqa: E402

if len(sys.argv) < 2:
    print(json.dumps({"error": "Usage: delete_label.py <label_id>"}))
    sys.exit(1)

label_id = sys.argv[1]
try:
    gmail_client.delete_label(label_id)
    print(json.dumps({"status": "ok", "deleted": label_id}))
except Exception as e:
    print(json.dumps({"error": str(e)}, ensure_ascii=False))
    sys.exit(1)
