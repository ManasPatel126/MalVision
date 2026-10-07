"""
config.py — Central configuration for the Malware Image Classification pipeline.

All hyperparameters, paths, and constants live here so that every other module
imports from a single source of truth.  Adjust these values to match your
hardware (GPU memory), dataset size, and experimentation needs.
"""

import os

# ──────────────────────────────────────────────────────────────────────────────
# 1.  PATH CONFIGURATION
# ──────────────────────────────────────────────────────────────────────────────
# RAW_BINARIES_DIR:
#   Root folder that contains *raw malware binaries* organized by family.
#   Expected layout:
#       raw_binaries/
#       ├── family_A/
#       │   ├── sample_001.exe
#       │   └── sample_002.dll
#       ├── family_B/
#       │   └── sample_003.bin
#       └── ...
RAW_BINARIES_DIR = os.path.join("data", "raw_binaries")

# IMAGE_OUTPUT_DIR:
#   Where the converted grayscale .png images will be saved.
#   The script mirrors the family-subfolder structure automatically:
#       dataset/
#       ├── family_A/
#       │   ├── sample_001.png
#       │   └── sample_002.png
#       └── family_B/
#           └── sample_003.png
IMAGE_OUTPUT_DIR = os.path.join("data", "dataset")

# MODEL_SAVE_DIR:
#   Where trained model checkpoints (.pth files) are persisted.
MODEL_SAVE_DIR = os.path.join("outputs", "models")

# RESULTS_DIR:
#   Where evaluation artefacts (confusion matrix, classification report) land.
RESULTS_DIR = os.path.join("outputs", "results")

# ──────────────────────────────────────────────────────────────────────────────
# 2.  BINARY → IMAGE CONVERSION SETTINGS
# ──────────────────────────────────────────────────────────────────────────────
# FILE_SIZE_TO_WIDTH defines the mapping from *raw binary file size* (in bytes)
# to the *width* (in pixels) of the generated grayscale image.
#
# Rationale (from the seminal Nataraj et al. 2011 paper):
#   • Smaller executables yield very few bytes; using a large width would
#     produce an image with very few rows, losing spatial texture.
#   • Larger executables benefit from wider images so that visual patterns
#     (code sections, data sections, padding) remain discernible.
#
# The tuples are (upper_bound_bytes, image_width).  We iterate through them
# in order and pick the *first* entry whose upper bound exceeds the file size.
FILE_SIZE_TO_WIDTH = [
    (10 * 1024,         32),    # ≤  10 KB  →  32 px wide
    (30 * 1024,         64),    # ≤  30 KB  →  64 px wide
    (60 * 1024,        128),    # ≤  60 KB  → 128 px wide
    (100 * 1024,       256),    # ≤ 100 KB  → 256 px wide
    (200 * 1024,       384),    # ≤ 200 KB  → 384 px wide
    (500 * 1024,       512),    # ≤ 500 KB  → 512 px wide
    (1000 * 1024,      768),    # ≤   1 MB  → 768 px wide
    (float("inf"),    1024),    # >   1 MB  → 1024 px wide
]

# ──────────────────────────────────────────────────────────────────────────────
# 3.  DATA PIPELINE / PREPROCESSING
# ──────────────────────────────────────────────────────────────────────────────
# Standard input size for the CNN.  224×224 is the canonical ImageNet size and
# works well with pretrained ResNet / MobileNet backbones.
IMAGE_SIZE = (224, 224)

# Dataset split ratios.  Must sum to 1.0.
TRAIN_RATIO = 0.70
VAL_RATIO   = 0.15
TEST_RATIO  = 0.15

# Random seed for reproducible splits and weight initialization.
RANDOM_SEED = 42

# ──────────────────────────────────────────────────────────────────────────────
# 4.  TRAINING HYPERPARAMETERS
# ──────────────────────────────────────────────────────────────────────────────
BATCH_SIZE     = 32
NUM_EPOCHS     = 30
LEARNING_RATE  = 1e-4      # Adam's default is 1e-3; 1e-4 is safer for fine-tuning
WEIGHT_DECAY   = 1e-5      # L2 regularisation to curb over-fitting
NUM_WORKERS    = 0         # DataLoader worker threads (set to 0 on Windows if issues)

# ──────────────────────────────────────────────────────────────────────────────
# 5.  MODEL SETTINGS
# ──────────────────────────────────────────────────────────────────────────────
# USE_PRETRAINED:
#   If True  → load ImageNet-pretrained ResNet-18 and adapt the first conv
#              layer to accept 1-channel (grayscale) input.
#   If False → train the same architecture completely from scratch.
USE_PRETRAINED = True

# MODEL_NAME: backbone architecture tag (currently only "resnet18" is wired up,
# but extending to "resnet50", "mobilenet_v2", etc. is straightforward).
MODEL_NAME = "resnet18"
