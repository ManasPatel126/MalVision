"""
download_malimg.py — Download and prepare the Malimg dataset.

Downloads the Malimg dataset (grayscale malware visualization images)
from Figshare, extracts it, and reorganizes it into the expected
data/dataset/<family_name>/ structure.

The dataset contains ~9,339 images across 25 malware families.
These are SAFE grayscale images (not executable malware).
"""

import os
import sys
import zipfile
import shutil
import urllib.request
import time

DATASET_URL = "https://ndownloader.figshare.com/files/42443904"
DOWNLOAD_DIR = os.path.join("data", "downloads")
DATASET_DIR = os.path.join("data", "dataset")
ZIP_PATH = os.path.join(DOWNLOAD_DIR, "malimg_dataset.zip")


def download_with_progress(url: str, dest: str) -> None:
    """Download a file with a progress bar."""
    os.makedirs(os.path.dirname(dest), exist_ok=True)

    print(f"[INFO] Downloading from: {url}")
    print(f"[INFO] Saving to: {dest}")

    # Use urllib to handle redirects and show progress
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

    try:
        response = urllib.request.urlopen(req, timeout=300)
    except Exception as e:
        print(f"[ERROR] Download failed: {e}")
        sys.exit(1)

    total_size = response.headers.get("Content-Length")
    if total_size:
        total_size = int(total_size)
        print(f"[INFO] File size: {total_size / (1024*1024):.1f} MB")

    downloaded = 0
    chunk_size = 1024 * 256  # 256 KB chunks

    with open(dest, "wb") as f:
        while True:
            chunk = response.read(chunk_size)
            if not chunk:
                break
            f.write(chunk)
            downloaded += len(chunk)
            if total_size:
                pct = downloaded * 100 / total_size
                mb = downloaded / (1024 * 1024)
                print(f"\r  Progress: {mb:.1f} MB / {total_size/(1024*1024):.1f} MB ({pct:.0f}%)", end="", flush=True)
            else:
                mb = downloaded / (1024 * 1024)
                print(f"\r  Downloaded: {mb:.1f} MB", end="", flush=True)

    print()  # newline after progress
    print(f"[INFO] Download complete: {downloaded / (1024*1024):.1f} MB")


def extract_and_organize(zip_path: str, output_dir: str) -> None:
    """Extract all family images directly from the zip to output_dir/<family>/."""
    print(f"[INFO] Extracting images directly from {zip_path} to {output_dir} ...")

    # Clear existing synthetic/old dataset if present
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    extracted_counts = {}

    with zipfile.ZipFile(zip_path, "r") as zf:
        members = [m for m in zf.namelist() if m.lower().endswith(".png")]
        total = len(members)
        print(f"[INFO] Found {total} PNG images in archive. Extracting...")

        for idx, member in enumerate(members):
            parts = member.strip("/").split("/")
            if len(parts) < 2:
                continue
            family = parts[-2]
            filename = parts[-1]

            family_dir = os.path.join(output_dir, family)
            os.makedirs(family_dir, exist_ok=True)

            dest_file = os.path.join(family_dir, filename)
            # Avoid duplicate overwriting if same filename exists across train/val
            if not os.path.exists(dest_file):
                with zf.open(member) as src, open(dest_file, "wb") as dst:
                    shutil.copyfileobj(src, dst)
                extracted_counts[family] = extracted_counts.get(family, 0) + 1

            if (idx + 1) % 1000 == 0 or (idx + 1) == total:
                print(f"  Extracted {idx + 1}/{total} images...", flush=True)

    print("\n[INFO] Extraction complete! Family breakdown:")
    for family, count in sorted(extracted_counts.items()):
        print(f"  {family:25s}: {count} images")

    total_extracted = sum(extracted_counts.values())
    print(f"\n[INFO] Dataset ready: {total_extracted} images across "
          f"{len(extracted_counts)} families in '{output_dir}'")


def main():
    print("=" * 60)
    print("  Malimg Dataset Downloader")
    print("  (Nataraj et al. 2011 - Malware Visualization Images)")
    print("=" * 60)
    print()
    print("  This downloads SAFE grayscale images (NOT malware binaries).")
    print("  ~9,339 images across 25 malware families, ~1.2 GB zip.")
    print()

    EXPECTED_SIZE = 1295672591  # Exact byte size from Figshare API

    if os.path.exists(ZIP_PATH) and os.path.getsize(ZIP_PATH) >= EXPECTED_SIZE:
        print(f"[INFO] Complete zip already exists at {ZIP_PATH}, skipping download.")
    else:
        if os.path.exists(ZIP_PATH) and os.path.getsize(ZIP_PATH) < EXPECTED_SIZE:
            print(f"[INFO] Partial zip detected ({os.path.getsize(ZIP_PATH)/(1024*1024):.1f} MB / {EXPECTED_SIZE/(1024*1024):.1f} MB). Continuing...")
        download_with_progress(DATASET_URL, ZIP_PATH)

    extract_and_organize(ZIP_PATH, DATASET_DIR)

    print()
    print("=" * 60)
    print("  [DONE] Dataset is ready!")
    print("  Run: python main.py --skip-conversion --epochs 15")
    print("=" * 60)


if __name__ == "__main__":
    main()
