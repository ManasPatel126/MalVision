"""
train.py — Training Loop Module

Orchestrates:
    1.  Model instantiation
    2.  Loss function & optimiser setup
    3.  Epoch-level training with mini-batch gradient descent
    4.  Per-epoch validation accuracy tracking
    5.  Learning-rate scheduling (ReduceLROnPlateau)
    6.  Early stopping & best-model checkpointing
    7.  Training history plotting (loss & accuracy curves)
"""

import os
import time
from typing import Dict, List, Tuple

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt

from config import (
    NUM_EPOCHS,
    LEARNING_RATE,
    WEIGHT_DECAY,
    MODEL_SAVE_DIR,
    RESULTS_DIR,
)


# ──────────────────────────────────────────────────────────────────────────────
# 1.  Single-epoch training step
# ──────────────────────────────────────────────────────────────────────────────

def train_one_epoch(model: nn.Module,
                    loader: DataLoader,
                    criterion: nn.Module,
                    optimizer: optim.Optimizer,
                    device: torch.device) -> Tuple[float, float]:
    """
    Run one full pass over the training set.

    For each mini-batch:
        1. Forward pass   → logits
        2. Compute loss   → CrossEntropyLoss(logits, targets)
        3. Backward pass  → compute ∂loss/∂θ for all parameters θ
        4. Optimiser step → θ ← θ − lr · ∂loss/∂θ  (simplified; Adam does more)
        5. Zero gradients → prevent accumulation across batches

    Returns
    -------
    avg_loss : float
        Mean loss over all batches.
    accuracy : float
        Fraction of correctly predicted samples.
    """
    model.train()                    # Enable dropout / BN in training mode
    running_loss    = 0.0
    correct         = 0
    total           = 0

    for batch_idx, (images, labels) in enumerate(loader):
        images = images.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)

        # ── Forward ──────────────────────────────────────────────────────
        logits = model(images)                    # (B, num_classes)
        loss   = criterion(logits, labels)        # scalar

        # ── Backward + update ────────────────────────────────────────────
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        # ── Bookkeeping ──────────────────────────────────────────────────
        running_loss += loss.item() * images.size(0)   # un-average the loss
        _, predicted  = logits.max(dim=1)               # argmax over classes
        correct      += (predicted == labels).sum().item()
        total        += images.size(0)

        if (batch_idx + 1) % 50 == 0 or (batch_idx + 1) == len(loader):
            current_acc = correct / total
            print(f"    Batch {batch_idx + 1:3d}/{len(loader)} | Loss: {loss.item():.4f} | Batch Acc: {current_acc:.1%}", flush=True)

    avg_loss = running_loss / total
    accuracy = correct / total
    return avg_loss, accuracy


# ──────────────────────────────────────────────────────────────────────────────
# 2.  Validation step
# ──────────────────────────────────────────────────────────────────────────────

@torch.no_grad()
def validate(model: nn.Module,
             loader: DataLoader,
             criterion: nn.Module,
             device: torch.device) -> Tuple[float, float]:
    """
    Evaluate the model on a validation (or test) set *without* computing
    gradients — this saves memory and time.

    Returns
    -------
    avg_loss : float
    accuracy : float
    """
    model.eval()                      # Disable dropout / use running BN stats
    running_loss = 0.0
    correct      = 0
    total        = 0

    for images, labels in loader:
        images = images.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)

        logits = model(images)
        loss   = criterion(logits, labels)

        running_loss += loss.item() * images.size(0)
        _, predicted  = logits.max(dim=1)
        correct      += (predicted == labels).sum().item()
        total        += images.size(0)

    avg_loss = running_loss / total
    accuracy = correct / total
    return avg_loss, accuracy


# ──────────────────────────────────────────────────────────────────────────────
# 3.  Full training orchestration
# ──────────────────────────────────────────────────────────────────────────────

