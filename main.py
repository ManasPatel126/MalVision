"""
main.py — Entry Point for the Malware Image Classification Pipeline

This script orchestrates the entire workflow:
    Step 1 │ Convert raw binaries → grayscale PNG images
    Step 2 │ Build data loaders (train / val / test)
    Step 3 │ Construct the CNN model
    Step 4 │ Train the model
    Step 5 │ Evaluate on the held-out test set

Usage
─────
    # Full pipeline (conversion + training + evaluation):
    python main.py

    # Skip conversion (images already exist):
    python main.py --skip-conversion

    # Only convert binaries (no training):
    python main.py --convert-only

    # Only evaluate a previously trained model:
    python main.py --eval-only
"""

import argparse
import torch

from binary_to_image import convert_dataset
from dataset import get_dataloaders
from model import build_model
from train import train_model, plot_training_history
from evaluate import evaluate_model
from config import IMAGE_OUTPUT_DIR, RAW_BINARIES_DIR


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Image-Based Malware Classification Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--skip-conversion", action="store_true",
        help="Skip the binary→image conversion step "
             "(use if images already exist in the dataset folder).",
    )
    parser.add_argument(
        "--convert-only", action="store_true",
        help="Only perform binary→image conversion, then exit.",
    )
    parser.add_argument(
        "--eval-only", action="store_true",
        help="Only run evaluation on the test set using a saved checkpoint.",
    )
    parser.add_argument(
        "--epochs", type=int, default=None,
        help="Override the number of training epochs (default from config.py).",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # ── Device selection ─────────────────────────────────────────────────
    if torch.cuda.is_available():
        device = torch.device("cuda")
        print(f"[INFO] Using GPU: {torch.cuda.get_device_name(0)}")
    else:
        device = torch.device("cpu")
        print("[INFO] Using CPU (no CUDA GPU detected).")

    # ══════════════════════════════════════════════════════════════════════
    # STEP 1: Binary → Image Conversion
    # ══════════════════════════════════════════════════════════════════════
    if not args.skip_conversion and not args.eval_only:
        print("\n" + "=" * 60)
        print("  STEP 1: Converting raw binaries to grayscale images")
        print("=" * 60)
        convert_dataset(
            input_dir=RAW_BINARIES_DIR,
            output_dir=IMAGE_OUTPUT_DIR,
        )

    if args.convert_only:
        print("\n[DONE] Conversion complete. Exiting (--convert-only).")
        return

    # ══════════════════════════════════════════════════════════════════════
    # STEP 2: Build DataLoaders
    # ══════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("  STEP 2: Building data pipeline")
    print("=" * 60)
    (train_loader, val_loader, test_loader,
     idx_to_class, num_classes) = get_dataloaders(IMAGE_OUTPUT_DIR)

    # ══════════════════════════════════════════════════════════════════════
    # STEP 3: Build Model
    # ══════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("  STEP 3: Constructing CNN model")
    print("=" * 60)
    model = build_model(num_classes)

    # Print parameter count
    total_params     = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"[INFO] Total parameters:     {total_params:>12,}")
    print(f"[INFO] Trainable parameters: {trainable_params:>12,}")

    # ══════════════════════════════════════════════════════════════════════
    # STEP 4: Train
    # ══════════════════════════════════════════════════════════════════════
    if not args.eval_only:
        print("\n" + "=" * 60)
        print("  STEP 4: Training the model")
        print("=" * 60)

        num_epochs = args.epochs if args.epochs else None
        train_kwargs = {"model": model, "train_loader": train_loader,
                        "val_loader": val_loader, "device": device}
        if num_epochs is not None:
            train_kwargs["num_epochs"] = num_epochs

        history = train_model(**train_kwargs)

        # Plot training curves
        plot_training_history(history)

    # ══════════════════════════════════════════════════════════════════════
    # STEP 5: Evaluate on Test Set
    # ══════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("  STEP 5: Evaluating on the test set")
    print("=" * 60)
    evaluate_model(model, test_loader, idx_to_class, device)

    print("\n" + "=" * 60)
    print("  [DONE]  PIPELINE COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
