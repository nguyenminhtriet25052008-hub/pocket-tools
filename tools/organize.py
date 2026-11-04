#!/usr/bin/env python3
"""organize - tidy a messy folder (hello, Downloads) into category subfolders.

Dry-run by default; add --apply to actually move files.

Usage:
    python organize.py ~/Downloads            # preview
    python organize.py ~/Downloads --apply    # do it
"""
import argparse
import os
import shutil

CATEGORIES = {
    "Images": "jpg jpeg png gif bmp webp svg heic ico",
    "Videos": "mp4 mkv mov avi webm flv wmv",
    "Audio": "mp3 wav flac aac ogg m4a",
    "Documents": "pdf doc docx xls xlsx ppt pptx txt md csv odt rtf",
    "Archives": "zip rar 7z tar gz bz2 xz iso",
    "Code": "py js ts html css json c cpp h java ipynb sh ps1",
    "Programs": "exe msi apk deb dmg appimage",
}
EXT_MAP = {ext: cat for cat, exts in CATEGORIES.items() for ext in exts.split()}


def unique_path(path):
    base, ext = os.path.splitext(path)
    i = 1
    while os.path.exists(path):
        path, i = f"{base} ({i}){ext}", i + 1
    return path


def plan(folder):
    """Yield (source, destination) for every file directly inside folder."""
    for name in sorted(os.listdir(folder)):
        src = os.path.join(folder, name)
        if os.path.isfile(src):
            category = EXT_MAP.get(os.path.splitext(name)[1][1:].lower(), "Other")
            yield src, os.path.join(folder, category, name)


def main():
    ap = argparse.ArgumentParser(description="Sort files into category folders.")
    ap.add_argument("folder")
    ap.add_argument("--apply", action="store_true", help="really move files")
    args = ap.parse_args()
    moves = list(plan(args.folder))
    for src, dst in moves:
        if args.apply:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            dst = unique_path(dst)
            shutil.move(src, dst)
        print(f"{os.path.basename(src)}  ->  {os.path.relpath(dst, args.folder)}")
    print(f"\n{len(moves)} files {'moved' if args.apply else 'would be moved (dry-run, use --apply)'}.")


if __name__ == "__main__":
    main()
