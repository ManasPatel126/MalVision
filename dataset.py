"""
dataset.py — Data Pipeline & Preprocessing Module

Responsibilities
────────────────
1.  Discover all grayscale .png images under the dataset directory, where each
    subfolder name is a malware family label.
2.  Split the dataset into training / validation / testing subsets with
    *stratification* (so that each family is proportionally represented in
    every split).
3.  Apply runtime transforms:
        • Resize to IMAGE_SIZE (default 224×224)
        • Convert to a single-channel tensor in [0, 1]
        • Normalise with mean=0.5, std=0.5 → values in [−1, 1]
    Training images additionally receive random augmentation (horizontal flip,
    slight rotation) to improve generalisation.
4.  Expose PyTorch DataLoaders ready for the training loop.
"""

import os
from typing import Tuple, Dict, List

import numpy as np
from PIL import Image
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms

from config import (
    IMAGE_OUTPUT_DIR,
    IMAGE_SIZE,
    TRAIN_RATIO,
    VAL_RATIO,
    TEST_RATIO,
    BATCH_SIZE,
    NUM_WORKERS,
    RANDOM_SEED,
)


# ──────────────────────────────────────────────────────────────────────────────
# 1.  Custom PyTorch Dataset
# ──────────────────────────────────────────────────────────────────────────────

class MalwareImageDataset(Dataset):
    """
    A PyTorch Dataset that loads grayscale malware-visualisation images.

    Each sample is a tuple (image_tensor, label_index) where:
        • image_tensor has shape (1, H, W) after transforms
        • label_index  is an integer in [0, num_classes)

    Parameters
    ----------
    image_paths : list[str]
        Absolute / relative paths to the .png images.
    labels : list[int]
        Corresponding integer labels.
    transform : torchvision.transforms.Compose, optional
        Preprocessing + augmentation pipeline.
    """

    def __init__(self, image_paths: List[str], labels: List[int],
                 transform=None):
        self.image_paths = image_paths
        self.labels      = labels
        self.transform   = transform

    def __len__(self) -> int:
        return len(self.image_paths)

    def __getitem__(self, idx: int):
        # Load as 8-bit grayscale ("L" mode in PIL)
        image = Image.open(self.image_paths[idx]).convert("L")

        if self.transform:
            image = self.transform(image)

        label = self.labels[idx]
        return image, label


# ──────────────────────────────────────────────────────────────────────────────
# 2.  Transforms
# ──────────────────────────────────────────────────────────────────────────────

def get_train_transforms() -> transforms.Compose:
    """
    Augmentation + preprocessing for the *training* split.

    Pipeline
    ────────
    1. Resize → IMAGE_SIZE (bilinear interpolation keeps textures smooth).
    2. RandomHorizontalFlip (p=0.5) — a lightweight augmentation that does
       not distort the malware texture structure.
    3. RandomRotation(±5°) — small rotation to teach the model translation
       invariance without corrupting section boundaries.
    4. ToTensor() — converts PIL Image (H, W) → tensor (1, H, W) in [0, 1].
    5. Normalize(mean=0.5, std=0.5) — linearly maps [0, 1] → [−1, 1].
       This centres activations around zero, which speeds up convergence.
    """
    return transforms.Compose([
        transforms.Resize(IMAGE_SIZE),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(degrees=5),
        transforms.ToTensor(),                           # (1, 224, 224)
        transforms.Normalize(mean=[0.5], std=[0.5]),     # → [−1, 1]
    ])


def get_eval_transforms() -> transforms.Compose:
    """
    Deterministic preprocessing for validation / test splits.

    No augmentation — we want reproducible metrics.
    """
    return transforms.Compose([
        transforms.Resize(IMAGE_SIZE),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5], std=[0.5]),
    ])


# ──────────────────────────────────────────────────────────────────────────────
# 3.  Dataset discovery & splitting
# ──────────────────────────────────────────────────────────────────────────────

def discover_samples(dataset_dir: str = IMAGE_OUTPUT_DIR
                     ) -> Tuple[List[str], List[int], Dict[int, str]]:
    """
    Walk the dataset directory and collect (path, label) pairs.

    Parameters
    ----------
    dataset_dir : str
        Root folder whose immediate subfolders are malware family names.

    Returns
    -------
    image_paths : list[str]
        Paths to all discovered .png images.
    labels : list[int]
        Integer-encoded family labels (alphabetically sorted).
    idx_to_class : dict[int, str]
        Mapping from label index → human-readable family name.
    """
    image_paths: List[str] = []
    labels:      List[int] = []

    # Sort family names for deterministic label encoding
    family_names = sorted([
        d for d in os.listdir(dataset_dir)
        if os.path.isdir(os.path.join(dataset_dir, d))
    ])

    if not family_names:
        raise FileNotFoundError(
            f"No family subfolders found in '{dataset_dir}'.  "
            "Run binary_to_image.py first or check the path."
        )

    class_to_idx = {name: idx for idx, name in enumerate(family_names)}
    idx_to_class = {idx: name for name, idx in class_to_idx.items()}

    for family_name in family_names:
        family_dir = os.path.join(dataset_dir, family_name)
        for fname in sorted(os.listdir(family_dir)):
            if fname.lower().endswith(".png"):
                image_paths.append(os.path.join(family_dir, fname))
                labels.append(class_to_idx[family_name])

    print(f"[INFO] Discovered {len(image_paths)} images across "
          f"{len(family_names)} families.")
    for idx, name in idx_to_class.items():
        count = labels.count(idx)
        print(f"       {idx}: {name} ({count} samples)")

    return image_paths, labels, idx_to_class


