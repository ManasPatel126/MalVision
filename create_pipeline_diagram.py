"""
create_pipeline_diagram.py

Generates a publication-grade, pixel-perfect 4K architecture illustration of the
MalVision malware classification and explainability pipeline.
"""

import os
import glob
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.gridspec import GridSpec


def build_pipeline_figure(output_path="demo_presentation/pipeline_architecture_diagram.png"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 4K resolution canvas: 26 x 14.5 inches at 150 DPI = 3900 x 2175 px
    fig = plt.figure(figsize=(26, 14.5), facecolor="#070c14", dpi=150)
    gs = GridSpec(1, 1, figure=fig, left=0.01, right=0.99, top=0.98, bottom=0.02)
    ax = fig.add_subplot(gs[0])
    ax.set_facecolor("#070c14")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    # ──────────────────────────────────────────────────────────────────────────
    # COLOR PALETTE
    # ──────────────────────────────────────────────────────────────────────────
    C_BG_CARD    = "#0e1726"
    C_BORDER     = "#1c2e47"
    C_BORDER_ACC = "#00d4ff"
    C_CYAN       = "#00d4ff"
    C_BLUE       = "#448aff"
    C_GREEN      = "#00e676"
    C_RED        = "#ff1744"
    C_ORANGE     = "#ff9100"
    C_TEXT_MAIN  = "#ffffff"
    C_TEXT_MUTED = "#8fa3bf"
    C_CODE_BG    = "#09101a"

    # ──────────────────────────────────────────────────────────────────────────
    # HEADER BANNER
    # ──────────────────────────────────────────────────────────────────────────
    ax.text(50, 97.2, "MALVISION: IMAGE-BASED MALWARE CLASSIFICATION PIPELINE",
            fontsize=24, fontweight="bold", color=C_CYAN, ha="center", va="center",
            fontfamily="sans-serif")
    ax.text(50, 94.6, "End-to-End Deep Learning Architecture: Raw Binary to 2D Spatial Texture, ResNet-18 Inference, and Grad-CAM Explainability",
            fontsize=13, color=C_TEXT_MUTED, ha="center", va="center", fontfamily="sans-serif")

    # Separator line
    ax.plot([3, 97], [93.2, 93.2], color="#16273d", lw=1.5)

    # Helper for rounded card containers
    def draw_card(x, y, w, h, title, subtitle=None, border_color=C_BORDER, header_color=C_CYAN):
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.6,rounding_size=1.2",
                                      facecolor=C_BG_CARD, edgecolor=border_color, linewidth=1.5, zorder=1)
        ax.add_patch(rect)
        ax.text(x + 1.2, y + h - 2.0, title, fontsize=12, fontweight="bold", color=header_color, va="center", zorder=2)
        if subtitle:
            ax.text(x + 1.2, y + h - 3.8, subtitle, fontsize=9, color=C_TEXT_MUTED, va="center", zorder=2)
        # Inner dividing line under header
        ax.plot([x + 0.8, x + w - 0.8], [y + h - 5.0, y + h - 5.0], color="#16273d", lw=1, zorder=2)

    # Helper for arrows between stages
    def draw_arrow(x1, y1, x2, y2, color=C_CYAN, label=None):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=2.5, mutation_scale=18),
                    zorder=10)
        if label:
            ax.text((x1 + x2)/2, (y1 + y2)/2 + 1.2, label, fontsize=8.5, color=color,
                    ha="center", va="bottom", fontweight="bold", zorder=11)

    # ──────────────────────────────────────────────────────────────────────────
    # TOP ROW: DATA INGESTION & TRANSFORMATION (Y: 53 to 91, H: 38)
    # ──────────────────────────────────────────────────────────────────────────

    # BOX 1: Raw Binary Ingestion (X: 3 to 22, W: 19)
    draw_card(3, 53, 19, 38, "STAGE 1: BINARY INGESTION", "Direct Static File Read (No Execution)")
    
    # Hex Dump preview box
    hex_box = patches.FancyBboxPatch((4.2, 70), 16.6, 16, boxstyle="round,pad=0.3",
                                     facecolor=C_CODE_BG, edgecolor="#1a2f47", lw=1, zorder=3)
    ax.add_patch(hex_box)
    ax.text(4.8, 84.5, "OFFSET   00 01 02 03 04 05 06 07  ASCII", fontsize=8.5, family="monospace", color="#627d98", zorder=4)
    hex_lines = [
        "00000000 4D 5A 90 00 03 00 00 00  MZ......",
        "00000008 04 00 00 00 FF FF 00 00  ........",
        "00000010 B8 00 00 00 00 00 00 00  ........",
        "00000018 40 00 00 00 00 00 00 00  @.......",
        "00000020 00 00 00 00 00 00 00 00  ........",
        "00000028 00 00 00 00 00 00 00 00  ........",
        "00000030 00 00 00 00 00 00 00 00  ........",
        "00000038 00 00 00 00 F0 00 00 00  ........"
    ]
    for idx, l in enumerate(hex_lines):
        ax.text(4.8, 82.5 - idx * 1.5, l, fontsize=7.8, family="monospace", color="#00e5ff" if idx == 0 else "#a0b3c6", zorder=4)

    # Bullet properties
    props1 = [
        "• Input: Raw .exe / .dll / .bin files",
        "• Unconstrained file size (10 KB to 50 MB)",
        "• 100% Safe: Code is NEVER executed",
        "• Immune to sandbox evasion / sleep tricks",
        "• Stream converted to 1D uint8 byte array"
    ]
    for idx, p in enumerate(props1):
        ax.text(4.5, 66.5 - idx * 2.5, p, fontsize=8.5, color=C_TEXT_MAIN, zorder=4)

    draw_arrow(22.5, 72, 26.5, 72, color=C_CYAN, label="Bytes [0,255]")

    # BOX 2: 2D Spatial Reshaping (X: 27 to 57, W: 30)
    draw_card(27, 53, 30, 38, "STAGE 2: SPATIAL RESHAPING", "Nataraj et al. Binary-to-Texture Mapping")

    # Math Box
    math_box = patches.FancyBboxPatch((28.2, 77.5), 14.5, 9, boxstyle="round,pad=0.3",
                                      facecolor=C_CODE_BG, edgecolor="#1a2f47", lw=1, zorder=3)
    ax.add_patch(math_box)
    ax.text(29.0, 84.5, "WIDTH SELECTION HEURISTIC", fontsize=8.5, fontweight="bold", color=C_CYAN, zorder=4)
    ax.text(29.0, 82.5, "Width (W) = LookupTable(File Size)", fontsize=8, family="monospace", color="#ffffff", zorder=4)
    ax.text(29.0, 80.5, "Height (H) = ceil( File_Bytes / W )", fontsize=8, family="monospace", color="#ffffff", zorder=4)
    ax.text(29.0, 78.5, "Padding = (W * H - File_Bytes) zeros", fontsize=8, family="monospace", color="#8fa3bf", zorder=4)

    # Lookup table mini table
    table_box = patches.FancyBboxPatch((28.2, 55.5), 14.5, 20.5, boxstyle="round,pad=0.3",
                                       facecolor=C_CODE_BG, edgecolor="#1a2f47", lw=1, zorder=3)
    ax.add_patch(table_box)
    ax.text(29.0, 74.0, "FILE SIZE               WIDTH", fontsize=8, fontweight="bold", color="#627d98", family="monospace", zorder=4)
    table_rows = [
        ("< 10 KB", "32 px"),
        ("10 - 30 KB", "64 px"),
        ("30 - 60 KB", "128 px"),
        ("60 - 100 KB", "256 px"),
        ("100 - 200 KB", "384 px"),
        ("200 - 500 KB", "512 px"),
        ("500 KB - 1 MB", "768 px"),
        ("> 1 MB", "1024 px")
    ]
    for idx, (sz, w) in enumerate(table_rows):
        ax.text(29.0, 71.5 - idx * 2.0, f"{sz:<16}  {w:>7}", fontsize=8, family="monospace",
                color="#00e5ff" if "256" in w else "#a0b3c6", zorder=4)

    # Actual real sample byteplot embedded
    sample_files = glob.glob("data/dataset/*/*.png")
    if sample_files:
        sample_img = Image.open(sample_files[0]).convert("L")
        # Inset axes for real image
        img_ax = fig.add_axes([0.435, 0.40, 0.125, 0.19], zorder=5)
        img_ax.imshow(sample_img, cmap="gray")
        img_ax.axis("off")
        img_ax.set_title("Generated Byteplot\n(Family: Allaple.A)", fontsize=8.5, color=C_CYAN, pad=4)
    
    # Annotations on the texture
    ax.text(44.0, 56.5, "[PE Header]", fontsize=8, color="#ff9100", zorder=6)
    ax.text(44.0, 54.5, "[.text Executable Code]", fontsize=8, color="#00e676", zorder=6)
    ax.text(44.0, 52.5, "[.data & Resources]", fontsize=8, color="#448aff", zorder=6)

    draw_arrow(57.5, 72, 61.5, 72, color=C_CYAN, label="Grayscale PNG")

    # BOX 3: Preprocessing & Normalization (X: 62 to 97, W: 35)
    draw_card(62, 53, 35, 38, "STAGE 3: PREPROCESSING & TENSOR PREPARATION", "Resize & Standardization for CNN Input")

    col_boxes = [
        ("Step 1: Bilinear Resize", "Resizes arbitrary (H x W) byteplot to standard 224 x 224 pixels", "(224, 224)"),
        ("Step 2: Normalization", "Applies mean=0.5, std=0.5 scaling:\n  Tensor = (Pixel / 255.0 - 0.5) / 0.5", "[-1.0, +1.0]"),
        ("Step 3: Tensor Packaging", "Shapes tensor with batch & channel dimension:\n  Batch Tensor: [1, 1, 224, 224]", "[1, 1, 224, 224]")
    ]

    for idx, (title, desc, badge) in enumerate(col_boxes):
        s_box = patches.FancyBboxPatch((63.5, 76.5 - idx * 10.5), 32.0, 9.2, boxstyle="round,pad=0.3",
                                      facecolor=C_CODE_BG, edgecolor="#1a2f47", lw=1, zorder=3)
        ax.add_patch(s_box)
        ax.text(64.5, 83.5 - idx * 10.5, title, fontsize=9.5, fontweight="bold", color=C_CYAN, zorder=4)
        ax.text(64.5, 79.5 - idx * 10.5, desc, fontsize=8, color="#a0b3c6", zorder=4)
        # Badge
        badge_p = patches.FancyBboxPatch((86.0, 82.0 - idx * 10.5), 8.5, 2.8, boxstyle="round,pad=0.2",
                                         facecolor="#182c42", edgecolor=C_CYAN, lw=1, zorder=5)
        ax.add_patch(badge_p)
        ax.text(90.25, 83.4 - idx * 10.5, badge, fontsize=8, fontweight="bold", color="#ffffff", ha="center", va="center", zorder=6)

    # ──────────────────────────────────────────────────────────────────────────
    # CONNECTOR FROM TOP ROW TO BOTTOM ROW
    # ──────────────────────────────────────────────────────────────────────────
    ax.annotate("", xy=(50, 48.5), xytext=(50, 52.5),
                arrowprops=dict(arrowstyle="-|>", color=C_CYAN, lw=3, mutation_scale=20),
                zorder=10)
    ax.text(50, 50.8, "Input Tensor: [1, 1, 224, 224]", fontsize=9, color=C_CYAN, ha="center", va="center",
            fontweight="bold", bbox=dict(boxstyle="round,pad=0.3", facecolor="#091320", edgecolor=C_CYAN, lw=1), zorder=11)

    # ──────────────────────────────────────────────────────────────────────────
    # BOTTOM ROW: NEURAL NETWORK INFERENCE & EXPLAINABILITY (Y: 4 to 47, H: 43)
    # ──────────────────────────────────────────────────────────────────────────

    # BOX 4: ResNet-18 Backbone Architecture (X: 3 to 48, W: 45)
    draw_card(3, 4, 45, 43, "STAGE 4: RESNET-18 DEEP CONVOLUTIONAL NETWORK", "Feature Extraction via Grayscale-Adapted Backbone")

    layers = [
        ("Conv1 + MaxPool", "7x7 Conv, Stride=2\n3x3 MaxPool", "112x112\nx 64", "Early Features:\nEdges & Section Boundaries", "#2979ff"),
        ("Layer 1 (ResBlock x2)", "BasicBlock x2\nResidual Skips", "56x56\nx 64", "Opcode Patterns:\nSpeckled static / Instruction flow", "#00b0ff"),
        ("Layer 2 (ResBlock x2)", "BasicBlock x2\nResidual Skips", "28x28\nx 128", "Micro-Textures:\nString tables & data loops", "#00e5ff"),
        ("Layer 3 (ResBlock x2)", "BasicBlock x2\nResidual Skips", "14x14\nx 256", "Macro Structures:\nSection ratios & packed stubs", "#00e676"),
        ("Layer 4 (ResBlock x2)", "BasicBlock x2\nFinal Conv Block", "7x7\nx 512", "Family Fingerprints:\nMalware family signature layout", "#ff9100"),
    ]

    for idx, (lname, arch, dim, role, col) in enumerate(layers):
        ly = 39.5 - idx * 7.0
        # Block card
        l_rect = patches.FancyBboxPatch((4.5, ly - 5.5), 42.0, 6.0, boxstyle="round,pad=0.3",
                                        facecolor=C_CODE_BG, edgecolor=col, lw=1.2, zorder=3)
        ax.add_patch(l_rect)
        # Indicator badge
        b_dot = patches.Circle((6.2, ly - 2.5), 0.9, facecolor=col, zorder=4)
        ax.add_patch(b_dot)
        ax.text(6.2, ly - 2.5, str(idx + 1), fontsize=8, fontweight="bold", color="#000000", ha="center", va="center", zorder=5)

        ax.text(8.0, ly - 1.8, lname, fontsize=9.5, fontweight="bold", color="#ffffff", zorder=4)
        ax.text(8.0, ly - 4.0, arch, fontsize=8, color="#8fa3bf", zorder=4)

        # Dimension badge
        dim_p = patches.FancyBboxPatch((23.0, ly - 4.5), 7.5, 4.0, boxstyle="round,pad=0.2",
                                       facecolor="#122336", edgecolor="#213d5b", lw=1, zorder=4)
        ax.add_patch(dim_p)
        ax.text(26.75, ly - 2.5, dim, fontsize=7.8, family="monospace", color=C_CYAN, ha="center", va="center", zorder=5)

        ax.text(32.0, ly - 2.8, role, fontsize=8, color="#c2d4e7", zorder=4)

    # Global Average Pooling box
    pool_box = patches.FancyBboxPatch((4.5, 5.0), 42.0, 3.8, boxstyle="round,pad=0.2",
                                     facecolor="#10253d", edgecolor=C_CYAN, lw=1, zorder=3)
    ax.add_patch(pool_box)
    ax.text(25.5, 6.9, "AdaptiveAvgPool2d(1, 1)  ==>  512-Dimensional Latent Embedding Vector",
            fontsize=8.5, family="monospace", fontweight="bold", color="#ffffff", ha="center", va="center", zorder=4)

    # Branch Arrow to Inference
    draw_arrow(48.5, 30, 52.5, 30, color=C_CYAN, label="512-d Vector")

    # Branch Arrow to Grad-CAM
    draw_arrow(48.5, 15, 52.5, 15, color=C_ORANGE, label="Gradients")

    # BOX 5: Classification & Threat Triage (X: 53 to 75, W: 22)
    draw_card(53, 4, 22, 43, "STAGE 5: INFERENCE & TRIAGE", "Softmax Over 26 Malware Classes")

    # Classification metrics
    ax.text(54.5, 40.0, "OUTPUT PROBABILITY DISTRIBUTION", fontsize=8.5, fontweight="bold", color=C_CYAN, zorder=4)

    # Mini Bar chart simulation
    sample_classes = [("Allaple.A", 0.9997, C_RED), ("Allaple.L", 0.0002, C_CYAN), ("Fakerean", 0.0001, C_CYAN),
                      ("Yuner.A", 0.0000, C_CYAN), ("VB.AT", 0.0000, C_CYAN), ("Other 21", 0.0000, "#50657b")]
    for idx, (cname, prob, col) in enumerate(sample_classes):
        by = 37.0 - idx * 2.8
        ax.text(54.5, by, f"{cname:<12}", fontsize=8, family="monospace", color="#ffffff", zorder=4)
        bar_len = max(prob * 10.0, 0.4)
        b_bar = patches.Rectangle((63.0, by - 0.5), bar_len, 1.2, facecolor=col, zorder=4)
        ax.add_patch(b_bar)
        ax.text(63.5 + bar_len, by, f"{prob:>7.2%}", fontsize=7.5, family="monospace", color=col, va="center", zorder=4)

    # Threat Triage Badges Box
    ax.text(54.5, 19.5, "AUTOMATED THREAT LEVEL TRIAGE", fontsize=8.5, fontweight="bold", color=C_CYAN, zorder=4)

    badges = [
        ("CRITICAL", "Confidence > 85%", C_RED, "Definite match to known malware family. Immediate quarantine & incident response."),
        ("SUSPICIOUS", "Confidence 60-85%", C_ORANGE, "Probable variant or modified sample. Secondary sandbox inspection advised."),
        ("INCONCLUSIVE", "Confidence < 60%", C_GREEN, "Likely benign Windows executable or clean unknown utility.")
    ]

    for idx, (b_name, b_crit, b_color, b_desc) in enumerate(badges):
        by = 16.5 - idx * 4.5
        b_patch = patches.FancyBboxPatch((54.5, by - 2.5), 19.0, 3.6, boxstyle="round,pad=0.2",
                                         facecolor=C_CODE_BG, edgecolor=b_color, lw=1.2, zorder=4)
        ax.add_patch(b_patch)
        ax.text(55.2, by - 0.2, b_name, fontsize=8.5, fontweight="bold", color=b_color, zorder=5)
        ax.text(62.5, by - 0.2, b_crit, fontsize=7.5, color=C_TEXT_MUTED, zorder=5)
        ax.text(55.2, by - 1.8, b_desc, fontsize=6.8, color="#a0b3c6", zorder=5)

    # BOX 6: Explainable AI / Grad-CAM (X: 76 to 97, W: 21)
    draw_card(76, 4, 21, 43, "STAGE 6: EXPLAINABILITY (GRAD-CAM)", "Visualizing Decision Regions", border_color=C_ORANGE, header_color=C_ORANGE)

    ax.text(77.2, 40.0, "HOW GRAD-CAM WORKS", fontsize=8.5, fontweight="bold", color=C_ORANGE, zorder=4)
    g_steps = [
        "1. Backpropagate predicted class score (yc)",
        "   to Layer 4 feature maps Ak",
        "2. Global average pool gradients -> weights ak",
        "3. Compute linear combination: Sum(ak * Ak)",
        "4. Apply ReLU -> retain positive influences",
        "5. Overlay 60% byteplot + 40% JET heatmap"
    ]
    for idx, gs_text in enumerate(g_steps):
        ax.text(77.2, 37.8 - idx * 1.8, gs_text, fontsize=7.5, family="monospace", color="#c2d4e7", zorder=4)

    # Embed real Grad-CAM image if available
    gradcam_samples = glob.glob("outputs/explanations/*.png")
    if gradcam_samples:
        gc_img = Image.open(gradcam_samples[0])
        gc_ax = fig.add_axes([0.765, 0.065, 0.20, 0.165], zorder=5)
        gc_ax.imshow(gc_img)
        gc_ax.axis("off")
        gc_ax.set_title("Real Model Grad-CAM Explanation\n(Original -> Heatmap -> Decision Overlay)",
                        fontsize=7.8, color=C_ORANGE, pad=4)

    # Save high-res figure
    plt.savefig(output_path, dpi=150, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    print(f"[SUCCESS] Saved publication-grade pipeline diagram to: {output_path}")
    return output_path


if __name__ == "__main__":
    build_pipeline_figure()
