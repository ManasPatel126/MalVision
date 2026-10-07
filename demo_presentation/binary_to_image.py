"""
binary_to_image.py — Binary-to-Image Conversion Module

Converts raw malware binary files into grayscale PNG images using the
visualisation technique introduced by Nataraj et al. (2011).

Algorithm
─────────
1.  Read every byte of the binary file → flat 1-D NumPy array of uint8
    values in [0, 255].
2.  Choose an image *width* based on the file size (see config.FILE_SIZE_TO_WIDTH).
3.  Compute the *height* = ceil(total_bytes / width).
4.  Pad the byte array with zeros so that it fills an exact (height × width)
    grid — the padding represents "no data" and appears black in the image.
5.  Reshape into a 2-D array and save as a lossless 8-bit grayscale PNG.

Why this works
──────────────
Different sections of a PE executable (code, data, resources, headers) produce
visually distinct textures when laid out as an image.  Malware from the *same*
family shares structural similarities → similar visual textures → a CNN can
learn to classify them.
"""

import os
import math
import numpy as np
from PIL import Image
from typing import Optional

from config import FILE_SIZE_TO_WIDTH, RAW_BINARIES_DIR, IMAGE_OUTPUT_DIR


def get_image_width(file_size: int) -> int:
    """
    Determine the image width for a binary of the given size.

    We iterate through the FILE_SIZE_TO_WIDTH look-up table (defined in
    config.py) and return the width paired with the *first* upper bound
    that is ≥ file_size.

    Math
    ────
    There is no single "correct" width; the heuristic balances two goals:
        • Enough columns so that structural patterns (PE sections, padding
          runs, encrypted blobs) span multiple rows and form 2-D textures.
        • Not *too* many columns, which would compress tiny files into a
          single row and destroy spatial information.

    The thresholds (10 KB → 32 px, …, >1 MB → 1024 px) are empirically
    established defaults from the malware-visualisation literature.

    Parameters
    ----------
    file_size : int
        Size of the raw binary in bytes.

    Returns
    -------
    int
        Image width in pixels.
    """
    for upper_bound, width in FILE_SIZE_TO_WIDTH:
        if file_size <= upper_bound:
            return width
    # Fallback (should never reach here because the last entry is inf)
    return 1024


def binary_to_grayscale_array(file_path: str) -> Optional[np.ndarray]:
    """
    Read a binary file and return a 2-D uint8 NumPy array representing
    a grayscale image.

    Steps
    ─────
    1. Read raw bytes → 1-D array of shape (N,), dtype=uint8.
    2. Look up the appropriate image width W from the file size N.
    3. Compute the image height H = ⌈N / W⌉.
       (We use math.ceil so that the last row is zero-padded rather than
       truncating bytes.)
    4. Pad the array to length H * W with zeros (black pixels).
    5. Reshape to (H, W).

    Parameters
    ----------
    file_path : str
        Absolute or relative path to the binary file.

    Returns
    -------
    np.ndarray or None
        2-D array of shape (H, W) with dtype uint8, or None if the file
        is empty / unreadable.
    """
    try:
        with open(file_path, "rb") as f:
            raw_bytes = f.read()
    except (IOError, OSError) as e:
        print(f"[WARNING] Could not read '{file_path}': {e}")
        return None

    # Convert to a flat numpy array of unsigned 8-bit integers
    byte_array = np.frombuffer(raw_bytes, dtype=np.uint8)

    if byte_array.size == 0:
        print(f"[WARNING] File is empty: '{file_path}'")
        return None

    file_size = byte_array.size                      # N
    width     = get_image_width(file_size)            # W
    height    = math.ceil(file_size / width)          # H = ⌈N/W⌉

    # ── Padding ──────────────────────────────────────────────────────────
    # The last row may be incomplete: we need exactly H*W values.
    # np.pad appends zeros (black) to fill the gap.
    #
    # Example:  file has 1000 bytes, width=32  →  H = ⌈1000/32⌉ = 32
    #           total pixels needed = 32*32 = 1024
    #           padding = 1024 - 1000 = 24 zeros
    padding_needed = (height * width) - file_size
    if padding_needed > 0:
        byte_array = np.pad(byte_array, (0, padding_needed), mode="constant",
                            constant_values=0)

    # Reshape into a 2-D grayscale image: rows = height, cols = width
    image_array = byte_array.reshape((height, width))
    return image_array


def save_image(image_array: np.ndarray, output_path: str) -> None:
    """
    Save a 2-D uint8 NumPy array as a lossless 8-bit grayscale PNG.

    Parameters
    ----------
    image_array : np.ndarray
        2-D array of shape (H, W), dtype uint8.
    output_path : str
        Destination file path (should end with .png).
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img = Image.fromarray(image_array, mode="L")   # "L" = 8-bit grayscale
    img.save(output_path, format="PNG")


def convert_dataset(input_dir: str = RAW_BINARIES_DIR,
                    output_dir: str = IMAGE_OUTPUT_DIR) -> None:
    """
    Walk through the *input_dir* folder tree, convert every file found
    into a grayscale PNG, and mirror the directory structure under
    *output_dir*.

    Expected input layout
    ─────────────────────
        input_dir/
        ├── family_A/
        │   ├── sample1.exe
        │   └── sample2.dll
        └── family_B/
            └── sample3.bin

    Produced output layout
    ──────────────────────
        output_dir/
        ├── family_A/
        │   ├── sample1.png
        │   └── sample2.png
        └── family_B/
            └── sample3.png
    """
    if not os.path.isdir(input_dir):
        print(f"[ERROR] Input directory not found: '{input_dir}'")
        print("        Please create it and place malware families in subfolders.")
        return

    total, success, skipped = 0, 0, 0

    for family_name in sorted(os.listdir(input_dir)):
        family_path = os.path.join(input_dir, family_name)
        if not os.path.isdir(family_path):
            continue  # skip stray files at the root level

        for file_name in sorted(os.listdir(family_path)):
            file_path = os.path.join(family_path, file_name)
            if not os.path.isfile(file_path):
                continue

            total += 1
            image_array = binary_to_grayscale_array(file_path)

            if image_array is None:
                skipped += 1
                continue

            # Build the output path: replace extension with .png
            base_name   = os.path.splitext(file_name)[0] + ".png"
            output_path = os.path.join(output_dir, family_name, base_name)
            save_image(image_array, output_path)
            success += 1

    print(f"[INFO] Conversion complete: {success}/{total} files converted "
          f"({skipped} skipped).  Output -> '{output_dir}'")


# ─────────────────────────────────────────────────────────────────────────────
# Stand-alone execution for quick testing
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    convert_dataset()
