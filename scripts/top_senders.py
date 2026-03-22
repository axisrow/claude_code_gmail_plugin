#!/usr/bin/env python3
"""Get top email senders. Usage: top_senders.py [--max N] [--query Q]"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gmail_client  # noqa: E402

max_results = 5000
query = "category:promotions OR category:updates -is:starred -is:important"

args = sys.argv[1:]
i = 0
while i < len(args):
    if args[i] == "--max" and i + 1 < len(args):
        max_results = int(args[i + 1])
        i += 2
    elif args[i] == "--query" and i + 1 < len(args):
        query = args[i + 1]
        i += 2
    else:
        i += 1

try:
    counter = gmail_client.get_top_senders(max_results=max_results, query=query)
    senders = [{"email": email, "count": count} for email, count in counter.most_common()]
    print(json.dumps({"senders": senders, "total": len(senders)}, ensure_ascii=False))
except Exception as e:
    print(json.dumps({"error": str(e)}, ensure_ascii=False))
    sys.exit(1)
