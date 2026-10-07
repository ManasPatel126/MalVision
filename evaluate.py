"""
evaluate.py — Evaluation & Visualization Module

After training, this module:
    1.  Loads the best model checkpoint.
    2.  Runs inference on the held-out test set.
    3.  Computes per-class Precision, Recall, F1-score via scikit-learn.
    4.  Plots and saves a colour-mapped Confusion Matrix.
"""

import os
from typing import Dict, List, Tuple

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
)
import matplotlib.pyplot as plt

from config import MODEL_SAVE_DIR, RESULTS_DIR


# ──────────────────────────────────────────────────────────────────────────────
# 1.  Collect all predictions on a DataLoader
# ──────────────────────────────────────────────────────────────────────────────

@torch.no_grad()
def get_all_predictions(model: nn.Module,
                        loader: DataLoader,
                        device: torch.device
                        ) -> Tuple[np.ndarray, np.ndarray]:
    """
    Run the model over every batch in *loader* and collect the predicted
    class indices alongside the ground-truth labels.

    Returns
    -------
    all_preds  : np.ndarray of shape (N,)   — predicted class indices
    all_labels : np.ndarray of shape (N,)   — true class indices
    """
    model.eval()
    all_preds:  List[np.ndarray] = []
    all_labels: List[np.ndarray] = []

    for images, labels in loader:
        images = images.to(device, non_blocking=True)
        logits = model(images)                                # (B, C)
        preds  = logits.argmax(dim=1).cpu().numpy()           # (B,)

        all_preds.append(preds)
        all_labels.append(labels.numpy())

    return np.concatenate(all_preds), np.concatenate(all_labels)


# ──────────────────────────────────────────────────────────────────────────────
# 2.  Classification report
# ──────────────────────────────────────────────────────────────────────────────

def print_classification_report(y_true: np.ndarray,
                                y_pred: np.ndarray,
                                idx_to_class: Dict[int, str]) -> str:
    """
    Print and return the scikit-learn classification report.

    The report includes:
        • Per-class Precision, Recall, F1-score, Support
        • Macro-average  (unweighted mean across classes)
        • Weighted-average (support-weighted mean)
        • Overall accuracy

    Parameters
    ----------
    y_true       : Ground truth labels (ints)
    y_pred       : Predicted labels (ints)
    idx_to_class : dict mapping label index → family name

    Returns
    -------
    report_str : str
    """
    target_names = [idx_to_class[i] for i in sorted(idx_to_class.keys())]

    report = classification_report(
        y_true, y_pred,
        target_names=target_names,
        digits=4,                      # 4 decimal places for precision
        zero_division=0,
    )

    print("\n" + "=" * 65)
    print("  CLASSIFICATION REPORT  (Test Set)")
    print("=" * 65)
    print(report)

    # Also save to file
    os.makedirs(RESULTS_DIR, exist_ok=True)
    report_path = os.path.join(RESULTS_DIR, "classification_report.txt")
    with open(report_path, "w") as f:
        f.write(report)
    print(f"[INFO] Report saved to: {report_path}")

    return report


# ──────────────────────────────────────────────────────────────────────────────
# 3.  Confusion matrix
# ──────────────────────────────────────────────────────────────────────────────

def plot_confusion_matrix(y_true: np.ndarray,
                          y_pred: np.ndarray,
                          idx_to_class: Dict[int, str]) -> None:
    """
    Compute and plot the confusion matrix as a colour-mapped heatmap.

    Each cell (i, j) counts the number of samples whose true label is
    family_i that the model predicted as family_j.

    • Diagonal cells   → correct predictions
    • Off-diagonal cells → misclassifications (reveals which families the
      model confuses with one another)

    The plot is saved to RESULTS_DIR/confusion_matrix.png.
    """
    labels       = sorted(idx_to_class.keys())
    target_names = [idx_to_class[i] for i in labels]

    cm = confusion_matrix(y_true, y_pred, labels=labels)

    # ── Plot ─────────────────────────────────────────────────────────────
    # Dynamically size the figure based on number of classes
    n_classes = len(target_names)
    fig_size  = max(8, n_classes * 0.7)

    fig, ax = plt.subplots(figsize=(fig_size, fig_size))

    disp = ConfusionMatrixDisplay(
        confusion_matrix=cm,
        display_labels=target_names,
    )
    disp.plot(
        ax=ax,
        cmap="Blues",             # blue gradient: darker = higher count
        values_format="d",       # integer format
        xticks_rotation=45,
    )

    ax.set_title("Confusion Matrix — Malware Family Classification", fontsize=14)
    ax.set_xlabel("Predicted Family", fontsize=12)
    ax.set_ylabel("True Family", fontsize=12)

    fig.tight_layout()

    os.makedirs(RESULTS_DIR, exist_ok=True)
    save_path = os.path.join(RESULTS_DIR, "confusion_matrix.png")
    fig.savefig(save_path, dpi=150)
    plt.close(fig)
    print(f"[INFO] Confusion matrix saved to: {save_path}")


# ──────────────────────────────────────────────────────────────────────────────
# 4.  Full evaluation pipeline
# ──────────────────────────────────────────────────────────────────────────────

def evaluate_model(model: nn.Module,
                   test_loader: DataLoader,
                   idx_to_class: Dict[int, str],
                   device: torch.device) -> None:
    """
    End-to-end evaluation:
        1. Load the best checkpoint (if it exists).
        2. Run inference on the test set.
        3. Print + save the classification report.
        4. Plot + save the confusion matrix.

    Parameters
    ----------
    model        : The model architecture (weights will be loaded from disk).
    test_loader  : DataLoader for the test split.
    idx_to_class : Label index → family name mapping.
    device       : CPU or CUDA device.
    """
    # ── Load best checkpoint ─────────────────────────────────────────────
    best_model_path = os.path.join(MODEL_SAVE_DIR, "best_model.pth")
    if os.path.isfile(best_model_path):
        model.load_state_dict(torch.load(best_model_path,
                                         map_location=device,
                                         weights_only=True))
        print(f"[INFO] Loaded best model from: {best_model_path}")
    else:
        print("[WARNING] No checkpoint found -- evaluating with current weights.")

    model = model.to(device)

    # ── Inference ────────────────────────────────────────────────────────
    y_pred, y_true = get_all_predictions(model, test_loader, device)

    # ── Metrics ──────────────────────────────────────────────────────────
    test_acc = (y_pred == y_true).mean()
    print(f"\n[RESULT] Test Accuracy: {test_acc:.4f} ({test_acc:.2%})")

    print_classification_report(y_true, y_pred, idx_to_class)
    plot_confusion_matrix(y_true, y_pred, idx_to_class)
