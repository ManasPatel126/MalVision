"""
create_project_infographic.py

Generates a publication-grade, crisp 4K visual infographic illustrating:
1. The Step-by-Step Operational Workflow (How it Works)
2. The Modular Software Architecture & Tech Stack (Project Structure)
"""

import os
import glob
from PIL import Image
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.gridspec import GridSpec


def build_infographic(output_path="demo_presentation/project_working_and_structure.png"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 4K Canvas (16:9 ratio): 24 x 13.5 inches at 150 DPI = 3600 x 2025 px
    fig = plt.figure(figsize=(24, 13.5), facecolor="#070c14", dpi=150)
    gs = GridSpec(1, 1, figure=fig, left=0.01, right=0.99, top=0.98, bottom=0.02)
    ax = fig.add_subplot(gs[0])
    ax.set_facecolor("#070c14")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    # Colors
    C_BG_CARD   = "#0d1624"
    C_BORDER    = "#1b2c44"
    C_CYAN      = "#00d4ff"
    C_BLUE      = "#388bfd"
    C_GREEN     = "#00e676"
    C_RED       = "#ff1744"
    C_ORANGE    = "#ff9100"
    C_PURPLE    = "#a371f7"
    C_TEXT_MAIN = "#ffffff"
    C_TEXT_MUT  = "#8fa3bf"
    C_CODE_BG   = "#09101a"

    # =========================================================================
    # HEADER BANNER
    # =========================================================================
    ax.text(50, 97.2, "MALVISION: SYSTEM WORKING & MODULAR STRUCTURE",
            fontsize=22, fontweight="bold", color=C_CYAN, ha="center", va="center")
    ax.text(50, 94.8, "Deep Learning Binary-to-Texture Malware Classification & Explainable Threat Hunting Platform",
            fontsize=12, color=C_TEXT_MUT, ha="center", va="center")
    ax.plot([3, 97], [93.4, 93.4], color="#16273d", lw=1.5)

    def draw_card(x, y, w, h, title, subtitle=None, border_color=C_BORDER, header_color=C_CYAN, fill=C_BG_CARD):
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.5,rounding_size=1.0",
                                      facecolor=fill, edgecolor=border_color, linewidth=1.4, zorder=1)
        ax.add_patch(rect)
        ax.text(x + 1.2, y + h - 1.8, title, fontsize=11, fontweight="bold", color=header_color, va="center", zorder=2)
        if subtitle:
            ax.text(x + 1.2, y + h - 3.4, subtitle, fontsize=8, color=C_TEXT_MUT, va="center", zorder=2)
        ax.plot([x + 0.8, x + w - 0.8], [y + h - 4.5, y + h - 4.5], color="#182c44", lw=1, zorder=2)

    def draw_arrow(x1, y1, x2, y2, color=C_CYAN, label=None):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=2.2, mutation_scale=16),
                    zorder=10)
        if label:
            ax.text((x1 + x2)/2, (y1 + y2)/2 + 1.2, label, fontsize=8, color=color,
                    ha="center", va="bottom", fontweight="bold", zorder=11)

    # =========================================================================
    # PART 1: THE OPERATIONAL WORKFLOW (HOW IT WORKS) - Top Half (Y: 50 to 92)
    # =========================================================================
    ax.text(3, 91.5, "PART 1: THE 4-STEP OPERATIONAL PIPELINE (HOW IT WORKS)",
            fontsize=12, fontweight="bold", color="#ffffff", va="center")

    # Step 1: Binary Ingestion
    draw_card(3, 52, 21, 37.5, "STEP 1: INGESTION", "Static Raw Byte Stream (No Execution)", border_color=C_BLUE, header_color=C_BLUE)
    
    # Hex Box
    hex_box = patches.FancyBboxPatch((4.2, 69.5), 18.6, 14.5, boxstyle="round,pad=0.3",
                                     facecolor=C_CODE_BG, edgecolor="#1a2f47", lw=1, zorder=3)
    ax.add_patch(hex_box)
    ax.text(4.8, 82.2, "OFFSET   HEX STREAM (BYTES 0-255)   ASCII", fontsize=7.2, family="monospace", color="#627d98", zorder=4)
    hex_lines = [
        "00000000 4D 5A 90 00 03 00 00 00  MZ......",
        "00000008 04 00 00 00 FF FF 00 00  ........",
        "00000010 B8 00 00 00 00 00 00 00  ........",
        "00000018 40 00 00 00 00 00 00 00  @.......",
        "00000020 00 00 00 00 00 00 00 00  ........",
        "00000028 00 00 00 00 00 00 00 00  ........",
        "00000030 00 00 00 00 F0 00 00 00  ........"
    ]
    for idx, l in enumerate(hex_lines):
        ax.text(4.8, 80.5 - idx * 1.4, l, fontsize=7.2, family="monospace",
                color="#00e5ff" if idx == 0 else "#a0b3c6", zorder=4)

    props1 = [
        "[+] Input: Raw .exe / .dll / .bin",
        "[+] 1D Array of N Bytes in [0, 255]",
        "[+] 100% Safe: Code NEVER executes",
        "[+] Immune to anti-VM / sleep tricks"
    ]
    for idx, p in enumerate(props1):
        ax.text(4.5, 65.5 - idx * 2.8, p, fontsize=8, color="#cbd5e1", zorder=4)

    draw_arrow(24.5, 70.5, 27.5, 70.5, color=C_CYAN, label="Bytes [0,255]")

    # Step 2: 2D Spatial Reshaping
    draw_card(28, 52, 22, 37.5, "STEP 2: SPATIAL RESHAPING", "Nataraj Heuristic: Byte -> Grayscale Pixel", border_color=C_CYAN, header_color=C_CYAN)

    math_box = patches.FancyBboxPatch((29.2, 75.5), 19.6, 8.5, boxstyle="round,pad=0.3",
                                      facecolor=C_CODE_BG, edgecolor="#1a2f47", lw=1, zorder=3)
    ax.add_patch(math_box)
    ax.text(30.0, 82.2, "HEURISTIC FORMULA", fontsize=8, fontweight="bold", color=C_CYAN, zorder=4)
    ax.text(30.0, 80.2, "Pixel (0-255) = Byte Value (0-255)", fontsize=7.5, family="monospace", color="#ffffff", zorder=4)
    ax.text(30.0, 78.4, "Width (W) = LookupTable(File Size)", fontsize=7.5, family="monospace", color="#ffffff", zorder=4)
    ax.text(30.0, 76.6, "Height (H) = ceil( File_Bytes / W )", fontsize=7.5, family="monospace", color="#8fa3bf", zorder=4)

    # Embed sample image
    sample_files = glob.glob("data/dataset/*/*.png")
    if sample_files:
        sample_img = Image.open(sample_files[0]).convert("L")
        img_ax = fig.add_axes([0.315, 0.54, 0.08, 0.14], zorder=5)
        img_ax.imshow(sample_img, cmap="gray")
        img_ax.axis("off")
        img_ax.set_title("Generated Byteplot", fontsize=7.5, color=C_CYAN, pad=3)

    props2 = [
        "Width Rule:",
        "<10KB -> 32px",
        "10-30KB -> 64px",
        "30-60KB -> 128px",
        "60-100KB -> 256px",
        ">1MB -> 1024px"
    ]
    for idx, p in enumerate(props2):
        ax.text(41.5, 68.0 - idx * 2.5, p, fontsize=7.5, family="monospace",
                color=C_CYAN if idx == 0 else "#a0b3c6", zorder=4)

    draw_arrow(50.5, 70.5, 53.5, 70.5, color=C_CYAN, label="Grayscale PNG")

    # Step 3: ResNet-18 Feature Extraction
    draw_card(54, 52, 22, 37.5, "STEP 3: DEEP CNN BACKBONE", "ResNet-18 Grayscale Feature Extraction", border_color=C_PURPLE, header_color=C_PURPLE)

    stages = [
        ("Conv1 (7x7, s=2)", "64 x 112x112", "Section edges & margins", "#2979ff"),
        ("Residual Layer 1", "64 x 56x56", "Opcode instruction static", "#00b0ff"),
        ("Residual Layer 2", "128 x 28x28", "String tables & data loops", "#00e5ff"),
        ("Residual Layer 3", "256 x 14x14", "Code-to-payload ratios", "#00e676"),
        ("Residual Layer 4", "512 x 7x7", "Family signature blueprint", "#ff9100"),
    ]
    for idx, (sname, dim, role, col) in enumerate(stages):
        sy = 83.5 - idx * 5.2
        s_rect = patches.FancyBboxPatch((55.2, sy - 4.2), 19.6, 4.4, boxstyle="round,pad=0.2",
                                        facecolor=C_CODE_BG, edgecolor=col, lw=1.1, zorder=3)
        ax.add_patch(s_rect)
        ax.text(56.0, sy - 1.5, sname, fontsize=8, fontweight="bold", color="#ffffff", zorder=4)
        ax.text(56.0, sy - 3.2, role, fontsize=7.2, color="#94a3b8", zorder=4)
        ax.text(73.5, sy - 2.4, dim, fontsize=7, family="monospace", color=col, ha="right", va="center", zorder=4)

    draw_arrow(76.5, 70.5, 79.5, 70.5, color=C_CYAN, label="512-d Latent")

    # Step 4: Decision & Explainability
    draw_card(80, 52, 17, 37.5, "STEP 4: TRIAGE & EXPLAIN", "Output Scoring & Grad-CAM Heatmap", border_color=C_GREEN, header_color=C_GREEN)

    # Threat Triage Badges
    badges = [
        ("CRITICAL", "> 85%", C_RED, "Definite family match. Quarantine."),
        ("SUSPICIOUS", "60-85%", C_ORANGE, "Possible hybrid. Audit needed."),
        ("INCONCLUSIVE", "< 60%", C_GREEN, "Likely clean file (e.g. cmd.exe)")
    ]
    for idx, (bname, bthresh, bcol, bdesc) in enumerate(badges):
        by = 83.0 - idx * 4.8
        b_p = patches.FancyBboxPatch((81.2, by - 3.6), 14.6, 3.8, boxstyle="round,pad=0.2",
                                    facecolor=C_CODE_BG, edgecolor=bcol, lw=1, zorder=3)
        ax.add_patch(b_p)
        ax.text(82.0, by - 1.5, bname, fontsize=8, fontweight="bold", color=bcol, zorder=4)
        ax.text(94.5, by - 1.5, bthresh, fontsize=7.2, color="#cbd5e1", ha="right", zorder=4)
        ax.text(82.0, by - 3.0, bdesc, fontsize=6.5, color="#8fa3bf", zorder=4)

    # Embed GradCAM
    gc_files = glob.glob("outputs/explanations/*.png")
    if gc_files:
        gc_img = Image.open(gc_files[0])
        gc_ax = fig.add_axes([0.815, 0.54, 0.145, 0.09], zorder=5)
        gc_ax.imshow(gc_img)
        gc_ax.axis("off")
        gc_ax.set_title("Grad-CAM Thermal Heatmap", fontsize=7.2, color=C_ORANGE, pad=2)

    # Dividing line between Part 1 and Part 2
    ax.plot([3, 97], [48.0, 48.0], color="#16273d", lw=1.5)

    # =========================================================================
    # PART 2: MODULAR SOFTWARE STRUCTURE (HOW THE PROJECT IS BUILT) - Bottom (Y: 4 to 45)
    # =========================================================================
    ax.text(3, 46.0, "PART 2: MODULAR PROJECT ARCHITECTURE & CODEBASE STRUCTURE",
            fontsize=12, fontweight="bold", color="#ffffff", va="center")

    # Layer A: User Interaction Layer
    draw_card(3, 4, 21, 39, "LAYER 1: USER INTERACTION", "Streamlit Threat Hunter Web Interface", border_color=C_CYAN, header_color=C_CYAN)
    ui_items = [
        ("app.py", "Main Streamlit Dashboard", "Web UI for drag-and-drop, gauges & results"),
        ("start.bat", "1-Click Windows Launcher", "Automates python environment & browser launch"),
        ("Single File Tab", "Real-time File Triage", "Instant byteplot toggle, top-5 confidence meters"),
        ("Batch Triage Tab", "Multi-File Ingestion", "Uploads dozens of binaries for bulk analysis"),
        ("Dataset Gallery", "Malimg Visual Explorer", "Browse & inspect sample textures across 26 classes")
    ]
    for idx, (fn, role, desc) in enumerate(ui_items):
        iy = 36.5 - idx * 6.0
        i_box = patches.FancyBboxPatch((4.2, iy - 4.5), 18.6, 5.0, boxstyle="round,pad=0.2",
                                       facecolor=C_CODE_BG, edgecolor="#1a2f47", lw=1, zorder=3)
        ax.add_patch(i_box)
        ax.text(5.0, iy - 1.5, fn, fontsize=8, fontweight="bold", family="monospace", color=C_CYAN, zorder=4)
        ax.text(5.0, iy - 2.8, role, fontsize=7.2, fontweight="bold", color="#ffffff", zorder=4)
        ax.text(5.0, iy - 4.0, desc, fontsize=6.5, color="#8fa3bf", zorder=4)

    # Layer B: Inference & Processing Engine
    draw_card(27, 4, 22, 39, "LAYER 2: CORE AI ENGINE", "PyTorch Modeling, Training & Inference", border_color=C_BLUE, header_color=C_BLUE)
    ai_items = [
        ("model.py", "ResNet-18 Grayscale Surgery", "Averages RGB weights [64,3,7,7] -> [64,1,7,7]"),
        ("train.py", "Optimization Loop", "Adam, lr=1e-4, CrossEntropyLoss, ReduceLROnPlateau"),
        ("predict.py", "CLI Inference Engine", "Processes files, outputs top-k family rankings"),
        ("evaluate.py", "Evaluation Metrics", "Computes confusion matrix & classification report"),
        ("tracker.py", "Real-time Training Monitor", "Tracks epoch loss & accuracy curves during training")
    ]
    for idx, (fn, role, desc) in enumerate(ai_items):
        iy = 36.5 - idx * 6.0
        i_box = patches.FancyBboxPatch((28.2, iy - 4.5), 19.6, 5.0, boxstyle="round,pad=0.2",
                                       facecolor=C_CODE_BG, edgecolor="#1a2f47", lw=1, zorder=3)
        ax.add_patch(i_box)
        ax.text(29.0, iy - 1.5, fn, fontsize=8, fontweight="bold", family="monospace", color=C_BLUE, zorder=4)
        ax.text(29.0, iy - 2.8, role, fontsize=7.2, fontweight="bold", color="#ffffff", zorder=4)
        ax.text(29.0, iy - 4.0, desc, fontsize=6.5, color="#8fa3bf", zorder=4)

    # Layer C: Data Transformation & Explainability
    draw_card(52, 4, 22, 39, "LAYER 3: DATA & EXPLAINABILITY", "Byte Conversion & Grad-CAM Heatmaps", border_color=C_ORANGE, header_color=C_ORANGE)
    data_items = [
        ("binary_to_image.py", "Nataraj Conversion Engine", "Maps raw byte arrays to 2D grayscale PNGs"),
        ("explain.py", "Grad-CAM Implementation", "Hooks Layer 4 feature maps, calculates gradients"),
        ("dataset.py", "PyTorch Dataset Loader", "Implements stratified 70/15/15 train/val/test splits"),
        ("config.py", "Central Configuration", "Single source of truth for paths, width table & hyperparams"),
        ("download_malimg.py", "Dataset Pipeline", "Automates acquisition & extraction of Malimg corpus")
    ]
    for idx, (fn, role, desc) in enumerate(data_items):
        iy = 36.5 - idx * 6.0
        i_box = patches.FancyBboxPatch((53.2, iy - 4.5), 19.6, 5.0, boxstyle="round,pad=0.2",
                                       facecolor=C_CODE_BG, edgecolor="#1a2f47", lw=1, zorder=3)
        ax.add_patch(i_box)
        ax.text(54.0, iy - 1.5, fn, fontsize=8, fontweight="bold", family="monospace", color=C_ORANGE, zorder=4)
        ax.text(54.0, iy - 2.8, role, fontsize=7.2, fontweight="bold", color="#ffffff", zorder=4)
        ax.text(54.0, iy - 4.0, desc, fontsize=6.5, color="#8fa3bf", zorder=4)

    # Layer D: Storage & Threat Intelligence
    draw_card(77, 4, 20, 39, "LAYER 4: INTEL & STORAGE", "Knowledge Base, Weights & Samples", border_color=C_GREEN, header_color=C_GREEN)
    storage_items = [
        ("malware_intel.py", "Threat Intelligence Dossiers", "26 family knowledge base: vectors & remediations"),
        ("best_model.pth", "Trained ResNet-18 Weights", "42.7 MB pre-trained weights (97.86% accuracy)"),
        ("test_samples/", "Verification Test Suite", "15 pre-loaded samples (10 malware + 5 clean Windows)"),
        ("demo_presentation/", "Presentation Package", "Contains 4K diagrams, IEEE paper, and reports"),
        ("IEEE Paper & PDF", "Academic Documentation", "11-page IEEE paper + 4-page executive report")
    ]
    for idx, (fn, role, desc) in enumerate(storage_items):
        iy = 36.5 - idx * 6.0
        i_box = patches.FancyBboxPatch((78.2, iy - 4.5), 17.6, 5.0, boxstyle="round,pad=0.2",
                                       facecolor=C_CODE_BG, edgecolor="#1a2f47", lw=1, zorder=3)
        ax.add_patch(i_box)
        ax.text(79.0, iy - 1.5, fn, fontsize=8, fontweight="bold", family="monospace", color=C_GREEN, zorder=4)
        ax.text(79.0, iy - 2.8, role, fontsize=7.2, fontweight="bold", color="#ffffff", zorder=4)
        ax.text(79.0, iy - 4.0, desc, fontsize=6.5, color="#8fa3bf", zorder=4)

    # Connectors between layers
    draw_arrow(24.2, 23.5, 26.8, 23.5, color=C_CYAN, label="API Calls")
    draw_arrow(49.2, 23.5, 51.8, 23.5, color=C_BLUE, label="Tensors")
    draw_arrow(74.2, 23.5, 76.8, 23.5, color=C_ORANGE, label="Weights & Intel")

    plt.savefig(output_path, dpi=150, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    print(f"[SUCCESS] Infographic generated: {output_path}")
    return output_path


if __name__ == "__main__":
    build_infographic()
