"""
build_full_documentation_pdf.py

Compiles the exhaustive 16-section documentation into a publication-grade,
master technical report PDF with all tables, diagrams, equations, and benchmarks.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas for dynamic running headers and 'Page X of Y' footers."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        # Running header (pages 2+)
        if self._pageNumber > 1:
            self.setFont("Helvetica-Bold", 7.5)
            self.setFillColor(colors.HexColor("#0284c7"))
            self.drawString(54, 11 * 72 - 32, "MALVISION // COMPLETE TECHNICAL SPECIFICATION & PROJECT REPORT")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(54, 11 * 72 - 36, 8.5 * 72 - 54, 11 * 72 - 36)

        # Running footer (all pages)
        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor("#64748b"))
        self.drawString(54, 28, "MalVision: Deep Learning Malware Classification System • Full Technical Documentation")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * 72 - 54, 28, page_str)
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.5)
        self.line(54, 38, 8.5 * 72 - 54, 38)
        self.restoreState()


def build_full_pdf(filename="MalVision_Complete_Documentation.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=46,
        bottomMargin=46
    )

    styles = getSampleStyleSheet()

    # Colors
    C_PRIMARY   = colors.HexColor("#0f172a")
    C_ACCENT    = colors.HexColor("#0284c7")
    C_TEXT      = colors.HexColor("#1e293b")
    C_MUTED     = colors.HexColor("#64748b")
    C_LIGHT_BG  = colors.HexColor("#f8fafc")

    # Typography
    title_style = ParagraphStyle(
        "CoverTitle",
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=C_PRIMARY,
        spaceAfter=3
    )
    subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        fontName="Helvetica",
        fontSize=10.5,
        leading=14,
        textColor=C_ACCENT,
        spaceAfter=8
    )
    h1_style = ParagraphStyle(
        "H1_Custom",
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=C_PRIMARY,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        "H2_Custom",
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=13,
        textColor=C_ACCENT,
        spaceBefore=7,
        spaceAfter=3,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        "Body_Custom",
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=C_TEXT,
        spaceAfter=4
    )
    bullet_style = ParagraphStyle(
        "Bullet_Custom",
        fontName="Helvetica",
        fontSize=8.2,
        leading=11.5,
        textColor=C_TEXT,
        leftIndent=12,
        spaceAfter=2
    )
    callout_style = ParagraphStyle(
        "Callout",
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#0369a1")
    )
    table_cell = ParagraphStyle(
        "TableCell",
        fontName="Helvetica",
        fontSize=7.8,
        leading=10,
        textColor=C_TEXT
    )
    table_cell_bold = ParagraphStyle(
        "TableCellBold",
        fontName="Helvetica-Bold",
        fontSize=7.8,
        leading=10,
        textColor=C_PRIMARY
    )
    table_hdr = ParagraphStyle(
        "TableHdr",
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10.5,
        textColor=colors.white
    )

    story = []

    # =========================================================================
    # SECTION 1: COVER & EXECUTIVE SUMMARY
    # =========================================================================
    story.append(Paragraph("MALVISION: IMAGE-BASED MALWARE CLASSIFICATION", title_style))
    story.append(Paragraph("Complete Technical Documentation, Mathematical Formulations & Architecture Blueprint", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.2, color=C_ACCENT, spaceBefore=0, spaceAfter=8))

    # Metadata Grid
    meta_data = [
        [Paragraph("<b>Model Architecture:</b> ResNet-18 (Grayscale Adapted)", table_cell),
         Paragraph("<b>Test Accuracy:</b> 97.86% (1,401 test samples)", table_cell),
         Paragraph("<b>Classes:</b> 26 Malware Families", table_cell)],
        [Paragraph("<b>Dataset:</b> Malimg Benchmark (9,339 images)", table_cell),
         Paragraph("<b>Explainability:</b> Layer4 Grad-CAM Heatmaps", table_cell),
         Paragraph("<b>Interface:</b> Streamlit Web Threat Hunter", table_cell)]
    ]
    meta_table = Table(meta_data, colWidths=[168, 168, 168])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), C_LIGHT_BG),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 6))

    # Concept Art Graphic
    concept_art = "demo_presentation/malvision_concept_art.jpg"
    if os.path.isfile(concept_art):
        story.append(RLImage(concept_art, width=504, height=135))
        story.append(Spacer(1, 6))

    story.append(Paragraph("1. Executive Summary & Core Mission", h1_style))
    story.append(Paragraph(
        "<b>MalVision</b> is a deep-learning cybersecurity threat hunting platform that identifies and classifies malware "
        "without executing or disassembling suspicious software. By transforming raw executable files (<code>.exe</code>, <code>.dll</code>, <code>.bin</code>) "
        "into 2D grayscale byteplot textures, MalVision formulates cyber threat detection as an advanced computer vision task, achieving "
        "<b>97.86% test accuracy across 26 real-world malware families</b> with sub-50-millisecond inference time.", body_style))

    # Airport Analogy Box
    analogy = [
        Paragraph(
            "<b>The Airport X-Ray Scanner Analogy:</b> "
            "Airport security screeners do not unpack every passenger's bag by hand, nor do they wait for an item to detonate to know if it is dangerous. "
            "Instead, luggage passes through an X-ray scanner that produces a density image where specialists recognize prohibited shapes. "
            "<b>MalVision applies this exact principle to computer files:</b> converting raw executable code into visual textures where a "
            "ResNet-18 neural network instantly spots the unique structural blueprints of malware families.",
            callout_style
        )
    ]
    analogy_t = Table([[analogy]], colWidths=[504])
    analogy_t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f0f9ff")),
        ('BOX', (0,0), (-1,-1), 0.75, colors.HexColor("#bae6fd")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(analogy_t)
    story.append(Spacer(1, 6))

    story.append(Paragraph("2. Problem Statement: Why Existing Antivirus Fails", h1_style))
    story.append(Paragraph(
        "Current endpoint security relies heavily on static hash signatures (MD5/SHA256) and dynamic sandbox execution. "
        "Signatures fail because polymorphic crypters alter byte values daily, producing new hashes with zero code changes. "
        "Sandboxing takes 3-10 minutes per file, requires expensive infrastructure, and is defeated by malware sleep and anti-VM routines.", body_style))

    # Comparison Matrix
    comp_data = [
        [Paragraph("Feature / Vector", table_hdr), Paragraph("Signature Antivirus", table_hdr), Paragraph("Dynamic Sandboxing", table_hdr), Paragraph("MalVision (Our System)", table_hdr)],
        [Paragraph("Analysis Latency", table_cell_bold), Paragraph("Milliseconds", table_cell), Paragraph("3 - 10 Minutes", table_cell), Paragraph("<b>< 50 Milliseconds</b>", table_cell)],
        [Paragraph("Execution Risk", table_cell_bold), Paragraph("None (passive lookup)", table_cell), Paragraph("High (runs hostile code)", table_cell), Paragraph("<b>Zero (read-only mapping)</b>", table_cell)],
        [Paragraph("Sandbox Evasion", table_cell_bold), Paragraph("Not Applicable", table_cell), Paragraph("Highly Vulnerable (sleep tricks)", table_cell), Paragraph("<b>Immune (code never executes)</b>", table_cell)],
        [Paragraph("Polymorphic Resilience", table_cell_bold), Paragraph("Fails completely", table_cell), Paragraph("Moderate", table_cell), Paragraph("<b>High (shared macro textures)</b>", table_cell)],
        [Paragraph("Explainability", table_cell_bold), Paragraph("None", table_cell), Paragraph("Audit log traces", table_cell), Paragraph("<b>Grad-CAM Visual Heatmaps</b>", table_cell)]
    ]
    comp_table = Table(comp_data, colWidths=[110, 115, 125, 154])
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_PRIMARY),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#94a3b8")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, C_LIGHT_BG]),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(comp_table)

    story.append(PageBreak())

    # =========================================================================
    # SECTION 2: BINARY TO IMAGE CONVERSION & HEURISTIC MATH
    # =========================================================================
    story.append(Paragraph("3. Theoretical Foundations: Binary-to-Image Conversion", h1_style))
    story.append(Paragraph(
        "Any digital binary file is an ordered array of 8-bit unsigned bytes: $b_i \\in [0, 255]$. "
        "In 8-bit grayscale imaging, pixel brightness is defined identically: $p_i \\in [0, 255]$ (where 0 = pure black, 255 = pure white). "
        "Following the seminal methodology of <b>Nataraj et al. (2011)</b>, the byte array is reshaped into a 2D matrix using a file-size-to-width heuristic table. "
        "For a file with $N$ bytes and assigned width $W$, height is $H = \\lceil N / W \\rceil$, and remaining cells $(H \\times W - N)$ are zero-padded (black pixels):", body_style))

    # Width Table
    width_data = [
        [Paragraph("File Size Range", table_hdr), Paragraph("Width (W)", table_hdr), Paragraph("Architectural Rationale & Visual Properties", table_hdr),
         Paragraph("File Size Range", table_hdr), Paragraph("Width (W)", table_hdr), Paragraph("Architectural Rationale & Visual Properties", table_hdr)],
        [Paragraph("< 10 KB", table_cell), Paragraph("32 px", table_cell_bold), Paragraph("Prevents 1-pixel line collapse.", table_cell),
         Paragraph("100 - 200 KB", table_cell), Paragraph("384 px", table_cell_bold), Paragraph("Accommodates multi-section droppers.", table_cell)],
        [Paragraph("10 - 30 KB", table_cell), Paragraph("64 px", table_cell_bold), Paragraph("Preserves row counts for dialers.", table_cell),
         Paragraph("200 - 500 KB", table_cell), Paragraph("512 px", table_cell_bold), Paragraph("Balanced aspect ratio for trojans.", table_cell)],
        [Paragraph("30 - 60 KB", table_cell), Paragraph("128 px", table_cell_bold), Paragraph("Captures header-to-code shifts.", table_cell),
         Paragraph("500 KB - 1 MB", table_cell), Paragraph("768 px", table_cell_bold), Paragraph("Preserves distinct code vs icon blobs.", table_cell)],
        [Paragraph("60 - 100 KB", table_cell), Paragraph("256 px", table_cell_bold), Paragraph("Standard resolution for PE tools.", table_cell),
         Paragraph("> 1 MB", table_cell), Paragraph("1024 px", table_cell_bold), Paragraph("High definition for complex suites.", table_cell)]
    ]
    width_table = Table(width_data, colWidths=[65, 52, 135, 65, 52, 135])
    width_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e293b")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#94a3b8")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, C_LIGHT_BG]),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(width_table)
    story.append(Spacer(1, 4))

    story.append(Paragraph("Visual Anatomy of PE Binary Sections", h2_style))
    story.append(Paragraph("• <b>PE Header / DOS Stub:</b> High-contrast geometric alternating stripes containing signature 'MZ' bytes and section offsets.", bullet_style))
    story.append(Paragraph("• <b>.text Section (Machine Opcodes):</b> Fine-grained, speckled 'sand/static' pattern caused by frequent x86 jumps, calls, and instructions.", bullet_style))
    story.append(Paragraph("• <b>.rdata & String Tables:</b> Distinct horizontal striated bands containing ASCII messages, URL paths, and registry keys.", bullet_style))
    story.append(Paragraph("• <b>.data Section:</b> Uniform dark blocks representing uninitialized variables, global buffers, and padding zeros.", bullet_style))
    story.append(Paragraph("• <b>Packed / Encrypted Payloads:</b> Chaotic, high-entropy 'TV static snow' caused by encryption randomizing byte frequencies.", bullet_style))

    story.append(Spacer(1, 4))
    story.append(Paragraph("4. ResNet-18 Deep Convolutional Backbone", h1_style))
    story.append(Paragraph(
        "We utilize an adapted <b>ResNet-18 (Residual Network)</b> with identity shortcut connections: $\\mathcal{H}(x) = \\mathcal{F}(x) + x$, "
        "allowing deep gradient propagation without vanishing. We adapted the first convolutional layer (<code>conv1</code>) by averaging "
        "pretrained ImageNet weights across the 3 RGB channels: $\\mathbf{W}_{\\text{gray}} = \\frac{1}{3} \\sum_{c=0}^2 \\mathbf{W}_{\\text{RGB}}$, "
        "enabling the model to accept 1-channel grayscale inputs while retaining all learned edge and texture filters.", body_style))

    resnet_data = [
        [Paragraph("Layer Block", table_hdr), Paragraph("Output Dimension", table_hdr), Paragraph("Spatial Semantics & Learned Features", table_hdr)],
        [Paragraph("Input Tensor", table_cell_bold), Paragraph("1 x 224 x 224", table_cell), Paragraph("Normalized grayscale byteplot (mean=0.5, std=0.5 scaling).", table_cell)],
        [Paragraph("Conv1 + MaxPool", table_cell_bold), Paragraph("64 x 112 x 112", table_cell), Paragraph("Low-level features: Sharp section boundaries and padding runs.", table_cell)],
        [Paragraph("Residual Layer 1", table_cell_bold), Paragraph("64 x 56 x 56", table_cell), Paragraph("Opcode static: Instruction sequences and repetitive loop structures.", table_cell)],
        [Paragraph("Residual Layer 2", table_cell_bold), Paragraph("128 x 28 x 28", table_cell), Paragraph("Micro-textures: String tables, data boundaries, and import directory tables.", table_cell)],
        [Paragraph("Residual Layer 3", table_cell_bold), Paragraph("256 x 14 x 14", table_cell), Paragraph("Macro structure: Proportions of loader stub vs. encrypted payload sections.", table_cell)],
        [Paragraph("Residual Layer 4", table_cell_bold), Paragraph("512 x 7 x 7", table_cell), Paragraph("Malware family signatures: Distinct family architectural blueprint.", table_cell)],
        [Paragraph("Adaptive AvgPool", table_cell_bold), Paragraph("512 x 1 x 1", table_cell), Paragraph("Global pooling: Flattens 2D spatial features into a 512-dimensional vector.", table_cell)],
        [Paragraph("FC Classification Head", table_cell_bold), Paragraph("26 Classes", table_cell), Paragraph("Softmax probability distribution: $\\sum_{j=1}^{26} P(\\text{Family}_j) = 1.0$.", table_cell)]
    ]
    resnet_table = Table(resnet_data, colWidths=[115, 95, 294])
    resnet_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_PRIMARY),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#94a3b8")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, C_LIGHT_BG]),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(resnet_table)

    story.append(PageBreak())

    # =========================================================================
    # SECTION 3: FULL ARCHITECTURE BLUEPRINT & RESULTS
    # =========================================================================
    story.append(Paragraph("5. End-to-End System Architecture Blueprint", h1_style))
    story.append(Paragraph(
        "Below is the complete engineering pipeline tracing an uninspected binary from raw byte ingestion to final multi-class probability scoring and Grad-CAM interpretability:", body_style))

    diagram_path = "demo_presentation/pipeline_architecture_diagram.png"
    if os.path.isfile(diagram_path):
        story.append(RLImage(diagram_path, width=504, height=195))
        story.append(Spacer(1, 4))

    story.append(Paragraph("6. Empirical Benchmark Results (Malimg Benchmark)", h1_style))
    story.append(Paragraph(
        "The model was evaluated using a stratified 70/15/15 split on the benchmark Malimg dataset (9,339 samples across 26 families):", body_style))

    metrics_data = [
        [Paragraph("Evaluation Metric", table_hdr), Paragraph("Measured Score", table_hdr), Paragraph("Operational Significance & Reliability", table_hdr)],
        [Paragraph("<b>Overall Test Accuracy</b>", table_cell), Paragraph("<b>97.86%</b>", table_cell_bold), Paragraph("1,371 correct classifications out of 1,401 unseen test samples.", table_cell)],
        [Paragraph("<b>Best Validation Loss</b>", table_cell), Paragraph("<b>0.0574</b>", table_cell_bold), Paragraph("Achieved at Epoch 3 checkpoint with early stopping safeguard.", table_cell)],
        [Paragraph("<b>Perfect F1-Score Families</b>", table_cell), Paragraph("<b>18 of 26</b>", table_cell_bold), Paragraph("100% precision & recall on Allaple, Fakerean, Yuner, VB.AT, etc.", table_cell)],
        [Paragraph("<b>Inference Latency</b>", table_cell), Paragraph("<b>~35 ms</b>", table_cell_bold), Paragraph("Sub-second classification on standard CPU hardware.", table_cell)]
    ]
    metrics_table = Table(metrics_data, colWidths=[130, 85, 289])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f766e")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#94a3b8")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, C_LIGHT_BG]),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(metrics_table)
    story.append(Spacer(1, 4))

    # Plots side by side
    curves_path = "demo_presentation/training_curves.png"
    cm_path     = "demo_presentation/confusion_matrix.png"
    if os.path.isfile(curves_path) and os.path.isfile(cm_path):
        plots_table = Table([
            [RLImage(curves_path, width=248, height=130), RLImage(cm_path, width=248, height=130)],
            [Paragraph("<b>Figure A:</b> Training & Validation Curves", table_cell),
             Paragraph("<b>Figure B:</b> 26-Class Confusion Matrix", table_cell)]
        ], colWidths=[252, 252])
        plots_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 1),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ]))
        story.append(plots_table)

    story.append(PageBreak())

    # =========================================================================
    # SECTION 4: EXPLAINABLE AI, TRIAGING & DEFENSE CHEAT SHEET
    # =========================================================================
    story.append(Paragraph("7. Explainable AI: Grad-CAM Decision Heatmaps", h1_style))
    story.append(Paragraph(
        "To eliminate the 'black box' problem, MalVision implements <b>Grad-CAM (Gradient-Weighted Class Activation Mapping)</b>. "
        "It backpropagates gradients from the predicted class score to <code>layer4</code> feature maps, calculates channel weights $\\alpha_k$, "
        "and projects a thermal overlay (Red = highest attention, Blue = lowest attention) over the original binary byteplot:", body_style))

    gradcam_path = "demo_presentation/gradcam_example.png"
    if os.path.isfile(gradcam_path):
        story.append(RLImage(gradcam_path, width=504, height=135))
        story.append(Paragraph("<b>Figure C:</b> 3-Panel Grad-CAM Output (Original Byteplot → Activation Heatmap → Decision Overlay)", table_cell))
        story.append(Spacer(1, 4))

    story.append(Paragraph("8. Automated Threat Triage Levels", h1_style))
    triage_data = [
        [Paragraph("Threat Level", table_hdr), Paragraph("Confidence", table_hdr), Paragraph("Operational Verdict & Incident Response Action", table_hdr)],
        [Paragraph("<font color='#dc2626'><b>CRITICAL</b></font>", table_cell), Paragraph("> 85%", table_cell_bold), Paragraph("Definite match to known malware family. Isolate host and quarantine binary immediately.", table_cell)],
        [Paragraph("<font color='#d97706'><b>SUSPICIOUS</b></font>", table_cell), Paragraph("60% - 85%", table_cell_bold), Paragraph("Probable variant or modified sample. Route to secondary sandbox for behavioral audit.", table_cell)],
        [Paragraph("<font color='#16a34a'><b>INCONCLUSIVE</b></font>", table_cell), Paragraph("< 60%", table_cell_bold), Paragraph("Likely benign Windows executable (e.g. cmd.exe) or unindexed clean utility.", table_cell)]
    ]
    triage_table = Table(triage_data, colWidths=[90, 80, 334])
    triage_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_PRIMARY),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#94a3b8")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, C_LIGHT_BG]),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(triage_table)
    story.append(Spacer(1, 4))

    story.append(Paragraph("9. Project Defense & Viva Q&A Cheat Sheet", h1_style))
    qa_list = [
        ("Q: Why convert binaries to images instead of using disassembled opcodes (IDA Pro)?",
         "A: Disassembling code requires complex static parsing, takes seconds to minutes, and fails when binaries are packed or obfuscated with anti-disassembly tricks. Image conversion takes under 10 milliseconds, reads raw byte values directly, and bypasses disassembly failures entirely."),
        ("Q: What prevents malware authors from modifying their code to evade your CNN?",
         "A: While authors easily change variable names or insert junk opcodes to alter hash signatures, doing so only alters minor micro-textures. The macro-level section blueprint (e.g. tiny code stub + massive encrypted overlay) remains visually consistent across the entire family."),
        ("Q: How does the system handle clean / benign Windows files like cmd.exe?",
         "A: Through confidence thresholding and entropy analysis. When clean software is tested, its visual layout does not match any malicious family. Softmax probabilities scatter thinly across all classes, keeping the top score below 60% and triggering an INCONCLUSIVE / BENIGN triage verdict."),
        ("Q: How did you adapt a pretrained 3-channel RGB model to 1-channel Grayscale?",
         "A: We modified the first convolutional layer (conv1). The original ImageNet weights had shape [64, 3, 7, 7]. We averaged the weights across the 3 RGB channel dimensions into shape [64, 1, 7, 7], retaining all pretrained edge-detection filters while accepting single-channel grayscale input.")
    ]

    for q, a in qa_list:
        qa_box = [
            Paragraph(f"<b>{q}</b>", table_cell_bold),
            Paragraph(a, table_cell)
        ]
        qa_t = Table([[qa_box]], colWidths=[504])
        qa_t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), C_LIGHT_BG),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(qa_t)
        story.append(Spacer(1, 2.5))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[SUCCESS] Complete Documentation PDF compiled: {filename}")
    return filename


if __name__ == "__main__":
    build_full_pdf()
