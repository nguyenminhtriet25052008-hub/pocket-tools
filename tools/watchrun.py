#!/usr/bin/env python3
"""watchrun - re-run a command whenever matching files change. No dependencies
(uses polling), works everywhere.

Usage:
    python watchrun.py "*.py" -- python -m unittest
    python watchrun.py "src/**/*.c" "*.h" -i 1 -- make
"""
import argparse
import glob
import os
import subprocess
import sys
import time


def snapshot(patterns):
    """Map every matching file to its modification time."""
    state = {}
    for pattern in patterns:
        for path in glob.glob(pattern, recursive=True):
            try:
                state[path] = os.path.getmtime(path)
            except OSError:
                pass
    return state


def changed(old, new):
    return sorted(p for p in old.keys() | new.keys() if old.get(p) != new.get(p))


def split_argv(argv):
    if "--" not in argv:
        return argv, []
    i = argv.index("--")
    return argv[:i], argv[i + 1:]


def main():
    ap = argparse.ArgumentParser(description="Run a command when files change.",
                                 usage="watchrun.py PATTERN [PATTERN ...] [-i SEC] -- COMMAND ...")
    ap.add_argument("patterns", nargs="+", help='glob patterns, e.g. "*.py" "src/**/*.js"')
    ap.add_argument("-i", "--interval", type=float, default=0.5, help="poll seconds")
    own, command = split_argv(sys.argv[1:])
    args = ap.parse_args(own)
    if not command:
        ap.error("put the command after '--'")
    state = snapshot(args.patterns)
    print(f"Watching {len(state)} files. Ctrl+C to stop.")
    try:
        while True:
            print(f"\n$ {' '.join(command)}")
            print(f"[exit {subprocess.call(command)}] waiting for changes...")
            while True:
                time.sleep(args.interval)
                new = snapshot(args.patterns)
                diff = changed(state, new)
                if diff:
                    state = new
                    print("changed: " + ", ".join(diff[:5]) + (" ..." if len(diff) > 5 else ""))
                    break
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
