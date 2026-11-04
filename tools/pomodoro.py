#!/usr/bin/env python3
"""pomodoro - a focus timer in your terminal with a progress bar and a beep.

Usage:
    python pomodoro.py              # 25 min work / 5 min break, 4 rounds
    python pomodoro.py 50 10 -r 2   # 50/10, 2 rounds
"""
import argparse
import sys
import time


def bar(done, total, width=30):
    filled = int(width * done / total) if total else width
    return "#" * filled + "-" * (width - filled)


def fmt(seconds):
    return f"{int(seconds) // 60:02d}:{int(seconds) % 60:02d}"


def beep(times=3):
    for _ in range(times):
        sys.stdout.write("\a")
        sys.stdout.flush()
        time.sleep(0.3)


def countdown(label, minutes):
    total = int(minutes * 60)
    start = time.monotonic()
    while True:
        elapsed = min(time.monotonic() - start, total)
        sys.stdout.write(f"\r{label:<6} [{bar(elapsed, total)}] {fmt(total - elapsed)} ")
        sys.stdout.flush()
        if elapsed >= total:
            break
        time.sleep(1)
    print()
    beep()


def main():
    ap = argparse.ArgumentParser(description="Terminal Pomodoro timer.")
    ap.add_argument("work", nargs="?", type=float, default=25, help="work minutes")
    ap.add_argument("rest", nargs="?", type=float, default=5, help="break minutes")
    ap.add_argument("-r", "--rounds", type=int, default=4)
    args = ap.parse_args()
    try:
        for i in range(1, args.rounds + 1):
            print(f"Round {i}/{args.rounds}")
            countdown("WORK", args.work)
            if i < args.rounds:
                countdown("BREAK", args.rest)
        print("Done! Take a long break. :)")
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
