#!/usr/bin/env python3

import argparse
import os
import pathlib
import sys

from PIL import Image, ImageOps


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_FOLDER = os.path.join(BASE_DIR, "subset_300_white_men_20_35")
EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

TARGET_SIZE = (64, 64)


def find_images(folder):
    p = pathlib.Path(folder)

    for path in p.rglob("*"):
        if path.is_file() and path.suffix.lower() in EXTS:
            yield path


def preprocess_image(path):
    try:
        with Image.open(path) as img:

            # Convert to greyscale
            gray = img.convert("L")

            # Resize while keeping aspect ratio
            gray.thumbnail(TARGET_SIZE, Image.Resampling.LANCZOS)

            # Create 64x64 background
            final_image = Image.new("L", TARGET_SIZE, color=0)

            # Center resized image
            x = (TARGET_SIZE[0] - gray.width) // 2
            y = (TARGET_SIZE[1] - gray.height) // 2

            final_image.paste(gray, (x, y))

            # Save
            params = {}

            fmt = img.format

            if fmt and fmt.upper() in {"JPEG", "JPG"}:
                params["quality"] = 95

            final_image.save(path, format=fmt, **params)

        print(f"Processed: {path}")

    except Exception as e:
        print(f"Failed to process {path}: {e}")


def main():

    parser = argparse.ArgumentParser(
        description="Convert images to greyscale and resize"
    )

    parser.add_argument(
        "folder",
        nargs="?",
        default=DEFAULT_FOLDER,
        help="Folder with images"
    )

    args = parser.parse_args()

    folder = args.folder

    if not os.path.isdir(folder):
        print(f"Folder does not exist: {folder}", file=sys.stderr)
        sys.exit(2)

    files = list(find_images(folder))

    if not files:
        print("No images found to process.")
        return

    print(f"Found {len(files)} images.")

    for path in files:
        preprocess_image(path)


if __name__ == "__main__":
    main()