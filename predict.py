"""
predict.py — Inference & Malware Classification Engine

Classifies any given file (either raw binary .exe/.dll/.bin or pre-converted .png image)
using the trained ResNet-18 model checkpoint (outputs/models/best_model.pth).

Workflow:
    1. If input is a raw binary (.exe, .dll, .bin):
       - Reads byte-by-byte and converts to 2D grayscale image using dynamic width heuristics.
       - Saves the visualization to outputs/predictions/
    2. Resizes to 224x224 and normalizes with mean=0.5, std=0.5.
    3. Runs forward pass through trained ResNet-18 model.
    4. Computes Softmax probabilities for all 26 malware families.
    5. Displays Top-K predictions with confidence scores and threat summary.

Usage:
    python predict.py --file path/to/suspicious_sample.exe
    python predict.py --image path/to/sample.png --top-k 5
"""

import os
import argparse
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms

from binary_to_image import binary_to_grayscale_array, save_image, get_image_width
from model import build_model
from config import IMAGE_SIZE, MODEL_SAVE_DIR, IMAGE_OUTPUT_DIR


def get_class_labels(dataset_dir: str = IMAGE_OUTPUT_DIR):
    """Retrieve alphabetically sorted family class names."""
    if os.path.isdir(dataset_dir):
        families = sorted([
            d for d in os.listdir(dataset_dir)
            if os.path.isdir(os.path.join(dataset_dir, d))
        ])
        if families:
            return {idx: name for idx, name in enumerate(families)}

    # Fallback to standard 26 Malimg families
    default_classes = [
        "Adialer.C", "Agent.FYI", "Allaple.A", "Allaple.L", "Alueron.gen!J",
        "Autorun.K", "C2LOP.P", "C2LOP.gen!g", "Dialplatform.B", "Dontovo.A",
        "Fakerean", "Instantaccess", "Lolyda.AA1", "Lolyda.AA2", "Lolyda.AA3",
        "Lolyda.AT", "Malex.gen!J", "Obfuscator.AD", "Rbot!gen", "Rbotigen",
        "Skintrim.N", "Swizzor.gen!E", "Swizzor.gen!I", "VB.AT", "Wintrim.BX", "Yuner.A"
    ]
    return {idx: name for idx, name in enumerate(default_classes)}


def load_trained_model(model_path: str, num_classes: int, device: torch.device):
    """Load model architecture and checkpoint weights."""
    model = build_model(num_classes)
    if os.path.isfile(model_path):
        state_dict = torch.load(model_path, map_location=device, weights_only=True)
        model.load_state_dict(state_dict)
        print(f"[INFO] Loaded trained weights from: {model_path}")
    else:
        raise FileNotFoundError(f"Checkpoint not found at: {model_path}. Run training first.")
    model.to(device)
    model.eval()
    return model


def preprocess_image(pil_image: Image.Image) -> torch.Tensor:
    """Preprocess a grayscale PIL image for CNN inference."""
    transform = transforms.Compose([
        transforms.Resize(IMAGE_SIZE),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5], std=[0.5]),
    ])
    tensor = transform(pil_image.convert("L"))
    return tensor.unsqueeze(0)  # Add batch dimension: (1, 1, 224, 224)