def train_model(model: nn.Module,
                train_loader: DataLoader,
                val_loader: DataLoader,
                device: torch.device,
                num_epochs: int = NUM_EPOCHS) -> Dict[str, List[float]]:
    """
    End-to-end training loop with:
        • Adam optimiser (lr=1e-4, weight_decay=1e-5)
        • CrossEntropyLoss (= log-softmax + NLL; standard for multi-class)
        • ReduceLROnPlateau scheduler (patience=5, factor=0.5)
          — halves the LR when validation loss stalls for 5 consecutive epochs
        • Early stopping (patience=10)
          — stops training when validation loss hasn't improved for 10 epochs
        • Best-model checkpointing
          — saves model weights whenever a new best validation loss is achieved

    Parameters
    ----------
    model : nn.Module
    train_loader, val_loader : DataLoader
    device : torch.device
    num_epochs : int

    Returns
    -------
    history : dict[str, list[float]]
        Keys: "train_loss", "train_acc", "val_loss", "val_acc"
    """
    model = model.to(device)

    # ── Loss function ────────────────────────────────────────────────────
    # nn.CrossEntropyLoss expects:
    #   input  = raw logits of shape (B, C)
    #   target = class indices of shape (B,)
    # Internally it computes:  −log( softmax(logits)[target_class] )
    criterion = nn.CrossEntropyLoss()

    # ── Optimiser ────────────────────────────────────────────────────────
    optimizer = optim.Adam(model.parameters(),
                           lr=LEARNING_RATE,
                           weight_decay=WEIGHT_DECAY)

    # ── LR scheduler ────────────────────────────────────────────────────
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="min", factor=0.5, patience=5
    )

    # ── History trackers ─────────────────────────────────────────────────
    history: Dict[str, List[float]] = {
        "train_loss": [], "train_acc": [],
        "val_loss":   [], "val_acc":   [],
    }

    best_val_loss       = float("inf")
    epochs_no_improve   = 0
    early_stop_patience = 10

    os.makedirs(MODEL_SAVE_DIR, exist_ok=True)
    best_model_path = os.path.join(MODEL_SAVE_DIR, "best_model.pth")

    print("\n" + "=" * 75)
    print(f"{'Epoch':>6} | {'Train Loss':>10} | {'Train Acc':>10} | "
          f"{'Val Loss':>10} | {'Val Acc':>10} | {'Time':>6}")
    print("-" * 75)

    for epoch in range(1, num_epochs + 1):
        t0 = time.time()

        train_loss, train_acc = train_one_epoch(
            model, train_loader, criterion, optimizer, device
        )
        val_loss, val_acc = validate(
            model, val_loader, criterion, device
        )

        elapsed = time.time() - t0

        # Record history
        history["train_loss"].append(train_loss)
        history["train_acc"].append(train_acc)
        history["val_loss"].append(val_loss)
        history["val_acc"].append(val_acc)

        # Print epoch summary
        print(f"{epoch:6d} | {train_loss:10.4f} | {train_acc:9.2%} | "
              f"{val_loss:10.4f} | {val_acc:9.2%} | {elapsed:5.1f}s")

        # Step the LR scheduler based on validation loss
        scheduler.step(val_loss)

        # -- Checkpointing & early stopping -----------------------------------
        if val_loss < best_val_loss:
            best_val_loss     = val_loss
            epochs_no_improve = 0
            torch.save(model.state_dict(), best_model_path)
            print(f"       -> Saved best model (val_loss={val_loss:.4f})")
        else:
            epochs_no_improve += 1
            if epochs_no_improve >= early_stop_patience:
                print(f"\n[INFO] Early stopping at epoch {epoch} "
                      f"(no improvement for {early_stop_patience} epochs).")
                break

    print("=" * 75)
    print(f"[INFO] Best validation loss: {best_val_loss:.4f}")
    print(f"[INFO] Model checkpoint saved to: {best_model_path}")

    return history


# ──────────────────────────────────────────────────────────────────────────────
# 4.  Plot training curves
# ──────────────────────────────────────────────────────────────────────────────

def plot_training_history(history: Dict[str, List[float]]) -> None:
    """
    Generate and save two side-by-side plots:
        Left  — Training vs. Validation Loss
        Right — Training vs. Validation Accuracy

    Saved to RESULTS_DIR/training_curves.png.
    """
    os.makedirs(RESULTS_DIR, exist_ok=True)

    epochs = range(1, len(history["train_loss"]) + 1)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # ── Loss plot ────────────────────────────────────────────────────────
    ax1.plot(epochs, history["train_loss"], "b-o", markersize=3, label="Train Loss")
    ax1.plot(epochs, history["val_loss"],   "r-o", markersize=3, label="Val Loss")
    ax1.set_xlabel("Epoch")
    ax1.set_ylabel("Cross-Entropy Loss")
    ax1.set_title("Training & Validation Loss")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # ── Accuracy plot ────────────────────────────────────────────────────
    ax2.plot(epochs, history["train_acc"], "b-o", markersize=3, label="Train Acc")
    ax2.plot(epochs, history["val_acc"],   "r-o", markersize=3, label="Val Acc")
    ax2.set_xlabel("Epoch")
    ax2.set_ylabel("Accuracy")
    ax2.set_title("Training & Validation Accuracy")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    fig.tight_layout()
    save_path = os.path.join(RESULTS_DIR, "training_curves.png")
    fig.savefig(save_path, dpi=150)
    plt.close(fig)
    print(f"[INFO] Training curves saved to: {save_path}")
