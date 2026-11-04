#!/usr/bin/env python3
"""dupfind - find duplicate files fast (size -> partial hash -> full hash).

Usage:
    python dupfind.py ~/Pictures D:/Backup
    python dupfind.py . --min-size 1M
"""
import argparse
import hashlib
import os
from collections import defaultdict

UNITS = {"K": 1024, "M": 1024**2, "G": 1024**3}


def parse_size(text):
    text = text.strip().upper()
    return int(float(text[:-1]) * UNITS[text[-1]]) if text[-1] in UNITS else int(text)


def file_hash(path, limit=None, chunk=1 << 20):
    h, read = hashlib.blake2b(), 0
    with open(path, "rb") as f:
        while limit is None or read < limit:
            block = f.read(chunk if limit is None else min(chunk, limit - read))
            if not block:
                break
            h.update(block)
            read += len(block)
    return h.hexdigest()


def group_by(paths, key):
    groups = defaultdict(list)
    for p in paths:
        try:
            groups[key(p)].append(p)
        except OSError:
            pass  # unreadable / vanished file
    return [g for g in groups.values() if len(g) > 1]


def find_duplicates(roots, min_size=1):
    files = [os.path.join(d, n) for r in roots for d, _, names in os.walk(r) for n in names]
    files = [f for f in files if os.path.isfile(f) and not os.path.islink(f)]
    candidates = [g for g in group_by(files, os.path.getsize) if os.path.getsize(g[0]) >= min_size]
    partial = [g2 for g in candidates for g2 in group_by(g, lambda p: file_hash(p, 64 * 1024))]
    return [g2 for g in partial for g2 in group_by(g, file_hash)]


def main():
    ap = argparse.ArgumentParser(description="Find duplicate files.")
    ap.add_argument("roots", nargs="+", help="folders to scan")
    ap.add_argument("--min-size", default="1", help="ignore smaller files, e.g. 100K, 5M")
    args = ap.parse_args()
    groups = find_duplicates(args.roots, parse_size(args.min_size))
    wasted = 0
    for g in sorted(groups, key=lambda g: -os.path.getsize(g[0])):
        size = os.path.getsize(g[0])
        wasted += size * (len(g) - 1)
        print(f"\n[{len(g)} copies x {size:,} bytes]")
        for p in g:
            print("  " + p)
    print(f"\n{len(groups)} duplicate groups, {wasted / 1024**2:,.2f} MB reclaimable.")


if __name__ == "__main__":
    main()
