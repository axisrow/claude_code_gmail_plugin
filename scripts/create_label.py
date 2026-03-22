#!/usr/bin/env python3
"""Create a Gmail label. Usage: create_label.py <name>"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gmail_client  # noqa: E402

if len(sys.argv) < 2:
    print(json.dumps({"error": "Usage: create_label.py <name>"}))
    sys.exit(1)

name = " ".join(sys.argv[1:])
try:
    result = gmail_client.create_label(name)
    print(json.dumps(result, ensure_ascii=False))
except Exception as e:
    print(json.dumps({"error": str(e)}, ensure_ascii=False))
    sys.exit(1)
