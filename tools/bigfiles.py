#!/usr/bin/env python3
"""bigfiles - show what is eating your disk: top N largest files and folders.

Usage:
    python bigfiles.py C:/Users/me -n 15
    python bigfiles.py . --dirs
"""
import argparse
import heapq
import os
from collections import defaultdict


def human(n):
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return f"{n:,.1f} {unit}"
        n /= 1024


def scan(root):
    """Return ({file: size}, {dir: total size including subfolders})."""
    files, dirs = {}, defaultdict(int)
    root = os.path.abspath(root)
    for d, _, names in os.walk(root):
        for n in names:
            p = os.path.join(d, n)
            try:
                if os.path.islink(p):
                    continue
                size = os.path.getsize(p)
            except OSError:
                continue
            files[p] = size
            parent = d
            while True:  # add size to every ancestor up to root
                dirs[parent] += size
                if parent == root:
                    break
                parent = os.path.dirname(parent)
    return files, dirs


def main():
    ap = argparse.ArgumentParser(description="List the largest files / folders.")
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("-n", type=int, default=10, help="how many to show (default 10)")
    ap.add_argument("--dirs", action="store_true", help="rank folders instead of files")
    args = ap.parse_args()
    files, dirs = scan(args.root)
    table = dirs if args.dirs else files
    print(f"Total: {human(sum(files.values()))} in {len(files):,} files\n")
    for path, size in heapq.nlargest(args.n, table.items(), key=lambda kv: kv[1]):
        print(f"{human(size):>12}  {path}")


if __name__ == "__main__":
    main()