def split_dataset(image_paths: List[str], labels: List[int]
                  ) -> Tuple[List[str], List[int],
                             List[str], List[int],
                             List[str], List[int]]:
    """
    Stratified split into train / val / test subsets.

    Strategy
    ────────
    We perform two successive stratified splits:
        1.  Separate *test* from the rest:
                test_fraction  = TEST_RATIO                        (0.15)
                rest_fraction  = 1 − TEST_RATIO                   (0.85)
        2.  From the rest, separate *val*:
                val_fraction   = VAL_RATIO / (TRAIN_RATIO + VAL_RATIO)
                               = 0.15 / 0.85 ≈ 0.1765
            So that the final proportions are exactly 70 / 15 / 15.

    Stratification ensures every family appears in every split in roughly
    the same proportion, which is critical for balanced evaluation metrics.

    Returns
    -------
    (train_paths, train_labels,
     val_paths,   val_labels,
     test_paths,  test_labels)
    """
    # ── First split: separate out the test set ────────────────────────────
    rest_paths, test_paths, rest_labels, test_labels = train_test_split(
        image_paths, labels,
        test_size=TEST_RATIO,
        stratify=labels,
        random_state=RANDOM_SEED,
    )

    # ── Second split: from the remainder, carve out validation ───────────
    val_fraction = VAL_RATIO / (TRAIN_RATIO + VAL_RATIO)

    train_paths, val_paths, train_labels, val_labels = train_test_split(
        rest_paths, rest_labels,
        test_size=val_fraction,
        stratify=rest_labels,
        random_state=RANDOM_SEED,
    )

    print(f"[INFO] Split sizes -> Train: {len(train_paths)}, "
          f"Val: {len(val_paths)}, Test: {len(test_paths)}")

    return (train_paths, train_labels,
            val_paths,   val_labels,
            test_paths,  test_labels)


# ──────────────────────────────────────────────────────────────────────────────
# 4.  DataLoader factory
# ──────────────────────────────────────────────────────────────────────────────

def get_dataloaders(dataset_dir: str = IMAGE_OUTPUT_DIR
                    ) -> Tuple[DataLoader, DataLoader, DataLoader,
                               Dict[int, str], int]:
    """
    End-to-end convenience function: discover → split → wrap in DataLoaders.

    Returns
    -------
    train_loader : DataLoader
    val_loader   : DataLoader
    test_loader  : DataLoader
    idx_to_class : dict[int, str]
    num_classes  : int
    """
    image_paths, labels, idx_to_class = discover_samples(dataset_dir)

    (train_paths, train_labels,
     val_paths,   val_labels,
     test_paths,  test_labels) = split_dataset(image_paths, labels)

    # Build Dataset objects with appropriate transforms
    train_ds = MalwareImageDataset(train_paths, train_labels,
                                   transform=get_train_transforms())
    val_ds   = MalwareImageDataset(val_paths,   val_labels,
                                   transform=get_eval_transforms())
    test_ds  = MalwareImageDataset(test_paths,  test_labels,
                                   transform=get_eval_transforms())

    # Build DataLoaders
    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True,
                              num_workers=NUM_WORKERS, pin_memory=True)
    val_loader   = DataLoader(val_ds,   batch_size=BATCH_SIZE, shuffle=False,
                              num_workers=NUM_WORKERS, pin_memory=True)
    test_loader  = DataLoader(test_ds,  batch_size=BATCH_SIZE, shuffle=False,
                              num_workers=NUM_WORKERS, pin_memory=True)

    num_classes = len(idx_to_class)

    return train_loader, val_loader, test_loader, idx_to_class, num_classes


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Quick sanity check: discover images and print split sizes
    train_loader, val_loader, test_loader, idx_to_class, n = get_dataloaders()
    print(f"\nNum classes: {n}")
    for images, labels in train_loader:
        print(f"Batch shape: {images.shape}, Labels: {labels[:8]}")
        break
