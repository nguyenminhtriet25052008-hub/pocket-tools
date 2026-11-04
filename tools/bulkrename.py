#!/usr/bin/env python3
"""bulkrename - rename many files with a regex. Preview first, --apply to commit.

Placeholders in the replacement: \\1 \\2 (regex groups), {n} (counter, 1-based),
{n:03} (zero-padded counter).

Usage:
    python bulkrename.py "IMG_(\\d+)" "trip_\\1"                 # preview
    python bulkrename.py "(.*)\\.jpeg$" "\\1.jpg" -d photos --apply
    python bulkrename.py ".*\\.png$" "slide_{n:02}.png" --apply
"""
import argparse
import os
import re


def plan(names, pattern, replacement):
    """Return [(old, new)] for names matching pattern, in sorted order."""
    rx, result, n = re.compile(pattern), [], 0
    for name in sorted(names):
        if not rx.search(name):
            continue
        n += 1
        new = rx.sub(replacement, name, count=1)
        new = re.sub(r"\{n(?::(\d+))?\}", lambda m: str(n).zfill(int(m.group(1) or 0)), new)
        if new != name:
            result.append((name, new))
    return result


def main():
    ap = argparse.ArgumentParser(description="Regex bulk rename (safe preview).")
    ap.add_argument("pattern")
    ap.add_argument("replacement")
    ap.add_argument("-d", "--dir", default=".", help="folder (default: current)")
    ap.add_argument("--apply", action="store_true", help="really rename")
    args = ap.parse_args()
    files = [f for f in os.listdir(args.dir) if os.path.isfile(os.path.join(args.dir, f))]
    changes = plan(files, args.pattern, args.replacement)
    targets = [new for _, new in changes]
    clashes = {t for t in targets if targets.count(t) > 1 or (t in files and t not in dict(changes))}
    for old, new in changes:
        print(f"{old}  ->  {new}" + ("   !! CONFLICT" if new in clashes else ""))
    if clashes:
        return print("\nAborted: name conflicts detected.")
    if args.apply:
        tmp = [(old, f".bulkrename_tmp_{i}", new) for i, (old, new) in enumerate(changes)]
        for old, t, _ in tmp:  # two-phase rename allows swaps like a<->b
            os.rename(os.path.join(args.dir, old), os.path.join(args.dir, t))
        for _, t, new in tmp:
            os.rename(os.path.join(args.dir, t), os.path.join(args.dir, new))
    print(f"\n{len(changes)} files {'renamed' if args.apply else 'to rename (preview, use --apply)'}.")


if __name__ == "__main__":
    main()
