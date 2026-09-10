#!/usr/bin/env python3
"""Convert images in the subset folder to greyscale, overwriting files.

Usage:
    python preprocess.py [folder]

If no folder is provided it defaults to the repository's
`subset_300_white_men_20_35` directory.
"""
import argparse
import os
import pathlib
import sys

try:
    from PIL import Image
except Exception:  # pragma: no cover - helpful error message
    print("Pillow is required. Install with: pip install pillow", file=sys.stderr)
    raise


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_FOLDER = os.path.join(BASE_DIR, "subset_300_white_men_20_35")
EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def find_images(folder):
    p = pathlib.Path(folder)
    for path in p.rglob("*"):
        if path.is_file() and path.suffix.lower() in EXTS:
            yield path


def convert_to_greyscale(path: pathlib.Path):
    try:
        with Image.open(path) as img:
            gray = img.convert("L")
            # Save back to same path and format. For JPEG provide reasonable quality.
            params = {}
            fmt = img.format
            if fmt and fmt.upper() in {"JPEG", "JPG"}:
                params["quality"] = 95
            gray.save(path, format=fmt, **params)
        print(f"Converted: {path}")
    except Exception as e:
        print(f"Failed to convert {path}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Convert images to greyscale in-place")
    parser.add_argument("folder", nargs="?", default=DEFAULT_FOLDER, help="Folder with images")
    args = parser.parse_args()

    folder = args.folder
    if not os.path.isdir(folder):
        print(f"Folder does not exist: {folder}", file=sys.stderr)
        sys.exit(2)

    files = list(find_images(folder))
    if not files:
        print("No images found to process.")
        return

    for p in files:
        convert_to_greyscale(p)


if __name__ == "__main__":
    main()
