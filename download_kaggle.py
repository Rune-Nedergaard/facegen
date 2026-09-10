import kagglehub
import os
import shutil
import random
import pathlib
import glob

# Configuration
DATASET_SLUG = "abhikjha/utk-face-cropped"
SAMPLE_SIZE = 300
MIN_AGE, MAX_AGE = 20, 35
TARGET_GENDER = 0  # 0=male, 1=female
TARGET_RACE = 0    # 0=white
RANDOM_SEED = 42
OUT_DIR = "subset_300_white_men_20_35"


def download_dataset():
	path = kagglehub.dataset_download(DATASET_SLUG)
	print("Path to dataset files:", path)
	return path


def find_image_files(root):
	p = pathlib.Path(root)
	files = []
	for pat in ("**/*.jpg", "**/*.jpeg", "**/*.png"):
		files.extend([str(x) for x in p.glob(pat)])
	return files


def parse_utk_filename(fname):
	base = os.path.basename(fname)
	parts = base.split("_")
	try:
		age = int(parts[0])
		gender = int(parts[1])
		race = int(parts[2])
		return age, gender, race
	except Exception:
		return None


def select_and_copy(images_root):
	files = find_image_files(images_root)
	random.seed(RANDOM_SEED)
	matches = []
	for f in files:
		parsed = parse_utk_filename(f)
		if not parsed:
			continue
		age, gender, race = parsed
		if MIN_AGE <= age <= MAX_AGE and gender == TARGET_GENDER and race == TARGET_RACE:
			matches.append(f)

	if not matches:
		print("No matching images found under:", images_root)
		return 0

	if len(matches) < SAMPLE_SIZE:
		print(f"Found only {len(matches)} matching images; will copy all of them.")
		sampled = matches
	else:
		sampled = random.sample(matches, SAMPLE_SIZE)

	os.makedirs(OUT_DIR, exist_ok=True)
	for src in sampled:
		dst = os.path.join(OUT_DIR, os.path.basename(src))
		shutil.copy2(src, dst)

	print(f"Copied {len(sampled)} images to {OUT_DIR}")
	return len(sampled)


def main():
	path = download_dataset()
	p = pathlib.Path(path)
	images_root = str(p) if p.is_dir() else str(p.parent)

	copied = select_and_copy(images_root)
	if copied < SAMPLE_SIZE:
		print("Warning: fewer than requested samples were copied.")


if __name__ == "__main__":
	main()