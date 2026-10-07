"""
explain.py — Explainability & Interpretability via Grad-CAM

Implements Gradient-weighted Class Activation Mapping (Grad-CAM) to explain
why the CNN classified a given binary or image as a specific malware family.

Visual Output:
    Saves a 3-panel visualization:
        1. Original Grayscale Binary Texture (Byteplot)
        2. Grad-CAM Activation Heatmap (Highlights key decision regions)
        3. Color-overlaid Texture (Shows exactly which PE sections triggered the detection)

Usage:
    python explain.py --image data/dataset/Allaple.A/sample.png
    python explain.py --file C:/Windows/System32/cmd.exe
"""

import os
import argparse
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.cm as cm

from binary_to_image import binary_to_grayscale_array, save_image, get_image_width
from model import build_model
from config import IMAGE_SIZE, MODEL_SAVE_DIR
from predict import get_class_labels, load_trained_model, preprocess_image


class GradCAM:
    """
    Grad-CAM implementation for ResNet-18 backbones.
    Hooks into the final convolutional layer (layer4) to extract feature maps
    and gradients.
    """
    def __init__(self, model: torch.nn.Module, target_layer):
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        self._register_hooks()

    def _register_hooks(self):
        def forward_hook(module, input, output):
            self.activations = output.detach()

        def backward_hook(module, grad_in, grad_out):
            self.gradients = grad_out[0].detach()

        self.target_layer.register_forward_hook(forward_hook)
        self.target_layer.register_full_backward_hook(backward_hook)

    def generate_cam(self, input_tensor: torch.Tensor, target_class: int = None) -> np.ndarray:
        self.model.eval()
        self.model.zero_grad()

        # Forward pass
        logits = self.model(input_tensor)
        if target_class is None:
            target_class = logits.argmax(dim=1).item()

        score = logits[0, target_class]
        score.backward()

        # Global average pooling of gradients: weights alpha_k
        pooled_gradients = torch.mean(self.gradients, dim=[0, 2, 3])  # (C,)

        # Linear combination of activations weighted by gradients
        cam = torch.zeros(self.activations.shape[2:], dtype=torch.float32)
        for i, w in enumerate(pooled_gradients):
            cam += w * self.activations[0, i, :, :]

        # Apply ReLU to retain features that have a positive influence on the class
        cam = F.relu(cam)

        # Normalize between 0 and 1
        cam_np = cam.cpu().numpy()
        if cam_np.max() > 0:
            cam_np = (cam_np - cam_np.min()) / (cam_np.max() - cam_np.min())
        else:
            cam_np = np.zeros_like(cam_np)

        return cam_np, target_class, float(score.item())


def generate_explanation(input_path: str, output_path: str = None):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    idx_to_class = get_class_labels()
    num_classes = len(idx_to_class)

    checkpoint_path = os.path.join(MODEL_SAVE_DIR, "best_model.pth")
    model = load_trained_model(checkpoint_path, num_classes, device)

    base_name = os.path.basename(input_path)
    file_ext = os.path.splitext(input_path)[1].lower()

    if file_ext in [".png", ".jpg", ".jpeg", ".bmp"]:
        pil_img = Image.open(input_path).convert("L")
    else:
        arr = binary_to_grayscale_array(input_path)
        if arr is None:
            print(f"[ERROR] Failed to convert binary file: {input_path}")
            return
        pil_img = Image.fromarray(arr, mode="L")

    # Resize image for overlay
    vis_img = pil_img.resize(IMAGE_SIZE, Image.Resampling.BILINEAR)
    vis_arr = np.array(vis_img) / 255.0

    input_tensor = preprocess_image(pil_img).to(device)

    # Initialize GradCAM on ResNet-18 layer4
    grad_cam = GradCAM(model, model.layer4)
    cam_heatmap, target_class, score = grad_cam.generate_cam(input_tensor)

    # Resize heatmap to match image size (224x224)
    cam_pil = Image.fromarray(np.uint8(255 * cam_heatmap)).resize(IMAGE_SIZE, Image.Resampling.BICUBIC)
    cam_resized = np.array(cam_pil) / 255.0

    # Colorize heatmap with 'jet' colormap
    try:
        jet = plt.colormaps["jet"]
    except AttributeError:
        jet = cm.get_cmap("jet")
    colored_heatmap = jet(cam_resized)[:, :, :3]  # Drop alpha

    # Overlay: 60% original image + 40% heatmap
    vis_rgb = np.stack([vis_arr] * 3, axis=-1)
    overlay = 0.6 * vis_rgb + 0.4 * colored_heatmap
    overlay = np.clip(overlay, 0, 1)

    predicted_family = idx_to_class.get(target_class, f"Class {target_class}")

    # Plot 3-panel explanation figure
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    axes[0].imshow(vis_arr, cmap="gray")
    axes[0].set_title(f"Original Byteplot\n{base_name}", fontsize=11)
    axes[0].axis("off")

    axes[1].imshow(cam_resized, cmap="jet")
    axes[1].set_title(f"Grad-CAM Heatmap\n(Activation Intensity)", fontsize=11)
    axes[1].axis("off")

    axes[2].imshow(overlay)
    axes[2].set_title(f"Predicted: {predicted_family}\nKey Structural Decision Regions", fontsize=11, fontweight="bold")
    axes[2].axis("off")

    plt.suptitle(f"CNN Model Interpretability via Grad-CAM: {base_name}", fontsize=14, fontweight="bold")
    plt.tight_layout()

    if output_path is None:
        out_dir = os.path.join("outputs", "explanations")
        os.makedirs(out_dir, exist_ok=True)
        output_path = os.path.join(out_dir, f"{os.path.splitext(base_name)[0]}_gradcam.png")

    fig.savefig(output_path, dpi=150)
    plt.close(fig)

    print(f"\n[INFO] Grad-CAM explanation saved to: {output_path}")
    print(f"  Target Sample:     {base_name}")
    print(f"  Predicted Family:  {predicted_family}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Explain Malware CNN predictions with Grad-CAM")
    parser.add_argument("--image", "-i", type=str, help="Path to grayscale image (.png)")
    parser.add_argument("--file", "-f", type=str, help="Path to raw binary (.exe, .dll, .bin)")
    parser.add_argument("--output", "-o", type=str, help="Output destination for explanation figure")
    args = parser.parse_args()

    target = args.image or args.file
    if not target:
        # Default sample from dataset
        import glob
        samples = glob.glob(os.path.join("data", "dataset", "Allaple.A", "*.png"))
        if samples:
            target = samples[0]
            print(f"[INFO] No target specified. Running demo on: {target}")
        else:
            parser.print_help()
            return

    generate_explanation(target, args.output)


if __name__ == "__main__":
    main()
