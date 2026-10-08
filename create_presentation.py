"""
create_presentation.py

Generates a publication-grade, widescreen (16:9) PowerPoint presentation (.pptx)
for the MalVision project with embedded high-resolution illustrations, diagrams,
academic metrics, and speaker notes.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE


# -----------------------------------------------------------------------------
# Color Palette (Dark Cybersecurity Keynote Theme)
# -----------------------------------------------------------------------------
COLOR_BG          = RGBColor(7, 12, 20)       # #070c14
COLOR_CARD        = RGBColor(14, 23, 38)      # #0e1726
COLOR_CARD_BORDER = RGBColor(28, 46, 71)      # #1c2e47
COLOR_CYAN        = RGBColor(0, 212, 255)     # #00d4ff
COLOR_BLUE        = RGBColor(56, 139, 253)    # #388bfd
COLOR_GREEN       = RGBColor(0, 230, 118)     # #00e676
COLOR_RED         = RGBColor(255, 23, 68)     # #ff1744
COLOR_ORANGE      = RGBColor(255, 145, 0)     # #ff9100
COLOR_TEXT_MAIN   = RGBColor(255, 255, 255)   # #ffffff
COLOR_TEXT_MUTED  = RGBColor(143, 163, 191)   # #8fa3bf
COLOR_CODE_BG     = RGBColor(9, 16, 26)       # #09101a


def apply_dark_background(slide):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = COLOR_BG


def add_header(slide, title_text, category_text="MALVISION // TECHNICAL PRESENTATION"):
    # Category tag
    tb_cat = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.35))
    tf_cat = tb_cat.text_frame
    tf_cat.word_wrap = True
    p_cat = tf_cat.paragraphs[0]
    p_cat.text = category_text.upper()
    p_cat.font.name = "Arial"
    p_cat.font.size = Pt(10)
    p_cat.font.bold = True
    p_cat.font.color.rgb = COLOR_CYAN

    # Main Slide Title
    tb_title = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.7), Inches(0.65))
    tf_title = tb_title.text_frame
    tf_title.word_wrap = True
    p_title = tf_title.paragraphs[0]
    p_title.text = title_text
    p_title.font.name = "Arial"
    p_title.font.size = Pt(22)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_TEXT_MAIN

    # Accent underline
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.35), Inches(11.733), Inches(0.02))
    line.fill.solid()
    line.fill.fore_color.rgb = COLOR_CARD_BORDER
    line.line.color.rgb = COLOR_CARD_BORDER


def add_card(slide, left, top, width, height, title=None, subtitle=None, border_color=COLOR_CARD_BORDER, bg_color=COLOR_CARD):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    card.line.color.rgb = border_color
    card.line.width = Pt(1.2)

    if title:
        tb = slide.shapes.add_textbox(left + Inches(0.15), top + Inches(0.1), width - Inches(0.3), Inches(0.5))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = COLOR_CYAN
        if subtitle:
            p_sub = tf.add_paragraph()
            p_sub.text = subtitle
            p_sub.font.name = "Arial"
            p_sub.font.size = Pt(9.5)
            p_sub.font.color.rgb = COLOR_TEXT_MUTED

    return card


def add_bullet_points(tf, points, font_size=11, bold_prefix=True, color=COLOR_TEXT_MAIN):
    for i, pt in enumerate(points):
        p = tf.add_paragraph() if i > 0 or len(tf.paragraphs[0].text) > 0 else tf.paragraphs[0]
        p.font.name = "Arial"
        p.font.size = Pt(font_size)
        p.space_after = Pt(6)
        
        if bold_prefix and ":" in pt:
            prefix, rest = pt.split(":", 1)
            run1 = p.add_run()
            run1.text = prefix + ":"
            run1.font.bold = True
            run1.font.color.rgb = COLOR_CYAN
            run2 = p.add_run()
            run2.text = rest
            run2.font.bold = False
            run2.font.color.rgb = color
        else:
            run = p.add_run()
            run.text = pt
            run.font.color.rgb = color


def set_speaker_notes(slide, notes_text):
    notes_slide = slide.notes_slide
    tf = notes_slide.notes_text_frame
    tf.text = notes_text


def build_malvision_presentation(output_path="MalVision_Presentation.pptx"):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # =========================================================================
    # SLIDE 1: TITLE SLIDE
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    apply_dark_background(s1)

    # Title Card (Left)
    add_card(s1, Inches(0.8), Inches(1.0), Inches(5.8), Inches(5.5), bg_color=COLOR_CARD, border_color=COLOR_CYAN)

    tb = s1.shapes.add_textbox(Inches(1.1), Inches(1.3), Inches(5.2), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True

    p_badge = tf.paragraphs[0]
    p_badge.text = "CYBERSECURITY & DEEP LEARNING PROJECT"
    p_badge.font.name = "Arial"
    p_badge.font.size = Pt(10)
    p_badge.font.bold = True
    p_badge.font.color.rgb = COLOR_CYAN
    p_badge.space_after = Pt(12)

    p_title = tf.add_paragraph()
    p_title.text = "MALVISION"
    p_title.font.name = "Arial"
    p_title.font.size = Pt(36)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_TEXT_MAIN
    p_title.space_after = Pt(6)

    p_sub = tf.add_paragraph()
    p_sub.text = "Image-Based Malware Classification & Explainable Threat Hunting"
    p_sub.font.name = "Arial"
    p_sub.font.size = Pt(15)
    p_sub.font.bold = True
    p_sub.font.color.rgb = COLOR_BLUE
    p_sub.space_after = Pt(18)

    p_desc = tf.add_paragraph()
    p_desc.text = "Transmuting raw unexecuted binary software into 2D spatial grayscale textures to identify 26 malware families with 97.86% accuracy using ResNet-18 and Grad-CAM explainability."
    p_desc.font.name = "Arial"
    p_desc.font.size = Pt(11)
    p_desc.font.color.rgb = COLOR_TEXT_MUTED
    p_desc.space_after = Pt(24)

    p_meta = tf.add_paragraph()
    p_meta.text = "Author: Manas Kumar  •  Academic & Technical Defense  •  2026"
    p_meta.font.name = "Arial"
    p_meta.font.size = Pt(10)
    p_meta.font.color.rgb = COLOR_GREEN

    # Hero Image (Right)
    img_art = "demo_presentation/malvision_concept_art.jpg"
    if os.path.isfile(img_art):
        s1.shapes.add_picture(img_art, Inches(6.9), Inches(1.0), Inches(5.633), Inches(5.5))

    set_speaker_notes(s1, "Welcome everyone. Today I am presenting MalVision, an AI-powered malware classification and threat hunting platform. Traditional antivirus tools struggle because modern malware alters its code to bypass signature checks and sandbox environments. We solve this by converting raw executable files into 2D grayscale textures and classifying them using a fine-tuned ResNet-18 vision model. It classifies files across 26 malware families with 97.86% accuracy, requires zero execution of suspicious code, and provides Grad-CAM heatmaps so analysts can visually verify why a detection was made.")

    # =========================================================================
    # SLIDE 2: THE PROBLEM (WHY ANTIVIRUS FAILS TODAY)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    apply_dark_background(s2)
    add_header(s2, "The Core Problem: Why Modern Antivirus Fails", "THREAT LANDSCAPE & MOTIVATION")

    col_w = Inches(3.7)
    gap = Inches(0.3)
    top_pos = Inches(1.7)
    h_pos = Inches(5.1)

    # Box 1: Signature AV
    add_card(s2, Inches(0.8), top_pos, col_w, h_pos, "1. Signature Matching (Hashes)", "Static Blacklisting (MD5 / SHA256)", border_color=COLOR_RED)
    tb1 = s2.shapes.add_textbox(Inches(1.0), top_pos + Inches(0.8), col_w - Inches(0.4), h_pos - Inches(1.0))
    add_bullet_points(tb1.text_frame, [
        "Trivial Evasion: Attackers use polymorphic crypters and packers (UPX, Themida) that alter byte hashes daily.",
        "Zero-Day Blindspot: Completely ineffective against new variants or zero-day binaries with no cataloged hash.",
        "Brittle Defense: A single-bit alteration defeats MD5/SHA256 matching with zero operational cost to attackers."
    ], font_size=11)

    # Box 2: Dynamic Sandboxing
    add_card(s2, Inches(0.8) + col_w + gap, top_pos, col_w, h_pos, "2. Dynamic Sandboxing", "Virtual Machine Execution", border_color=COLOR_ORANGE)
    tb2 = s2.shapes.add_textbox(Inches(1.0) + col_w + gap, top_pos + Inches(0.8), col_w - Inches(0.4), h_pos - Inches(1.0))
    add_bullet_points(tb2.text_frame, [
        "Severe Latency: Requires 3 to 10 minutes per binary to record system calls, causing massive triage backlogs.",
        "Sandbox Evasion: Malware detects hypervisors, delays execution with sleep loops, or waits for human mouse clicks.",
        "Execution Risk: Running live hostile code risks host leakage and accidental network infection."
    ], font_size=11)

    # Box 3: Disassembly / Opcodes
    add_card(s2, Inches(0.8) + (col_w + gap)*2, top_pos, col_w, h_pos, "3. Disassembly (IDA / Ghidra)", "Static Machine Code Parsing", border_color=COLOR_BLUE)
    tb3 = s2.shapes.add_textbox(Inches(1.0) + (col_w + gap)*2, top_pos + Inches(0.8), col_w - Inches(0.4), h_pos - Inches(1.0))
    add_bullet_points(tb3.text_frame, [
        "Fragile Reverse Engineering: Complex x86/x64 instruction disassembly takes seconds to minutes per file.",
        "Anti-Disassembly Tricks: Modern packers corrupt section headers to cause disassembler crashes.",
        "Computational Overhead: Extracting N-gram opcode features consumes massive memory and storage."
    ], font_size=11)

    set_speaker_notes(s2, "Explain the problem: Over 450,000 new malware samples appear daily. Traditional signature matching fails because polymorphic packers change hashes daily. Dynamic sandboxing takes 3 to 10 minutes per file and is vulnerable to sleep loops and anti-VM tricks. Disassembly is fragile and fails when code is packed. We need an evasion-proof, zero-execution approach that runs in milliseconds.")

    # =========================================================================
    # SLIDE 3: THE BIG IDEA (AIRPORT X-RAY ANALOGY)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    apply_dark_background(s3)
    add_header(s3, "The Big Idea: The Airport X-Ray Scanner Analogy", "CORE CONCEPT & PHILOSOPHY")

    # Left: Text Explanation
    add_card(s3, Inches(0.8), Inches(1.7), Inches(5.8), Inches(5.1), "How Airport Security Works", "The Intuitive Real-World Mental Model")
    tb = s3.shapes.add_textbox(Inches(1.0), Inches(2.5), Inches(5.4), Inches(4.1))
    add_bullet_points(tb.text_frame, [
        "The Analogy: Airport security guards DO NOT open and search every single suitcase by hand. They DO NOT wait for a bomb to explode to know if it is dangerous.",
        "The Solution: Instead, bags pass through an X-ray scanner. The scanner converts physical contents into a density image. Trained screeners immediately spot prohibited shapes.",
        "The Cybersecurity Breakthrough: MalVision does the exact same thing for computer software!",
        "Zero-Execution: The file is NEVER executed. We take an 'X-ray photo' of the binary code and let a Deep Convolutional Neural Network spot the malware by its visual texture."
    ], font_size=12)

    # Right: Embedded 3D Illustration
    img_wf = "demo_presentation/project_structure_workflow_concept.jpg"
    if os.path.isfile(img_wf):
        s3.shapes.add_picture(img_wf, Inches(6.9), Inches(1.7), Inches(5.633), Inches(5.1))

    set_speaker_notes(s3, "Present the analogy: This is the easiest way to explain the project to any evaluator or audience. Just like airport security uses an X-ray scanner to view the shape of an object without opening or detonating it, MalVision takes a visual X-ray of an executable file without ever running the code. The neural network learns the distinctive visual blueprints of malware families.")

    # =========================================================================
    # SLIDE 4: HOW IT WORKS (BINARY-TO-IMAGE CONVERSION)
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    apply_dark_background(s4)
    add_header(s4, "Binary-to-Image Conversion & Visual Textures", "THEORETICAL FOUNDATION")

    # Left: Math & Heuristics
    add_card(s4, Inches(0.8), Inches(1.7), Inches(5.8), Inches(5.1), "The Nataraj Heuristic Math", "Mapping Bytes [0, 255] to Grayscale Pixels [0, 255]")
    tb = s4.shapes.add_textbox(Inches(1.0), Inches(2.5), Inches(5.4), Inches(4.1))
    add_bullet_points(tb.text_frame, [
        "Bijective Mapping: Every byte has a value from 0 to 255. A grayscale pixel brightness also ranges from 0 (black) to 255 (white). 1D bytes map directly to pixels.",
        "Dynamic Width Heuristic: Width W is chosen dynamically from file size (32px for <10KB up to 1024px for >1MB) to preserve local spatial aspect ratios.",
        "Dynamic Height & Padding: Height H = ceil(N / W). Any remainder is zero-padded (black pixels).",
        "Visual PE Sections: .text machine opcodes look like speckled static; .rdata strings look like horizontal stripes; .data buffers look like dark blocks; packed payloads look like high-entropy TV snow."
    ], font_size=11)

    # Right: Malimg Texture Samples Grid
    img_samples = "outputs/results/malimg_samples.png"
    if os.path.isfile(img_samples):
        s4.shapes.add_picture(img_samples, Inches(6.9), Inches(1.7), Inches(5.633), Inches(5.1))

    set_speaker_notes(s4, "Explain the technical conversion: Every byte is an 8-bit number between 0 and 255. A grayscale pixel also has brightness 0 to 255. So we take the bytes and arrange them in a 2D grid. The width is picked using Nataraj's lookup table so small files don't collapse and large files don't stretch. Notice on the right how different malware families look visually distinct to the human eye—and to a deep convolutional network.")

    # =========================================================================
    # SLIDE 5: SYSTEM ARCHITECTURE (FULL 4K BLUEPRINT)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    apply_dark_background(s5)
    add_header(s5, "End-to-End System Architecture Blueprint", "ENGINEERING PIPELINE")

    img_diag = "demo_presentation/pipeline_architecture_diagram.png"
    if os.path.isfile(img_diag):
        s5.shapes.add_picture(img_diag, Inches(0.8), Inches(1.6), Inches(11.733), Inches(4.5))

    # Bottom summary box
    add_card(s5, Inches(0.8), Inches(6.2), Inches(11.733), Inches(0.9), bg_color=COLOR_CARD)
    tb_bot = s5.shapes.add_textbox(Inches(1.0), Inches(6.25), Inches(11.3), Inches(0.75))
    tf_bot = tb_bot.text_frame
    p_bot = tf_bot.paragraphs[0]
    p_bot.text = "6-Stage Pipeline: (1) Static Ingestion -> (2) Nataraj Reshaping -> (3) 224x224 Tensor Prep -> (4) ResNet-18 Deep Feature Extraction -> (5) Multi-Class Softmax & Triage -> (6) Grad-CAM Explainability"
    p_bot.font.name = "Arial"
    p_bot.font.size = Pt(11)
    p_bot.font.bold = True
    p_bot.font.color.rgb = COLOR_CYAN

    set_speaker_notes(s5, "Walk through the pipeline: Stage 1 ingests the binary safely without execution. Stage 2 reshapes the 1D byte stream into a 2D grayscale image. Stage 3 resizes it to standard 224x224 dimensions and normalizes pixel values. Stage 4 runs it through our adapted ResNet-18 model. Stage 5 outputs the 26 family probabilities and triggers automated threat level triage. Stage 6 generates a Grad-CAM heatmap to prove why the decision was made.")

    # =========================================================================
    # SLIDE 6: RESNET-18 DEEP LEARNING ADAPTATION
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    apply_dark_background(s6)
    add_header(s6, "Deep Learning Backbone: ResNet-18 Adaptation", "MODEL SURGERY & OPTIMIZATION")

    col_w2 = Inches(5.7)
    add_card(s6, Inches(0.8), Inches(1.7), col_w2, Inches(5.1), "Transfer Learning Weight Surgery", "Adapting ImageNet (RGB) to Grayscale (1-Channel)")
    tb_l = s6.shapes.add_textbox(Inches(1.0), Inches(2.5), col_w2 - Inches(0.4), Inches(4.1))
    add_bullet_points(tb_l.text_frame, [
        "The Challenge: ImageNet models expect 3-channel RGB images of shape [64, 3, 7, 7]. Malware byteplots are single-channel grayscale [1, 224, 224].",
        "The Weight Surgery: Instead of training from scratch, we averaged the weights across RGB channels: W_gray = (1/3) * sum(W_RGB).",
        "The Benefit: Preserved all low-level edge, contour, and spatial frequency filters learned from millions of ImageNet images.",
        "Convergence Speed: Reached 97.86% test accuracy in just 3 training epochs on standard CPU hardware."
    ], font_size=11)

    add_card(s6, Inches(6.8), Inches(1.7), col_w2, Inches(5.1), "Hierarchical Feature Learning", "What the Residual Layers 'See'")
    tb_r = s6.shapes.add_textbox(Inches(7.0), Inches(2.5), col_w2 - Inches(0.4), Inches(4.1))
    add_bullet_points(tb_r.text_frame, [
        "Conv1 + MaxPool (64 x 56x56): Extracts section borders, sharp margins, and trailing zero-padding runs.",
        "Residual Layer 1 (64 x 56x56): Captures micro-opcodes, memory alignment static, and assembly instruction loops.",
        "Residual Layer 2 (128 x 28x28): Captures string tables, import directory tables, and data loop boundaries.",
        "Residual Layer 3 (256 x 14x14): Extracts macro structure: relative proportions of loader stub vs encrypted payload.",
        "Residual Layer 4 (512 x 7x7): Assembles the full malware family signature blueprint for classification."
    ], font_size=11)

    set_speaker_notes(s6, "Explain the model architecture: We used ResNet-18 because of residual skip connections that prevent vanishing gradients. To use transfer learning, we performed mathematical weight surgery on conv1 by averaging the 3 RGB channels into 1 grayscale channel. Early layers learn edges, middle layers learn micro-textures like string tables, and Layer 4 learns the complete malware family blueprint.")

    # =========================================================================
    # SLIDE 7: EMPIRICAL BENCHMARK RESULTS (MALIMG)
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    apply_dark_background(s7)
    add_header(s7, "Empirical Benchmark Results (Malimg Dataset)", "PERFORMANCE EVALUATION")

    # Left: Metrics Summary
    add_card(s7, Inches(0.8), Inches(1.7), Inches(4.8), Inches(5.1), "Key Quantitative Metrics", "Tested on 1,401 Unseen Test Samples")
    tb_m = s7.shapes.add_textbox(Inches(1.0), Inches(2.5), Inches(4.4), Inches(4.1))
    add_bullet_points(tb_m.text_frame, [
        "Overall Test Accuracy: 97.86% (1,371 correct out of 1,401 unseen test samples).",
        "Best Validation Loss: 0.0574 reached at Epoch 3 checkpoint with early stopping.",
        "Weighted F1-Score: 97.82% balanced across diverse sample sizes.",
        "Perfect F1 Families: 18 out of 26 families achieved 100% precision and recall.",
        "Sub-Second Latency: ~34.8 ms mean CPU inference latency per binary.",
        "Dataset Partition: Stratified 70/15/15 split across 9,339 total Malimg samples."
    ], font_size=11)

    # Right: Curves & Confusion Matrix
    img_curves = "demo_presentation/training_curves.png"
    img_cm = "demo_presentation/confusion_matrix.png"
    if os.path.isfile(img_curves):
        s7.shapes.add_picture(img_curves, Inches(5.9), Inches(1.7), Inches(6.6), Inches(2.3))
    if os.path.isfile(img_cm):
        s7.shapes.add_picture(img_cm, Inches(7.8), Inches(4.2), Inches(2.8), Inches(2.6))

    set_speaker_notes(s7, "Highlight the results: On 1,401 unseen test samples, the model achieved 97.86% test accuracy. 18 out of 26 families had a perfect 1.00 F1 score. Look at the training curves: validation loss hit 0.0574 at epoch 3 with no overfitting. The confusion matrix shows a sharp, bright diagonal, proving the model reliably distinguishes between all 26 families.")

    # =========================================================================
    # SLIDE 8: EXPLAINABLE AI (GRAD-CAM FORENSICS)
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    apply_dark_background(s8)
    add_header(s8, "Explainable AI: Solving the Black Box with Grad-CAM", "AUDITABILITY & FORENSICS")

    # Left: Explanation Text
    add_card(s8, Inches(0.8), Inches(1.7), Inches(4.8), Inches(5.1), "Why SOCs Need Explainability", "Gradient-Weighted Class Activation Mapping")
    tb_g = s8.shapes.add_textbox(Inches(1.0), Inches(2.5), Inches(4.4), Inches(4.1))
    add_bullet_points(tb_g.text_frame, [
        "The Black Box Problem: In security, an alert saying '99% Malware' without proof cannot be acted upon by incident responders.",
        "How Grad-CAM Works: It traces gradients backward from the predicted class score to Layer 4 feature maps, computing spatial importance weights.",
        "Thermal Colormap: Red hotspots indicate regions of maximum causal attention; blue regions denote neutral background.",
        "Forensic Validation: Proves the AI triggers on genuine unpacking stubs and encrypted payloads, rather than irrelevant padding or compiler headers."
    ], font_size=11)

    # Right: GradCAM Tri-Panel Image
    img_gc = "demo_presentation/gradcam_example.png"
    if os.path.isfile(img_gc):
        s8.shapes.add_picture(img_gc, Inches(5.9), Inches(2.3), Inches(6.6), Inches(3.8))

    set_speaker_notes(s8, "Explain Grad-CAM: Security analysts cannot trust a black box. With Grad-CAM, we trace the gradients back to Layer 4 to generate a thermal heatmap. The red regions show exactly where the model looked. Notice that it focuses on the active payload and unpacking stubs, proving that the model is making decisions based on genuine malware features rather than noise.")

    # =========================================================================
    # SLIDE 9: OPEN-WORLD TRIAGING (CLEAN FILE HANDLING)
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    apply_dark_background(s9)
    add_header(s9, "Open-World Triaging: Handling Clean Files (cmd.exe)", "FALSE POSITIVE MITIGATION")

    col_w3 = Inches(3.7)
    top_pos2 = Inches(1.7)
    h_pos2 = Inches(5.1)

    # Box 1: Critical
    add_card(s9, Inches(0.8), top_pos2, col_w3, h_pos2, "CRITICAL THREAT (>85%)", "Definite Family Match", border_color=COLOR_RED)
    tb1 = s9.shapes.add_textbox(Inches(1.0), top_pos2 + Inches(0.8), col_w3 - Inches(0.4), h_pos2 - Inches(1.0))
    add_bullet_points(tb1.text_frame, [
        "Confidence: > 85.0% probability.",
        "Entropy: Very low (H < 0.50). Probability is sharply peaked on one family.",
        "Tested Sample: Allaple.A scored 99.97% CRITICAL.",
        "Operational Action: Immediate host isolation, process kill, and file quarantine."
    ], font_size=11)

    # Box 2: Suspicious
    add_card(s9, Inches(0.8) + col_w3 + gap, top_pos2, col_w3, h_pos2, "SUSPICIOUS (60% - 85%)", "Probable Variant / Packed", border_color=COLOR_ORANGE)
    tb2 = s9.shapes.add_textbox(Inches(1.0) + col_w3 + gap, top_pos2 + Inches(0.8), col_w3 - Inches(0.4), h_pos2 - Inches(1.0))
    add_bullet_points(tb2.text_frame, [
        "Confidence: 60.0% to 85.0%.",
        "Entropy: Moderate (0.50 - 1.50). Secondary family correlations exist.",
        "Tested Sample: Minor polymorphic re-packer variants.",
        "Operational Action: Route to secondary sandbox for behavioral verification."
    ], font_size=11)

    # Box 3: Inconclusive
    add_card(s9, Inches(0.8) + (col_w3 + gap)*2, top_pos2, col_w3, h_pos2, "INCONCLUSIVE (<60%)", "Benign File / Clean Utility", border_color=COLOR_GREEN)
    tb3 = s9.shapes.add_textbox(Inches(1.0) + (col_w3 + gap)*2, top_pos2 + Inches(0.8), col_w3 - Inches(0.4), h_pos2 - Inches(1.0))
    add_bullet_points(tb3.text_frame, [
        "Confidence: < 60.0% probability.",
        "Entropy: High (H > 1.80). Probabilities scatter diffusely across all classes.",
        "Tested Sample: cmd.exe (35.6%), calc.exe (34.8%), notepad.exe (36.1%).",
        "Operational Action: Classified as SAFE/BENIGN. Zero false alarms!"
    ], font_size=11)

    set_speaker_notes(s9, "Address the clean file question: In traditional academic ML models, if you feed in cmd.exe or calc.exe, the model is forced to pick one of the 26 malware families. We solved this using confidence and Shannon entropy thresholding. When clean files are uploaded, the probabilities scatter thinly under 60%, triggering an INCONCLUSIVE/BENIGN badge. This prevents false positives on clean system files.")

    # =========================================================================
    # SLIDE 10: OPERATIONAL THREAT INTEL & WEB DASHBOARD
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    apply_dark_background(s10)
    add_header(s10, "Threat Intelligence & Live Interactive Web UI", "SOFTWARE PLATFORM & APPLICATION")

    # Left: Web App Details
    add_card(s10, Inches(0.8), Inches(1.7), Inches(5.8), Inches(5.1), "Threat Intelligence Dossiers", "From AI Score to Actionable Incident Response")
    tb = s10.shapes.add_textbox(Inches(1.0), Inches(2.5), Inches(5.4), Inches(4.1))
    add_bullet_points(tb.text_frame, [
        "malware_intel.py: Embedded knowledge base covering all 26 cataloged families.",
        "Operational Dossiers: Instant profile with malware category, severity level, system impacts (registry changes, memory hooks), infection vectors, and remediation playbooks.",
        "Interactive Web App (app.py): Dark cybersecurity UI with drag-and-drop, on-click byteplot viewer, and Top-K gauge meters.",
        "Batch Triage Mode: Upload dozens of files simultaneously for bulk incident response.",
        "1-Click Windows Launcher: start.bat starts the server and opens the browser automatically."
    ], font_size=11)

    # Right: Embedded Infographic
    img_struct = "demo_presentation/project_working_and_structure.png"
    if os.path.isfile(img_struct):
        s10.shapes.add_picture(img_struct, Inches(6.9), Inches(1.7), Inches(5.633), Inches(5.1))

    set_speaker_notes(s10, "Showcase the application: Instead of just returning a number, MalVision pairs every detection with a complete threat dossier—what it does, how it spreads, and how to remove it. Our Streamlit dashboard supports drag-and-drop file ingestion, batch scanning, and on-click byteplot inspection, launchable with a single click via start.bat.")

    # =========================================================================
    # SLIDE 11: CORE NOVELTY & PEER REVIEW DEFENSE
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    apply_dark_background(s11)
    add_header(s11, "Core Novelty & Defense Q&A Cheat Sheet", "ACADEMIC & TECHNICAL DEFENSE")

    add_card(s11, Inches(0.8), Inches(1.7), Inches(5.8), Inches(5.1), "The 5 Pillars of Novelty", "What Makes This System Truly Unique")
    tb_nov = s11.shapes.add_textbox(Inches(1.0), Inches(2.5), Inches(5.4), Inches(4.1))
    add_bullet_points(tb_nov.text_frame, [
        "1. Cross-Domain Computer Vision: Formulates binary analysis as spatial texture recognition, bypassing fragile code disassembly.",
        "2. Zero-Execution Safety: Analyzes code statically without emulation, defeating all runtime anti-VM, sleep, and sandbox tricks.",
        "3. Grayscale Transfer Learning: Collapses ImageNet RGB filters to 1-channel grayscale, converging to 97.86% in just 3 epochs.",
        "4. Forensic Explainability: Hooks Grad-CAM into Layer 4 to eliminate the black-box dilemma with thermal heatmaps.",
        "5. Open-World Triage Calibration: Employs Shannon entropy thresholding to reliably discriminate clean Windows files from malware."
    ], font_size=11)

    add_card(s11, Inches(6.8), Inches(1.7), Inches(5.8), Inches(5.1), "Top Examiner Viva Questions", "Quick Answers for Academic Review")
    tb_qa = s11.shapes.add_textbox(Inches(7.0), Inches(2.5), Inches(5.4), Inches(4.1))
    add_bullet_points(tb_qa.text_frame, [
        "Q: Can malware evade by modifying code?: Attackers changing variable names only alter fine micro-textures. The macro-level section blueprint remains structurally consistent across the entire family.",
        "Q: Why not use ResNet-50 or VGG-16?: ResNet-18 offers the optimal trade-off with 11.2M parameters. Deeper networks risk overfitting on grayscale patterns and add unnecessary latency.",
        "Q: Why not just use hashes?: Hashes break with a 1-byte change. Visual textures represent the functional layout of the executable, which remains consistent across polymorphic variants."
    ], font_size=11)

    set_speaker_notes(s11, "Summarize novelty: When examiners ask what is novel: (1) we treat malware as visual textures rather than running code, (2) we adapt transfer learning to grayscale, (3) we solve the black-box problem with Grad-CAM, and (4) we handle clean files like cmd.exe through entropy triaging.")

    # =========================================================================
    # SLIDE 12: CONCLUSION & LIVE DEMO
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    apply_dark_background(s12)

    add_card(s12, Inches(1.5), Inches(1.2), Inches(10.333), Inches(5.1), bg_color=COLOR_CARD, border_color=COLOR_CYAN)
    tb = s12.shapes.add_textbox(Inches(1.8), Inches(1.5), Inches(9.7), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True

    p1 = tf.paragraphs[0]
    p1.text = "CONCLUSION & PROJECT SUMMARY"
    p1.font.name = "Arial"
    p1.font.size = Pt(12)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_CYAN
    p1.space_after = Pt(14)

    p2 = tf.add_paragraph()
    p2.text = "MalVision: Explainable AI Threat Hunting"
    p2.font.name = "Arial"
    p2.font.size = Pt(28)
    p2.font.bold = True
    p2.font.color.rgb = COLOR_TEXT_MAIN
    p2.space_after = Pt(16)

    add_bullet_points(tf, [
        "97.86% Accuracy across 26 real-world malware families on the Malimg benchmark.",
        "Zero-Execution: 100% safe, instant (<35ms), and immune to runtime anti-VM evasion.",
        "Explainable AI: Layer 4 Grad-CAM heatmaps visually verify causal decision regions.",
        "Production-Ready: Interactive web UI with threat dossiers, batch triage, and 1-click startup.",
        "Open-Source Repository: https://github.com/ManasPatel126/MalVision"
    ], font_size=12)

    p_end = tf.add_paragraph()
    p_end.text = "Ready for Live Demo (start.bat)  •  Thank You  •  Questions & Discussion"
    p_end.font.name = "Arial"
    p_end.font.size = Pt(14)
    p_end.font.bold = True
    p_end.font.color.rgb = COLOR_GREEN
    p_end.space_before = Pt(18)

    set_speaker_notes(s12, "Conclude: In summary, MalVision proves that computer vision and deep learning can replace slow, risky malware sandboxes with instant, explainable texture classification. All code, models, and papers are open-sourced on GitHub. I would now like to invite the committee to the live interactive demonstration. Thank you, and I look forward to your questions.")

    prs.save(output_path)
    print(f"[SUCCESS] Presentation generated: {output_path}")
    return output_path


if __name__ == "__main__":
    build_malvision_presentation()
