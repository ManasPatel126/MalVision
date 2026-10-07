"""
model.py — CNN Model Architecture Module

Provides two model options:

    1.  **Transfer Learning (default)**: A pretrained ResNet-18 backbone whose
        first convolutional layer is surgically modified to accept 1-channel
        (grayscale) input, and whose final fully-connected head is replaced
        to output N malware-family logits.

    2.  **Custom lightweight CNN**: A from-scratch network with 4 conv blocks
        followed by global average pooling and a linear classifier.  Useful
        when the dataset is small and a heavy pretrained model might overfit.

Both models are returned by the factory function `build_model(num_classes)`.
"""

import torch
import torch.nn as nn
from torchvision import models

from config import USE_PRETRAINED, MODEL_NAME


# ──────────────────────────────────────────────────────────────────────────────
# 1.  Custom Lightweight CNN (from scratch)
# ──────────────────────────────────────────────────────────────────────────────

class MalwareCNN(nn.Module):
    """
    A compact CNN designed for texture-based classification.

    Architecture
    ────────────
    4 convolutional blocks, each consisting of:
        Conv2d → BatchNorm → ReLU → MaxPool(2×2)

    Followed by:
        Global Average Pooling (GAP) → Dropout → Linear(num_classes)

    Using GAP instead of flattening makes the model agnostic to the spatial
    dimensions of the feature maps, and drastically reduces parameter count.

    Channel progression:  1 → 32 → 64 → 128 → 256
    After 4 rounds of 2×2 max-pooling on a 224×224 input:
        224 → 112 → 56 → 28 → 14  (spatial dimension of the last feature map)
    GAP reduces (B, 256, 14, 14) → (B, 256).

    Parameters
    ----------
    num_classes : int
        Number of malware family labels.
    """

    def __init__(self, num_classes: int):
        super().__init__()

        def conv_block(in_ch: int, out_ch: int) -> nn.Sequential:
            """Helper: Conv3×3 → BN → ReLU → MaxPool2×2."""
            return nn.Sequential(
                nn.Conv2d(in_ch, out_ch, kernel_size=3, padding=1),
                nn.BatchNorm2d(out_ch),
                nn.ReLU(inplace=True),
                nn.MaxPool2d(kernel_size=2, stride=2),
            )

        self.features = nn.Sequential(
            conv_block(1,   32),     # (B, 1, 224, 224)   → (B, 32, 112, 112)
            conv_block(32,  64),     # (B, 32, 112, 112)  → (B, 64, 56, 56)
            conv_block(64, 128),     # (B, 64, 56, 56)    → (B, 128, 28, 28)
            conv_block(128, 256),    # (B, 128, 28, 28)   → (B, 256, 14, 14)
        )

        self.classifier = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),          # (B, 256, 14, 14) → (B, 256, 1, 1)
            nn.Flatten(),                     # (B, 256)
            nn.Dropout(p=0.5),
            nn.Linear(256, num_classes),      # (B, num_classes)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.features(x)
        x = self.classifier(x)
        return x                              # raw logits (no softmax)


# ──────────────────────────────────────────────────────────────────────────────
# 2.  Transfer-Learning Model (pretrained ResNet-18)
# ──────────────────────────────────────────────────────────────────────────────

def _build_resnet18_grayscale(num_classes: int,
                              pretrained: bool = True) -> nn.Module:
    """
    Adapt a pretrained ResNet-18 to accept 1-channel grayscale input.

    Modification details
    ────────────────────
    • The original `conv1` is Conv2d(3, 64, 7×7, stride=2, padding=3).
      We replace it with Conv2d(**1**, 64, 7×7, stride=2, padding=3).
    • To preserve the pretrained knowledge, we *average* the 3 input-channel
      weight tensor along dim=1 (the RGB axis) and use the result as the
      single-channel kernel.
      Mathematically:  W_gray = (1/3) Σ_c W_rgb[:, c, :, :]
      This is equivalent to treating a grayscale image as an RGB image where
      R = G = B = gray, then averaging the per-channel convolutions.
    • The final fully-connected layer `fc` is replaced with a new Linear
      layer that outputs `num_classes` logits.

    Parameters
    ----------
    num_classes : int
        Number of output classes.
    pretrained : bool
        Whether to load ImageNet weights.

    Returns
    -------
    nn.Module
        Modified ResNet-18 model.
    """
    if pretrained:
        weights = models.ResNet18_Weights.DEFAULT
        model = models.resnet18(weights=weights)
    else:
        model = models.resnet18(weights=None)

    # ── Adapt first conv layer: 3-channel → 1-channel ────────────────────
    old_conv = model.conv1                          # (64, 3, 7, 7)
    new_conv = nn.Conv2d(
        in_channels=1,                              # grayscale
        out_channels=old_conv.out_channels,         # 64
        kernel_size=old_conv.kernel_size,            # (7, 7)
        stride=old_conv.stride,                     # (2, 2)
        padding=old_conv.padding,                   # (3, 3)
        bias=(old_conv.bias is not None),
    )

    if pretrained:
        # Average pretrained RGB weights → single channel
        # old_conv.weight shape: (64, 3, 7, 7) → mean over dim=1 → (64, 1, 7, 7)
        with torch.no_grad():
            new_conv.weight = nn.Parameter(
                old_conv.weight.mean(dim=1, keepdim=True)
            )

    model.conv1 = new_conv

    # ── Replace the classification head ──────────────────────────────────
    in_features = model.fc.in_features              # 512 for ResNet-18
    model.fc = nn.Sequential(
        nn.Dropout(p=0.5),
        nn.Linear(in_features, num_classes),
    )

    return model


# ──────────────────────────────────────────────────────────────────────────────
# 3.  Model factory
# ──────────────────────────────────────────────────────────────────────────────

def build_model(num_classes: int) -> nn.Module:
    """
    Factory function that returns the configured model.

    Reads config.USE_PRETRAINED and config.MODEL_NAME to decide which
    architecture to instantiate.

    Parameters
    ----------
    num_classes : int
        Number of malware family labels.

    Returns
    -------
    nn.Module
        The model, ready for .to(device).
    """
    if USE_PRETRAINED and MODEL_NAME == "resnet18":
        print(f"[INFO] Building pretrained ResNet-18 (1-ch grayscale) "
              f"-> {num_classes} classes")
        return _build_resnet18_grayscale(num_classes, pretrained=True)
    else:
        print(f"[INFO] Building custom MalwareCNN -> {num_classes} classes")
        return MalwareCNN(num_classes)


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Quick shape check
    m = build_model(num_classes=10)
    dummy = torch.randn(2, 1, 224, 224)
    out = m(dummy)
    print(f"Input:  {dummy.shape}")
    print(f"Output: {out.shape}")       # Expected: (2, 10)
    total_params = sum(p.numel() for p in m.parameters())
    print(f"Total parameters: {total_params:,}")
