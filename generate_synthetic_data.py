"""
generate_synthetic_data.py — Create fake binary "malware" samples for testing.

Each family gets a distinct byte-pattern signature so the CNN has something
learnable.  This is purely for pipeline validation — replace with real
malware binaries for actual research.
"""

import os
import random
import numpy as np

OUTPUT_DIR = os.path.join("data", "raw_binaries")
RANDOM_SEED = 42

# Each family: (name, num_samples, size_range_bytes, dominant_byte_pattern)
FAMILIES = [
    ("trojan_agent",    60, (8_000,  40_000),  lambda rng: rng.integers(0, 80, dtype=np.uint8)),
    ("ransomware_x",    55, (15_000, 80_000),  lambda rng: rng.integers(180, 256, dtype=np.uint8)),
    ("worm_spread",     50, (5_000,  30_000),  lambda rng: rng.integers(60, 140, dtype=np.uint8)),
    ("adware_popup",    55, (10_000, 50_000),  lambda rng: rng.integers(100, 200, dtype=np.uint8)),
    ("spyware_stealth", 50, (20_000, 100_000), lambda rng: rng.integers(20, 120, dtype=np.uint8)),
    ("backdoor_net",    45, (12_000, 60_000),  lambda rng: rng.integers(140, 240, dtype=np.uint8)),
]


def generate():
    rng = np.random.default_rng(RANDOM_SEED)

    total = 0
    for family_name, num_samples, (lo, hi), pattern_fn in FAMILIES:
        family_dir = os.path.join(OUTPUT_DIR, family_name)
        os.makedirs(family_dir, exist_ok=True)

        for i in range(num_samples):
            size = int(rng.integers(lo, hi))

            # Build the full array at the correct size from the start
            data = np.empty(size, dtype=np.uint8)

            # Header region (first 10%) — uniform PE-like bytes
            header_end = size // 10
            data[:header_end] = rng.integers(0x4D, 0x5B, size=header_end, dtype=np.uint8)

            # Code section (10%–60%) — family-specific pattern + noise
            code_start = header_end
            code_end   = size * 6 // 10
            code_len   = code_end - code_start
            base = pattern_fn(rng).repeat(code_len // max(1, pattern_fn(rng).size) + 1)[:code_len]
            noise = rng.integers(-30, 30, size=code_len, dtype=np.int16)
            data[code_start:code_end] = np.clip(
                base.astype(np.int16) + noise, 0, 255
            ).astype(np.uint8)

            # Resource/data section (last 40%) — more randomness
            data[code_end:] = rng.integers(0, 256, size=size - code_end, dtype=np.uint8)

            # Periodic padding blocks (to create visible texture stripes)
            stripe_val = int(rng.integers(0, 256))
            step = int(rng.integers(500, 2000))
            for offset in range(0, size, step):
                block_len = int(rng.integers(50, 200))
                end = min(offset + block_len, size)
                data[offset:end] = stripe_val

            file_path = os.path.join(family_dir, f"sample_{i:04d}.bin")
            with open(file_path, "wb") as f:
                f.write(data.tobytes())
            total += 1

    print(f"[INFO] Generated {total} synthetic samples across "
          f"{len(FAMILIES)} families in '{OUTPUT_DIR}'")


if __name__ == "__main__":
    generate()
