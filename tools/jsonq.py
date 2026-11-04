#!/usr/bin/env python3
"""jsonq - a tiny `jq`: pretty-print JSON or pull values out with a path.

Path syntax: key.sub[0].name   |   [*] maps over a list   |   [-1] last item

Usage:
    python jsonq.py data.json                       # pretty print
    python jsonq.py data.json "users[0].name"
    python jsonq.py data.json "users[*].email"
    curl -s https://api.github.com/repos/python/cpython | python jsonq.py - stargazers_count
"""
import argparse
import json
import re
import sys

TOKEN = re.compile(r"\[(\*|-?\d+)\]|([^.\[\]]+)")


def query(data, path):
    """Return the value at path. '[*]' fans out over a list."""
    tokens = [m.group(1) or m.group(2) for m in TOKEN.finditer(path)]

    def walk(node, i):
        if i == len(tokens):
            return node
        tok = tokens[i]
        if tok == "*":
            return [walk(item, i + 1) for item in node]
        if isinstance(node, list):
            return walk(node[int(tok)], i + 1)
        return walk(node[tok], i + 1)

    return walk(data, 0)


def main():
    ap = argparse.ArgumentParser(description="Pretty-print / query JSON.")
    ap.add_argument("file", help="JSON file, or - for stdin")
    ap.add_argument("path", nargs="?", default="", help='e.g. "items[0].name"')
    ap.add_argument("-r", "--raw", action="store_true", help="print strings without quotes")
    args = ap.parse_args()
    if args.file == "-":
        data = json.load(sys.stdin)
    else:
        with open(args.file, encoding="utf-8") as f:
            data = json.load(f)
    try:
        result = query(data, args.path)
    except (KeyError, IndexError, TypeError, ValueError) as e:
        sys.exit(f"path not found: {args.path} ({type(e).__name__}: {e})")
    if args.raw and isinstance(result, str):
        print(result)
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