def predict(input_path: str, top_k: int = 5, save_texture: bool = True):
    """
    Classify a suspicious file and print top-k confidence predictions.
    """
    if not os.path.exists(input_path):
        print(f"[ERROR] File not found: '{input_path}'")
        return

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    idx_to_class = get_class_labels()
    num_classes = len(idx_to_class)

    checkpoint_path = os.path.join(MODEL_SAVE_DIR, "best_model.pth")
    model = load_trained_model(checkpoint_path, num_classes, device)

    out_dir = os.path.join("outputs", "predictions")
    os.makedirs(out_dir, exist_ok=True)

    base_name = os.path.basename(input_path)
    file_ext = os.path.splitext(input_path)[1].lower()

    # Determine if input is raw binary or existing image
    if file_ext in [".png", ".jpg", ".jpeg", ".bmp"]:
        pil_img = Image.open(input_path)
        img_source = "Pre-rendered Image"
        texture_path = input_path
    else:
        # Convert raw binary to 2D grayscale image
        img_source = "Raw Binary (Byteplot Conversion)"
        file_size = os.path.getsize(input_path)
        width = get_image_width(file_size)
        arr = binary_to_grayscale_array(input_path)

        if arr is None:
            print(f"[ERROR] Failed to convert binary file '{input_path}'")
            return

        pil_img = Image.fromarray(arr, mode="L")
        texture_path = os.path.join(out_dir, f"{os.path.splitext(base_name)[0]}_texture.png")
        save_image(arr, texture_path)
        print(f"[INFO] Raw binary ({file_size:,} bytes, width {width}px) converted to texture: {texture_path}")

    # Preprocess
    input_tensor = preprocess_image(pil_img).to(device)

    # Inference
    with torch.no_grad():
        logits = model(input_tensor)
        probs = F.softmax(logits, dim=1).squeeze(0).cpu().numpy()

    # Top-K indices
    top_indices = np.argsort(probs)[::-1][:top_k]

    # Display results
    print("\n" + "=" * 65)
    print("  MALWARE CLASSIFICATION REPORT")
    print("=" * 65)
    print(f"  Target Sample:     {base_name}")
    print(f"  Input Type:        {img_source}")
    print(f"  Model Architecture: ResNet-18 (Grayscale, 26 Families)")
    print(f"  Device:            {device}")
    print("-" * 65)
    print(f"  {'Rank':<5} | {'Predicted Family':<24} | {'Confidence':<12} | {'Visual Bar'}")
    print("-" * 65)

    top_family = idx_to_class[top_indices[0]]
    top_conf = probs[top_indices[0]]

    for rank, idx in enumerate(top_indices, start=1):
        family = idx_to_class[idx]
        conf = probs[idx]
        bar_len = int(conf * 25)
        bar = "#" * bar_len + "-" * (25 - bar_len)
        print(f"  {rank:<5} | {family:<24} | {conf:>8.2%}    | [{bar}]")

    print("=" * 65)
    print(f"  PRIMARY VERDICT:  {top_family.upper()} ({top_conf:.2%} confidence)")

    if top_conf > 0.85:
        threat_level = "CRITICAL / HIGH CONFIDENCE"
    elif top_conf > 0.60:
        threat_level = "SUSPICIOUS / MEDIUM CONFIDENCE"
    else:
        threat_level = "INCONCLUSIVE / LOW CONFIDENCE (Variant/Unseen Family)"

    print(f"  THREAT ASSESSMENT: {threat_level}")
    print("=" * 65)

    return {
        "file": base_name,
        "primary_prediction": top_family,
        "confidence": float(top_conf),
        "texture_path": texture_path,
        "top_k": [(idx_to_class[i], float(probs[i])) for i in top_indices]
    }


def main():
    parser = argparse.ArgumentParser(description="Classify unknown file with trained Malware CNN")
    parser.add_argument("--file", "-f", type=str, help="Path to raw binary file (.exe, .dll, .bin)")
    parser.add_argument("--image", "-i", type=str, help="Path to pre-converted image file (.png)")
    parser.add_argument("--top-k", "-k", type=int, default=5, help="Number of top predictions to display (default: 5)")
    args = parser.parse_args()

    target = args.file or args.image
    if not target:
        # Default to classifying a real system binary as demonstration
        demo_sample = r"C:\Windows\System32\cmd.exe"
        if os.path.exists(demo_sample):
            print(f"[INFO] No file specified. Running demonstration on: {demo_sample}\n")
            predict(demo_sample, top_k=args.top_k)
        else:
            parser.print_help()
    else:
        predict(target, top_k=args.top_k)


if __name__ == "__main__":
    main()
