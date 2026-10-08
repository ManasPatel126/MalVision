"""
create_presentation.py

Generates a publication-grade, widescreen (16:9) PowerPoint presentation (.pptx)
for the MalVision project with pure programmatic vector illustrations, technical diagrams,
academic benchmark metrics, structured comparative tables, and comprehensive speaker notes.

Zero external image dependencies - all diagrams are constructed using native python-pptx shapes
to guarantee zero bounding box overflow, crisp scaling at any resolution, and flawless presentation formatting.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE


# -----------------------------------------------------------------------------
# Color Palette (Dark Cybersecurity Keynote Theme)
# -----------------------------------------------------------------------------
COLOR_BG          = RGBColor(7, 12, 20)       # #070c14 Deep Obsidian
COLOR_CARD        = RGBColor(14, 23, 38)      # #0e1726 Midnight Slate
COLOR_CARD_ALT    = RGBColor(18, 30, 49)      # #121e31 Slightly lighter container
COLOR_CARD_BORDER = RGBColor(28, 46, 71)      # #1c2e47 Default subtle border
COLOR_CODE_BG     = RGBColor(9, 16, 26)       # #09101a Deep inset contrast

COLOR_CYAN        = RGBColor(0, 212, 255)     # #00d4ff Glowing Cyan (Primary)
COLOR_BLUE        = RGBColor(56, 139, 253)    # #388bfd Neon Blue (Technical)
COLOR_GREEN       = RGBColor(0, 230, 118)     # #00e676 Emerald Green (Success / Benign)
COLOR_RED         = RGBColor(255, 23, 68)     # #ff1744 Critical Crimson (Malware / Fail)
COLOR_ORANGE      = RGBColor(255, 145, 0)     # #ff9100 Amber Warning (Suspicious / Sandbox)
COLOR_PURPLE      = RGBColor(163, 113, 247)   # #a371f7 Neural Purple (DL / Architecture)

COLOR_TEXT_MAIN   = RGBColor(255, 255, 255)   # #ffffff Pure White
COLOR_TEXT_MUTED  = RGBColor(143, 163, 191)   # #8fa3bf Slate Silver
COLOR_TEXT_DIM    = RGBColor(90, 108, 133)    # #5a6c85 Dim Silver


# -----------------------------------------------------------------------------
# Fundamental Layout Helpers
# -----------------------------------------------------------------------------
def apply_dark_background(slide):
    """Fills the slide background with the deep obsidian cybersecurity color."""
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = COLOR_BG


def add_header(slide, title_text, category_text="MALVISION // TECHNICAL PRESENTATION"):
    """Adds a standardized publication-grade header with category badge and accent line."""
    # Category tag
    tb_cat = slide.shapes.add_textbox(Inches(0.8), Inches(0.35), Inches(11.733), Inches(0.3))
    tf_cat = tb_cat.text_frame
    tf_cat.word_wrap = True
    tf_cat.margin_left = Inches(0)
    tf_cat.margin_top = Inches(0)
    p_cat = tf_cat.paragraphs[0]
    p_cat.text = category_text.upper()
    p_cat.font.name = "Arial"
    p_cat.font.size = Pt(9.5)
    p_cat.font.bold = True
    p_cat.font.color.rgb = COLOR_CYAN

    # Main Slide Title
    tb_title = slide.shapes.add_textbox(Inches(0.8), Inches(0.65), Inches(11.733), Inches(0.55))
    tf_title = tb_title.text_frame
    tf_title.word_wrap = True
    tf_title.margin_left = Inches(0)
    tf_title.margin_top = Inches(0)
    p_title = tf_title.paragraphs[0]
    p_title.text = title_text
    p_title.font.name = "Arial"
    p_title.font.size = Pt(21)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_TEXT_MAIN

    # Accent underline
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.25), Inches(11.733), Inches(0.02))
    line.fill.solid()
    line.fill.fore_color.rgb = COLOR_CARD_BORDER
    line.line.color.rgb = COLOR_CARD_BORDER


def add_card(slide, left, top, width, height, title=None, subtitle=None, tag=None, tag_color=COLOR_CYAN,
             border_color=COLOR_CARD_BORDER, bg_color=COLOR_CARD):
    """
    Creates a rounded card container with crisp borders and optional header text.
    Carefully padded to guarantee child elements never overflow the bounding box.
    """
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    card.line.color.rgb = border_color
    card.line.width = Pt(1.2)

    # If tag is supplied, draw a small pill badge in upper right of card
    if tag:
        tag_w = Inches(1.8)
        tag_h = Inches(0.26)
        tag_l = left + width - tag_w - Inches(0.2)
        tag_t = top + Inches(0.12)
        badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, tag_l, tag_t, tag_w, tag_h)
        badge.fill.solid()
        badge.fill.fore_color.rgb = COLOR_CODE_BG
        badge.line.color.rgb = tag_color
        badge.line.width = Pt(1.0)
        tf_b = badge.text_frame
        tf_b.word_wrap = False
        tf_b.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf_b.margin_left = Inches(0.05)
        tf_b.margin_right = Inches(0.05)
        tf_b.margin_top = Inches(0)
        tf_b.margin_bottom = Inches(0)
        pb = tf_b.paragraphs[0]
        pb.alignment = PP_ALIGN.CENTER
        pb.text = tag
        pb.font.name = "Arial"
        pb.font.size = Pt(8.5)
        pb.font.bold = True
        pb.font.color.rgb = tag_color

    if title:
        tb = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.12), width - Inches(0.4), Inches(0.55))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0)
        tf.margin_top = Inches(0)
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = "Arial"
        p.font.size = Pt(12.5)
        p.font.bold = True
        p.font.color.rgb = COLOR_TEXT_MAIN
        if subtitle:
            p_sub = tf.add_paragraph()
            p_sub.text = subtitle
            p_sub.font.name = "Arial"
            p_sub.font.size = Pt(9.0)
            p_sub.font.color.rgb = COLOR_TEXT_MUTED
            p_sub.space_before = Pt(2)

    return card


def add_bullets(slide, left, top, width, height, points, font_size=9.5, line_spacing_pt=3):
    """
    Inserts clean bullet items into a textbox with strict word wrap and zero excessive margins.
    Highlights prefixes (before ':') in glowing cyan for high visual scanability.
    """
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0)
    tf.margin_right = Inches(0)
    tf.margin_top = Inches(0)
    tf.margin_bottom = Inches(0)

    for i, pt in enumerate(points):
        p = tf.add_paragraph() if i > 0 else tf.paragraphs[0]
        p.font.name = "Arial"
        p.font.size = Pt(font_size)
        p.space_after = Pt(line_spacing_pt)

        if ":" in pt:
            prefix, rest = pt.split(":", 1)
            run1 = p.add_run()
            run1.text = prefix + ":"
            run1.font.bold = True
            run1.font.color.rgb = COLOR_CYAN
            run2 = p.add_run()
            run2.text = rest
            run2.font.bold = False
            run2.font.color.rgb = COLOR_TEXT_MAIN
        else:
            run = p.add_run()
            run.text = pt
            run.font.color.rgb = COLOR_TEXT_MAIN

    return tb


def draw_kpi_box(slide, left, top, width, height, value_text, label_text, sublabel_text=None,
                 accent_color=COLOR_CYAN):
    """Draws a high-impact metric KPI counter box."""
    box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    box.fill.solid()
    box.fill.fore_color.rgb = COLOR_CODE_BG
    box.line.color.rgb = accent_color
    box.line.width = Pt(1.2)

    tb = slide.shapes.add_textbox(left + Inches(0.1), top + Inches(0.08), width - Inches(0.2), height - Inches(0.16))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0)
    tf.margin_top = Inches(0)

    p_val = tf.paragraphs[0]
    p_val.text = value_text
    p_val.font.name = "Arial"
    p_val.font.size = Pt(20)
    p_val.font.bold = True
    p_val.font.color.rgb = accent_color

    p_lbl = tf.add_paragraph()
    p_lbl.text = label_text
    p_lbl.font.name = "Arial"
    p_lbl.font.size = Pt(9.0)
    p_lbl.font.bold = True
    p_lbl.font.color.rgb = COLOR_TEXT_MAIN

    if sublabel_text:
        p_sub = tf.add_paragraph()
        p_sub.text = sublabel_text
        p_sub.font.name = "Arial"
        p_sub.font.size = Pt(7.5)
        p_sub.font.color.rgb = COLOR_TEXT_MUTED


def draw_verdict_banner(slide, left, top, width, height, headline, details, accent_color=COLOR_RED):
    """Draws a bottom verdict / status banner inside comparison cards."""
    banner = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    banner.fill.solid()
    banner.fill.fore_color.rgb = COLOR_CODE_BG
    banner.line.color.rgb = accent_color
    banner.line.width = Pt(1.0)

    tb = slide.shapes.add_textbox(left + Inches(0.12), top + Inches(0.06), width - Inches(0.24), height - Inches(0.12))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0)
    tf.margin_top = Inches(0)

    p1 = tf.paragraphs[0]
    p1.text = headline
    p1.font.name = "Arial"
    p1.font.size = Pt(9.5)
    p1.font.bold = True
    p1.font.color.rgb = accent_color

    p2 = tf.add_paragraph()
    p2.text = details
    p2.font.name = "Arial"
    p2.font.size = Pt(8.5)
    p2.font.color.rgb = COLOR_TEXT_MUTED


def set_speaker_notes(slide, notes_text):
    """Attaches complete speaker guidance notes to the slide."""
    notes_slide = slide.notes_slide
    tf = notes_slide.notes_text_frame
    tf.text = notes_text


# -----------------------------------------------------------------------------
# Main Presentation Builder
# -----------------------------------------------------------------------------
def build_malvision_presentation(output_path="MalVision_Presentation.pptx"):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # =========================================================================
    # SLIDE 1: TITLE SLIDE (COVER / HERO)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    apply_dark_background(s1)

    # Left Hero Container Card
    add_card(s1, Inches(0.8), Inches(1.4), Inches(5.8), Inches(5.4),
             border_color=COLOR_CYAN, bg_color=COLOR_CARD)

    # Pill badge
    badge = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.1), Inches(1.7), Inches(3.2), Inches(0.3))
    badge.fill.solid()
    badge.fill.fore_color.rgb = COLOR_CODE_BG
    badge.line.color.rgb = COLOR_CYAN
    badge.line.width = Pt(1.0)
    tf_b = badge.text_frame
    tf_b.margin_left = Inches(0.08)
    tf_b.margin_top = Inches(0.02)
    p_b = tf_b.paragraphs[0]
    p_b.text = "CYBERSECURITY // DEEP LEARNING SYSTEM"
    p_b.font.name = "Arial"
    p_b.font.size = Pt(8.5)
    p_b.font.bold = True
    p_b.font.color.rgb = COLOR_CYAN

    # Title & Text
    tb1 = s1.shapes.add_textbox(Inches(1.1), Inches(2.15), Inches(5.2), Inches(3.2))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    tf1.margin_left = Inches(0)
    tf1.margin_top = Inches(0)

    p_title = tf1.paragraphs[0]
    p_title.text = "MALVISION"
    p_title.font.name = "Arial"
    p_title.font.size = Pt(38)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_TEXT_MAIN

    p_sub = tf1.add_paragraph()
    p_sub.text = "Image-Based Malware Classification & Threat Hunting"
    p_sub.font.name = "Arial"
    p_sub.font.size = Pt(13)
    p_sub.font.bold = True
    p_sub.font.color.rgb = COLOR_BLUE
    p_sub.space_before = Pt(4)
    p_sub.space_after = Pt(10)

    p_desc = tf1.add_paragraph()
    p_desc.text = "Transmuting raw unexecuted binary software into 2D spatial grayscale textures to identify 26 malware families with 97.86% accuracy using ResNet-18 and Grad-CAM explainability."
    p_desc.font.name = "Arial"
    p_desc.font.size = Pt(10)
    p_desc.font.color.rgb = COLOR_TEXT_MUTED
    p_desc.space_after = Pt(14)

    # 3 Mini Stat Pills at bottom of left hero card
    pills = [
        ("ZERO EXECUTION", "100% Host Safe", COLOR_GREEN),
        ("34.8ms LATENCY", "Real-Time Scan", COLOR_CYAN),
        ("GRAD-CAM", "Forensic Auditing", COLOR_PURPLE)
    ]
    pill_w = Inches(1.65)
    pill_gap = Inches(0.12)
    for i, (p_top_t, p_bot_t, col) in enumerate(pills):
        pl = Inches(1.1) + i * (pill_w + pill_gap)
        pt = Inches(5.2)
        p_box = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, pl, pt, pill_w, Inches(0.65))
        p_box.fill.solid()
        p_box.fill.fore_color.rgb = COLOR_CODE_BG
        p_box.line.color.rgb = col
        p_box.line.width = Pt(1.0)
        tf_p = p_box.text_frame
        tf_p.margin_left = Inches(0.06)
        tf_p.margin_top = Inches(0.06)
        tf_p.word_wrap = True
        pp1 = tf_p.paragraphs[0]
        pp1.text = p_top_t
        pp1.font.name = "Arial"
        pp1.font.size = Pt(8.0)
        pp1.font.bold = True
        pp1.font.color.rgb = col
        pp2 = tf_p.add_paragraph()
        pp2.text = p_bot_t
        pp2.font.name = "Arial"
        pp2.font.size = Pt(7.5)
        pp2.font.color.rgb = COLOR_TEXT_MUTED

    # Author metadata
    tb_meta = s1.shapes.add_textbox(Inches(1.1), Inches(6.1), Inches(5.2), Inches(0.4))
    tf_meta = tb_meta.text_frame
    tf_meta.margin_left = Inches(0)
    tf_meta.margin_top = Inches(0)
    p_meta = tf_meta.paragraphs[0]
    p_meta.text = "Author: Manas Kumar  •  Academic & Technical Defense  •  2026"
    p_meta.font.name = "Arial"
    p_meta.font.size = Pt(9.0)
    p_meta.font.bold = True
    p_meta.font.color.rgb = COLOR_GREEN

    # Right Hero Illustration Card: PROGRAMMATIC PIPELINE SCHEMATIC
    add_card(s1, Inches(6.833), Inches(1.4), Inches(5.7), Inches(5.4),
             title="SYSTEM ARCHITECTURE SCHEMATIC",
             subtitle="Dual-Phase Computer Vision & Threat Triage Workflow",
             tag="VECTOR BLUEPRINT", tag_color=COLOR_CYAN,
             border_color=COLOR_CARD_BORDER, bg_color=COLOR_CARD)

    # 4 Connected Stages Stacked Vertically
    stages = [
        ("STAGE 01: RAW HOSTILE PE INGESTION",
         "Static file stream • 0% Code execution • Bypasses runtime evasion",
         COLOR_RED),
        ("STAGE 02: NATARAJ 2D TEXTURE PROJECTION",
         "Dynamic width W(size) • Maps [0, 255] bytes to grayscale pixel density",
         COLOR_BLUE),
        ("STAGE 03: RESNET-18 DEEP VISION BACKBONE",
         "Grayscale weight surgery • 4 residual stages • 11.2M parameters",
         COLOR_PURPLE),
        ("STAGE 04: MULTI-FAMILY TRIAGE & GRAD-CAM",
         "97.86% Family classification • Layer 4 heatmaps • MITRE ATT&CK intel",
         COLOR_GREEN)
    ]
    st_top = Inches(2.2)
    st_h = Inches(0.85)
    st_gap = Inches(0.2)

    for i, (title, desc, accent) in enumerate(stages):
        cur_top = st_top + i * (st_h + st_gap)
        s_box = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.1), cur_top, Inches(5.166), st_h)
        s_box.fill.solid()
        s_box.fill.fore_color.rgb = COLOR_CODE_BG
        s_box.line.color.rgb = accent
        s_box.line.width = Pt(1.2)

        tb_s = s1.shapes.add_textbox(Inches(7.25), cur_top + Inches(0.1), Inches(4.85), st_h - Inches(0.2))
        tf_s = tb_s.text_frame
        tf_s.word_wrap = True
        tf_s.margin_left = Inches(0)
        tf_s.margin_top = Inches(0)

        p1 = tf_s.paragraphs[0]
        p1.text = title
        p1.font.name = "Arial"
        p1.font.size = Pt(9.5)
        p1.font.bold = True
        p1.font.color.rgb = accent

        p2 = tf_s.add_paragraph()
        p2.text = desc
        p2.font.name = "Arial"
        p2.font.size = Pt(8.5)
        p2.font.color.rgb = COLOR_TEXT_MUTED
        p2.space_before = Pt(2)

        # Connector Arrow downwards
        if i < 3:
            arrow = s1.shapes.add_shape(MSO_SHAPE.DOWN_ARROW,
                                        Inches(9.55), cur_top + st_h + Inches(0.03),
                                        Inches(0.25), Inches(0.14))
            arrow.fill.solid()
            arrow.fill.fore_color.rgb = COLOR_CYAN
            arrow.line.color.rgb = COLOR_CYAN

    set_speaker_notes(s1, "Welcome committee and colleagues. Today I present MalVision, an AI platform that converts raw unexecuted malware binaries into 2D grayscale textures to classify 26 families with 97.86% accuracy using ResNet-18. It requires zero execution of hostile code and provides Grad-CAM explainability.")

    # =========================================================================
    # SLIDE 2: THE PROBLEM (WHY ANTIVIRUS FAILS TODAY)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    apply_dark_background(s2)
    add_header(s2, "The Core Problem: Why Modern Antivirus Fails", "THREAT LANDSCAPE & MOTIVATION")

    col_w = Inches(3.7)
    gap = Inches(0.316)
    top_pos = Inches(1.55)
    h_pos = Inches(5.45)

    # Box 1: Signature AV (Red Accent)
    c1_left = Inches(0.8)
    add_card(s2, c1_left, top_pos, col_w, h_pos,
             title="1. Signature Hashes", subtitle="MD5 / SHA256 Blacklisting",
             tag="TRADITIONAL DEFENSE", tag_color=COLOR_RED,
             border_color=COLOR_RED)
    add_bullets(s2, c1_left + Inches(0.2), top_pos + Inches(0.75), col_w - Inches(0.4), Inches(3.2), [
        "• Polymorphic Evasion: Attackers use UPX, Themida, and custom crypters that alter byte hashes on every build.",
        "• Zero-Day Blindspot: Completely blind to novel variants or zero-day binaries with no cataloged hash in threat feeds.",
        "• Brittle Matching: Flipping a single arbitrary bit defeats hash matching with zero operational cost to attackers."
    ], font_size=9.5, line_spacing_pt=8)
    draw_verdict_banner(s2, c1_left + Inches(0.2), top_pos + Inches(4.2), col_w - Inches(0.4), Inches(1.0),
                        "STATUS: BYPASSED IN SECONDS",
                        "Attacker Cost: Zero • Hash Database Obsolescence: 100% on new builds",
                        accent_color=COLOR_RED)

    # Box 2: Dynamic Sandboxing (Amber Accent)
    c2_left = Inches(0.8) + col_w + gap
    add_card(s2, c2_left, top_pos, col_w, h_pos,
             title="2. Dynamic Sandboxes", subtitle="Virtual Machine Execution",
             tag="BEHAVIORAL ANALYSIS", tag_color=COLOR_ORANGE,
             border_color=COLOR_ORANGE)
    add_bullets(s2, c2_left + Inches(0.2), top_pos + Inches(0.75), col_w - Inches(0.4), Inches(3.2), [
        "• Severe Latency: Requires 3 to 10 minutes per binary to capture API calls, creating massive triage bottlenecks.",
        "• Sleep Evasion: Malware detects hypervisors, delays execution with sleep loops, or waits for human mouse clicks.",
        "• Host Escape Risk: Running active hostile code risks VM sandbox escape and accidental internal network infection."
    ], font_size=9.5, line_spacing_pt=8)
    draw_verdict_banner(s2, c2_left + Inches(0.2), top_pos + Inches(4.2), col_w - Inches(0.4), Inches(1.0),
                        "STATUS: SEVERE TRIAGE BACKLOG",
                        "Queue Delay: 3-10 min/binary • Vulnerable to anti-analysis delay loops",
                        accent_color=COLOR_ORANGE)

    # Box 3: Disassembly / Opcodes (Blue Accent)
    c3_left = Inches(0.8) + (col_w + gap) * 2
    add_card(s2, c3_left, top_pos, col_w, h_pos,
             title="3. Static Disassembly", subtitle="IDA Pro / Ghidra Decompilation",
             tag="REVERSE ENGINEERING", tag_color=COLOR_BLUE,
             border_color=COLOR_BLUE)
    add_bullets(s2, c3_left + Inches(0.2), top_pos + Inches(0.75), col_w - Inches(0.4), Inches(3.2), [
        "• Fragile Parsing: Complex x86/x64 instruction disassembly takes seconds to minutes per file.",
        "• Anti-Disassembly Tricks: Malicious packers intentionally corrupt PE headers, crashing disassemblers.",
        "• Storage Burden: Extracting N-gram opcode tables and control-flow graphs consumes gigabytes of memory."
    ], font_size=9.5, line_spacing_pt=8)
    draw_verdict_banner(s2, c3_left + Inches(0.2), top_pos + Inches(4.2), col_w - Inches(0.4), Inches(1.0),
                        "STATUS: CRASHES ON PACKED CODE",
                        "Header Sabotage: High vulnerability • Memory Footprint: Unscalable",
                        accent_color=COLOR_BLUE)

    set_speaker_notes(s2, "Explain the problem: Over 450,000 new malware samples appear daily. Traditional signature matching fails because polymorphic packers change hashes daily. Dynamic sandboxing takes 3 to 10 minutes per file and is vulnerable to sleep loops. Disassembly is fragile and fails when code is packed. We need an evasion-proof, zero-execution approach that runs in milliseconds.")

    # =========================================================================
    # SLIDE 3: THE BIG IDEA (AIRPORT X-RAY ANALOGY)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    apply_dark_background(s3)
    add_header(s3, "The Big Idea: The Airport X-Ray Scanner Analogy", "CORE CONCEPT & PHILOSOPHY")

    col_w2 = Inches(5.7)
    gap2 = Inches(0.333)

    # Left: Conceptual Walkthrough
    add_card(s3, Inches(0.8), Inches(1.55), col_w2, Inches(5.45),
             title="The Airport Baggage Screening Metaphor",
             subtitle="Why Inspection Without Execution is the Superior Paradigm",
             tag="INTUITIVE MENTAL MODEL", tag_color=COLOR_CYAN)

    steps_analogy = [
        ("THE DILEMMA: EXPLOSIVE RISK",
         "Airport security cannot open and search every suitcase by hand. Opening takes too long, and detonating a bomb to test if it is dangerous defeats the entire purpose.",
         COLOR_RED),
        ("THE SOLUTION: NON-INVASIVE X-RAY",
         "Luggage passes through an X-ray scanner without opening. Physical contents are converted into a 2D density image. Prohibited shapes are recognized instantly.",
         COLOR_GREEN),
        ("THE CYBERSECURITY PARALLEL",
         "Executing hostile code in a sandbox risks host infection. Disassembling millions of instructions takes too long. Running malware to see what it does is dangerous.",
         COLOR_ORANGE),
        ("THE MALVISION BREAKTHROUGH",
         "Take an optical 'X-ray photo' of the raw unexecuted binary! Let a Deep Convolutional Neural Network classify the threat based on spatial texture blueprints.",
         COLOR_CYAN)
    ]
    box_t = Inches(2.25)
    box_h = Inches(1.05)
    box_g = Inches(0.12)
    for i, (head, desc, col) in enumerate(steps_analogy):
        bt = box_t + i * (box_h + box_g)
        sb = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), bt, col_w2 - Inches(0.4), box_h)
        sb.fill.solid()
        sb.fill.fore_color.rgb = COLOR_CODE_BG
        sb.line.color.rgb = col
        sb.line.width = Pt(1.0)

        tb_sb = s3.shapes.add_textbox(Inches(1.15), bt + Inches(0.08), col_w2 - Inches(0.7), box_h - Inches(0.16))
        tf_sb = tb_sb.text_frame
        tf_sb.word_wrap = True
        tf_sb.margin_left = Inches(0)
        tf_sb.margin_top = Inches(0)
        p1 = tf_sb.paragraphs[0]
        p1.text = head
        p1.font.name = "Arial"
        p1.font.size = Pt(9.0)
        p1.font.bold = True
        p1.font.color.rgb = col
        p2 = tf_sb.add_paragraph()
        p2.text = desc
        p2.font.name = "Arial"
        p2.font.size = Pt(8.0)
        p2.font.color.rgb = COLOR_TEXT_MUTED
        p2.space_before = Pt(2)

    # Right: Comparative Paradigm Diagram
    add_card(s3, Inches(6.833), Inches(1.55), col_w2, Inches(5.45),
             title="Comparative Paradigm Workflow",
             subtitle="Traditional Detonation vs. MalVision Vision Inspection",
             tag="PARADIGM SHIFT", tag_color=COLOR_GREEN)

    # Top Track: Traditional AV (Red)
    t1_box = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.05), Inches(2.3), Inches(5.266), Inches(1.85))
    t1_box.fill.solid()
    t1_box.fill.fore_color.rgb = COLOR_CODE_BG
    t1_box.line.color.rgb = COLOR_RED
    t1_box.line.width = Pt(1.2)

    tb_t1 = s3.shapes.add_textbox(Inches(7.2), Inches(2.4), Inches(4.966), Inches(1.65))
    tf_t1 = tb_t1.text_frame
    tf_t1.word_wrap = True
    tf_t1.margin_left = Inches(0)
    tf_t1.margin_top = Inches(0)
    p_t1 = tf_t1.paragraphs[0]
    p_t1.text = "TRADITIONAL RUNTIME DETONATION (HIGH RISK)"
    p_t1.font.name = "Arial"
    p_t1.font.size = Pt(9.5)
    p_t1.font.bold = True
    p_t1.font.color.rgb = COLOR_RED

    add_bullets(s3, Inches(7.2), Inches(2.7), Inches(4.966), Inches(1.3), [
        "• Workflow: Hostile Binary  -->  Spin up VM Sandbox  -->  Execute Code for 5 mins",
        "• Failure Mode: Malware detects hypervisor or sleeps 10 minutes to bypass analysis.",
        "• Result: High infrastructure cost, massive latency backlog, and infection risk."
    ], font_size=8.5, line_spacing_pt=3)

    # Bottom Track: MalVision (Green)
    t2_box = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.05), Inches(4.35), Inches(5.266), Inches(1.85))
    t2_box.fill.solid()
    t2_box.fill.fore_color.rgb = COLOR_CODE_BG
    t2_box.line.color.rgb = COLOR_GREEN
    t2_box.line.width = Pt(1.2)

    tb_t2 = s3.shapes.add_textbox(Inches(7.2), Inches(4.45), Inches(4.966), Inches(1.65))
    tf_t2 = tb_t2.text_frame
    tf_t2.word_wrap = True
    tf_t2.margin_left = Inches(0)
    tf_t2.margin_top = Inches(0)
    p_t2 = tf_t2.paragraphs[0]
    p_t2.text = "MALVISION COMPUTER VISION (ZERO RISK)"
    p_t2.font.name = "Arial"
    p_t2.font.size = Pt(9.5)
    p_t2.font.bold = True
    p_t2.font.color.rgb = COLOR_GREEN

    add_bullets(s3, Inches(7.2), Inches(4.75), Inches(4.966), Inches(1.3), [
        "• Workflow: Hostile Binary  -->  2D Texture Projection  -->  ResNet-18 Vision Model",
        "• Breakthrough: File is NEVER executed; immune to anti-VM and sleep tricks.",
        "• Result: 34.8ms scan speed, 97.86% accuracy, and 100% host safety guaranteed."
    ], font_size=8.5, line_spacing_pt=3)

    # Bottom Banner
    draw_verdict_banner(s3, Inches(7.05), Inches(6.35), Inches(5.266), Inches(0.55),
                        "STRATEGIC ADVANTAGE",
                        "Replaces slow, dangerous sandbox execution with instant, safe visual inspection.",
                        accent_color=COLOR_CYAN)

    set_speaker_notes(s3, "Present the analogy: This is the easiest way to explain the project. Just like airport security uses an X-ray scanner to view the shape of an object without opening or detonating it, MalVision takes a visual X-ray of an executable file without ever running the code.")

    # =========================================================================
    # SLIDE 4: HOW IT WORKS (BINARY-TO-IMAGE CONVERSION)
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    apply_dark_background(s4)
    add_header(s4, "Binary-to-Image Conversion & Visual Textures", "THEORETICAL FOUNDATION")

    # Left: Nataraj Heuristic Math
    add_card(s4, Inches(0.8), Inches(1.55), col_w2, Inches(5.45),
             title="The Nataraj Bijective Mapping",
             subtitle="Mapping 1D Byte Arrays to 2D Spatial Grayscale Textures",
             tag="MATHEMATICAL FORMULATION", tag_color=COLOR_CYAN)

    # Formula Box
    f_box = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(2.25), col_w2 - Inches(0.4), Inches(0.7))
    f_box.fill.solid()
    f_box.fill.fore_color.rgb = COLOR_CODE_BG
    f_box.line.color.rgb = COLOR_CYAN
    f_box.line.width = Pt(1.0)
    tf_f = f_box.text_frame
    tf_f.margin_left = Inches(0.1)
    tf_f.margin_top = Inches(0.08)
    pf1 = tf_f.paragraphs[0]
    pf1.text = "Byte Stream B = [b_0, b_1, ... b_N-1] where b_i ∈ [0, 255]"
    pf1.font.name = "Courier New"
    pf1.font.size = Pt(8.5)
    pf1.font.bold = True
    pf1.font.color.rgb = COLOR_CYAN
    pf2 = tf_f.add_paragraph()
    pf2.text = "Pixel Brightness P(x, y) = b_(y*W + x)  |  Height H = ceil(N / W)"
    pf2.font.name = "Courier New"
    pf2.font.size = Pt(8.5)
    pf2.font.color.rgb = COLOR_TEXT_MAIN

    add_bullets(s4, Inches(1.0), Inches(3.05), col_w2 - Inches(0.4), Inches(1.1), [
        "• Bijective Mapping: Every 8-bit byte maps 1:1 to a grayscale pixel (0=Black, 255=White).",
        "• Dynamic Width Table: Width W scales with file size to preserve visual aspect ratio."
    ], font_size=9.0, line_spacing_pt=3)

    # Dynamic Width Table
    tb_table = s4.shapes.add_table(8, 2, Inches(1.0), Inches(4.2), col_w2 - Inches(0.4), Inches(2.55))
    table = tb_table.table
    table.columns[0].width = Inches(3.1)
    table.columns[1].width = Inches(2.2)

    width_data = [
        ("Binary File Size Range", "Dynamic Width (W)"),
        ("< 10 KB", "32 pixels"),
        ("10 KB – 30 KB", "64 pixels"),
        ("30 KB – 60 KB", "128 pixels"),
        ("60 KB – 100 KB", "256 pixels"),
        ("100 KB – 200 KB", "384 pixels"),
        ("200 KB – 500 KB", "512 pixels"),
        ("> 1,000 KB (1 MB)", "1024 pixels")
    ]
    for row_idx, (col0, col1) in enumerate(width_data):
        c0 = table.cell(row_idx, 0)
        c1 = table.cell(row_idx, 1)
        for cell, txt in [(c0, col0), (c1, col1)]:
            cell.fill.solid()
            cell.fill.fore_color.rgb = COLOR_CARD_ALT if row_idx == 0 else COLOR_CODE_BG
            cell.margin_left = Inches(0.08)
            cell.margin_right = Inches(0.08)
            cell.margin_top = Inches(0.02)
            cell.margin_bottom = Inches(0.02)
            p = cell.text_frame.paragraphs[0]
            p.text = txt
            p.font.name = "Arial"
            p.font.size = Pt(8.0 if row_idx > 0 else 8.5)
            p.font.bold = (row_idx == 0)
            p.font.color.rgb = COLOR_CYAN if row_idx == 0 else COLOR_TEXT_MAIN

    # Right: PE Anatomy & Visual Textures
    add_card(s4, Inches(6.833), Inches(1.55), col_w2, Inches(5.45),
             title="PE Anatomy & Visual Texture Blueprint",
             subtitle="How Executable Sections Translate into Grayscale Patterns",
             tag="SPATIAL SEMANTICS", tag_color=COLOR_PURPLE)

    pe_sections = [
        ("PE HEADER & DOS STUB (0x0000)",
         "Magic MZ signature, COFF header, optional header. Appears as structured dark horizontal bars with fixed byte offsets.",
         COLOR_CYAN),
        (".TEXT CODE SECTION (MACHINE OPCODES)",
         "Compiled x86/x64 assembly instructions. Appears as speckled, fine-grained static texture with high local entropy.",
         COLOR_BLUE),
        (".RDATA & .DATA CONSTANTS / STRINGS",
         "ASCII strings, import address tables (IAT), and global variables. Appears as parallel horizontal bands and dark strips.",
         COLOR_PURPLE),
        ("PACKED / ENCRYPTED SHELLCODE",
         "UPX / Themida compressed payloads. Appears as dense high-frequency TV snow with near-maximum Shannon entropy.",
         COLOR_RED)
    ]
    pe_t = Inches(2.25)
    pe_h = Inches(1.0)
    pe_g = Inches(0.12)
    for i, (name, desc, col) in enumerate(pe_sections):
        pt = pe_t + i * (pe_h + pe_g)
        sb = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.05), pt, col_w2 - Inches(0.4), pe_h)
        sb.fill.solid()
        sb.fill.fore_color.rgb = COLOR_CODE_BG
        sb.line.color.rgb = col
        sb.line.width = Pt(1.0)

        tb_sb = s4.shapes.add_textbox(Inches(7.2), pt + Inches(0.08), col_w2 - Inches(0.7), pe_h - Inches(0.16))
        tf_sb = tb_sb.text_frame
        tf_sb.word_wrap = True
        tf_sb.margin_left = Inches(0)
        tf_sb.margin_top = Inches(0)
        p1 = tf_sb.paragraphs[0]
        p1.text = name
        p1.font.name = "Arial"
        p1.font.size = Pt(8.5)
        p1.font.bold = True
        p1.font.color.rgb = col
        p2 = tf_sb.add_paragraph()
        p2.text = desc
        p2.font.name = "Arial"
        p2.font.size = Pt(8.0)
        p2.font.color.rgb = COLOR_TEXT_MUTED
        p2.space_before = Pt(2)

    draw_verdict_banner(s4, Inches(7.05), Inches(6.35), col_w2 - Inches(0.4), Inches(0.55),
                        "KEY DISCOVERY",
                        "Malware authors can change hashes, but cannot hide the macro visual structure of code sections.",
                        accent_color=COLOR_GREEN)

    set_speaker_notes(s4, "Explain the technical conversion: Every byte is an 8-bit number between 0 and 255, matching grayscale pixels. Nataraj's lookup table scales image width dynamically. Different PE sections create visually distinctive textures: headers are dark bars, code sections are speckled static, strings are stripes, and packed malware is high-entropy snow.")

    # =========================================================================
    # SLIDE 5: SYSTEM ARCHITECTURE (FULL PIPELINE BLUEPRINT)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    apply_dark_background(s5)
    add_header(s5, "End-to-End System Architecture Blueprint", "ENGINEERING PIPELINE")

    # Top Area: 6 Horizontal Connected Stages Container
    top_box_w = Inches(11.733)
    top_box_h = Inches(2.25)
    add_card(s5, Inches(0.8), Inches(1.55), top_box_w, top_box_h,
             title="6-STAGE END-TO-END PIPELINE ARCHITECTURE",
             subtitle="From Raw Unexecuted Binary Stream to Incident Response Dossier",
             tag="DISTRIBUTED WORKFLOW", tag_color=COLOR_CYAN)

    pipeline_stages = [
        ("01. INGESTION", "Static file handle\n0% execution\nImmutable buffer", COLOR_RED),
        ("02. RESHAPE", "Nataraj formula\nDynamic width\n[0, 255] pixels", COLOR_BLUE),
        ("03. PREP", "Resize 224x224\nTensor convert\nNormalization", COLOR_CYAN),
        ("04. RESNET-18", "4 residual stages\nWeight surgery\n11.2M params", COLOR_PURPLE),
        ("05. TRIAGE", "26-class softmax\nEntropy gating\nThreat levels", COLOR_ORANGE),
        ("06. GRAD-CAM", "Layer 4 heatmap\nThermal overlay\nAudit dossier", COLOR_GREEN)
    ]
    p_step_w = Inches(1.68)
    p_step_h = Inches(1.2)
    p_step_gap = Inches(0.28)
    p_step_top = Inches(2.35)

    for i, (st_name, st_desc, st_col) in enumerate(pipeline_stages):
        sl = Inches(1.05) + i * (p_step_w + p_step_gap)
        sb = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, sl, p_step_top, p_step_w, p_step_h)
        sb.fill.solid()
        sb.fill.fore_color.rgb = COLOR_CODE_BG
        sb.line.color.rgb = st_col
        sb.line.width = Pt(1.2)

        tb_sb = s5.shapes.add_textbox(sl + Inches(0.05), p_step_top + Inches(0.06), p_step_w - Inches(0.1), p_step_h - Inches(0.12))
        tf_sb = tb_sb.text_frame
        tf_sb.word_wrap = True
        tf_sb.margin_left = Inches(0)
        tf_sb.margin_top = Inches(0)
        p1 = tf_sb.paragraphs[0]
        p1.text = st_name
        p1.font.name = "Arial"
        p1.font.size = Pt(8.5)
        p1.font.bold = True
        p1.font.color.rgb = st_col
        p2 = tf_sb.add_paragraph()
        p2.text = st_desc
        p2.font.name = "Arial"
        p2.font.size = Pt(7.5)
        p2.font.color.rgb = COLOR_TEXT_MUTED
        p2.space_before = Pt(2)

        # Connector Arrow rightwards
        if i < 5:
            arr_l = sl + p_step_w + Inches(0.05)
            arr = s5.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, arr_l, p_step_top + Inches(0.48), Inches(0.18), Inches(0.22))
            arr.fill.solid()
            arr.fill.fore_color.rgb = COLOR_CYAN
            arr.line.color.rgb = COLOR_CYAN

    # Bottom Area: 3 Specification Cards
    bot_top = Inches(4.0)
    bot_h = Inches(3.0)
    b_col_w = Inches(3.7)
    b_gap = Inches(0.316)

    # Card A: Latency & Compute
    add_card(s5, Inches(0.8), bot_top, b_col_w, bot_h,
             title="Latency & Compute Specs", subtitle="Commodity CPU Benchmarks",
             tag="PERFORMANCE", tag_color=COLOR_CYAN)
    add_bullets(s5, Inches(1.0), bot_top + Inches(0.75), b_col_w - Inches(0.4), Inches(2.1), [
        "• Inference Latency: 34.8 ms mean per file on commodity multi-core CPU.",
        "• Model Footprint: 42.7 MB (.pth weights), highly portable for edge deployment.",
        "• Memory Overhead: < 180 MB active RAM during continuous batch scanning.",
        "• Throughput: Processes > 28 binaries/sec per core without GPU acceleration."
    ], font_size=8.5, line_spacing_pt=5)

    # Card B: Security & Safety
    add_card(s5, Inches(0.8) + b_col_w + b_gap, bot_top, b_col_w, bot_h,
             title="Security & Safety Guarantees", subtitle="Zero-Execution Principles",
             tag="SAFETY ASSURANCE", tag_color=COLOR_GREEN)
    add_bullets(s5, Inches(1.0) + b_col_w + b_gap, bot_top + Inches(0.75), b_col_w - Inches(0.4), Inches(2.1), [
        "• Zero-Execution: 0.00% machine instructions executed; 100% read-only analysis.",
        "• Anti-VM Immunity: Completely unaffected by sleep loops or hypervisor checks.",
        "• Memory Safety: Sandboxed Python byte array manipulation prevents exploits.",
        "• Host Protection: No execution permissions required for storage partitions."
    ], font_size=8.5, line_spacing_pt=5)

    # Card C: Output Deliverables
    add_card(s5, Inches(0.8) + (b_col_w + b_gap) * 2, bot_top, b_col_w, bot_h,
             title="Output Deliverables", subtitle="Incident Response Triage Package",
             tag="SOC ACTIONABILITY", tag_color=COLOR_PURPLE)
    add_bullets(s5, Inches(1.0) + (b_col_w + b_gap) * 2, bot_top + Inches(0.75), b_col_w - Inches(0.4), Inches(2.1), [
        "• Family Match: Predicted malware family out of 26 cataloged classes.",
        "• Triage Tier: CRITICAL (>85%), SUSPICIOUS (60-85%), or BENIGN (<60%).",
        "• Visual Evidence: Layer 4 Grad-CAM thermal attention heatmap overlay.",
        "• Remediation Dossier: MITRE ATT&CK tactics, impact analysis, and playbooks."
    ], font_size=8.5, line_spacing_pt=5)

    set_speaker_notes(s5, "Walk through the pipeline: Stage 1 ingests the binary safely without execution. Stage 2 reshapes the byte stream. Stage 3 resizes to 224x224. Stage 4 runs through ResNet-18 in 34.8ms. Stage 5 performs triage with confidence and entropy. Stage 6 generates a Grad-CAM heatmap.")

    # =========================================================================
    # SLIDE 6: RESNET-18 DEEP LEARNING ADAPTATION
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    apply_dark_background(s6)
    add_header(s6, "Deep Learning Backbone: ResNet-18 Adaptation", "MODEL SURGERY & OPTIMIZATION")

    # Left: Weight Surgery
    add_card(s6, Inches(0.8), Inches(1.55), col_w2, Inches(5.45),
             title="Transfer Learning Weight Surgery",
             subtitle="Adapting ImageNet RGB Filters to 1-Channel Grayscale Textures",
             tag="CONV1 SURGERY", tag_color=COLOR_CYAN)

    # Formula Box
    f_surg = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(2.25), col_w2 - Inches(0.4), Inches(0.75))
    f_surg.fill.solid()
    f_surg.fill.fore_color.rgb = COLOR_CODE_BG
    f_surg.line.color.rgb = COLOR_CYAN
    f_surg.line.width = Pt(1.0)
    tf_sg = f_surg.text_frame
    tf_sg.margin_left = Inches(0.1)
    tf_sg.margin_top = Inches(0.08)
    psg1 = tf_sg.paragraphs[0]
    psg1.text = "Standard ImageNet Conv1: [64 filters, 3 channels, 7x7 kernel]"
    psg1.font.name = "Courier New"
    psg1.font.size = Pt(8.5)
    psg1.font.bold = True
    psg1.font.color.rgb = COLOR_TEXT_MUTED
    psg2 = tf_sg.add_paragraph()
    psg2.text = "Weight Surgery: W_gray = (1/3) * (W_R + W_G + W_B) -> [64, 1, 7, 7]"
    psg2.font.name = "Courier New"
    psg2.font.size = Pt(8.5)
    psg2.font.bold = True
    psg2.font.color.rgb = COLOR_CYAN

    add_bullets(s6, Inches(1.0), Inches(3.1), col_w2 - Inches(0.4), Inches(2.4), [
        "• The Dimensional Mismatch: ImageNet vision models require 3-channel RGB. Malware textures are 1-channel grayscale.",
        "• Mathematical Mean Projection: Summing and dividing the 3 channels by 3 preserves all pretrained low-level visual edge, contour, and spatial frequency filters.",
        "• Cold-Start Elimination: Training from scratch requires 50+ epochs and prone to local minima. Surgery allowed 97.86% convergence in only 3 epochs.",
        "• Residual Architecture: 8 residual skip connections bypass degradation and enable smooth gradient backpropagation during fine-tuning."
    ], font_size=9.0, line_spacing_pt=6)

    draw_verdict_banner(s6, Inches(1.0), Inches(5.65), col_w2 - Inches(0.4), Inches(1.15),
                        "PARAMETER & COMPUTE EFFICIENCY",
                        "Total Parameters: 11,189,850 • Model Size: 42.7 MB • Epochs to Converge: 3 • Hardware: CPU",
                        accent_color=COLOR_GREEN)

    # Right: Layer Stack Architecture
    add_card(s6, Inches(6.833), Inches(1.55), col_w2, Inches(5.45),
             title="Hierarchical Residual Layer Breakdown",
             subtitle="What Each Stage in ResNet-18 'Sees' in Binary Byteplots",
             tag="LAYER VISUALIZATION", tag_color=COLOR_PURPLE)

    layer_stack = [
        ("CONV1 + MAXPOOL (64 Filters, 56x56)",
         "Detects macro structural borders, PE section alignment margins, and trailing zero-padding blocks.",
         COLOR_CYAN),
        ("RESIDUAL LAYER 1 (64 Filters, 56x56)",
         "Extracts repetitive micro-opcodes, memory alignment static, and assembly instruction loops.",
         COLOR_BLUE),
        ("RESIDUAL LAYER 2 (128 Filters, 28x28)",
         "Captures string table margins, import address table (IAT) structures, and loop boundaries.",
         COLOR_PURPLE),
        ("RESIDUAL LAYER 3 (256 Filters, 14x14)",
         "Extracts macro ratios: proportion of unpacker stub vs. encrypted hostile payload.",
         COLOR_ORANGE),
        ("RESIDUAL LAYER 4 (512 Filters, 7x7)",
         "Synthesizes the global malware family fingerprint blueprint fed to the 26-class classifier.",
         COLOR_GREEN)
    ]
    ls_top = Inches(2.25)
    ls_h = Inches(0.85)
    ls_g = Inches(0.08)

    for i, (name, desc, col) in enumerate(layer_stack):
        lst = ls_top + i * (ls_h + ls_g)
        sb = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.05), lst, col_w2 - Inches(0.4), ls_h)
        sb.fill.solid()
        sb.fill.fore_color.rgb = COLOR_CODE_BG
        sb.line.color.rgb = col
        sb.line.width = Pt(1.0)

        tb_sb = s6.shapes.add_textbox(Inches(7.2), lst + Inches(0.06), col_w2 - Inches(0.7), ls_h - Inches(0.12))
        tf_sb = tb_sb.text_frame
        tf_sb.word_wrap = True
        tf_sb.margin_left = Inches(0)
        tf_sb.margin_top = Inches(0)
        p1 = tf_sb.paragraphs[0]
        p1.text = name
        p1.font.name = "Arial"
        p1.font.size = Pt(8.5)
        p1.font.bold = True
        p1.font.color.rgb = col
        p2 = tf_sb.add_paragraph()
        p2.text = desc
        p2.font.name = "Arial"
        p2.font.size = Pt(7.5)
        p2.font.color.rgb = COLOR_TEXT_MUTED
        p2.space_before = Pt(2)

    set_speaker_notes(s6, "Explain ResNet-18 adaptation: To use transfer learning, we performed mathematical weight surgery on conv1 by averaging the 3 RGB channels into 1 grayscale channel. Early layers learn edges, middle layers learn micro-textures like string tables, and Layer 4 learns the complete malware family blueprint.")

    # =========================================================================
    # SLIDE 7: EMPIRICAL BENCHMARK RESULTS (MALIMG DATASET)
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    apply_dark_background(s7)
    add_header(s7, "Empirical Benchmark Results (Malimg Dataset)", "PERFORMANCE EVALUATION")

    # Left: Quantitative Metrics
    add_card(s7, Inches(0.8), Inches(1.55), col_w2, Inches(5.45),
             title="Quantitative Performance Benchmarks",
             subtitle="Evaluated on 1,401 Unseen Real-World Test Binaries",
             tag="MALIMG BENCHMARK", tag_color=COLOR_CYAN)

    # 4 KPI Stat Boxes (2x2 Grid)
    kpis = [
        ("97.86%", "Test Accuracy", "1,371 / 1,401 correct", COLOR_GREEN),
        ("97.82%", "Weighted F1-Score", "Balanced across classes", COLOR_CYAN),
        ("0.0574", "Validation Loss", "Epoch 3 checkpoint", COLOR_BLUE),
        ("34.8 ms", "Inference Latency", "Per binary on CPU", COLOR_PURPLE)
    ]
    kw = Inches(2.55)
    kh = Inches(0.85)
    for i, (val, lbl, sub, col) in enumerate(kpis):
        r = i // 2
        c = i % 2
        kl = Inches(1.0) + c * (kw + Inches(0.2))
        kt = Inches(2.25) + r * (kh + Inches(0.12))
        draw_kpi_box(s7, kl, kt, kw, kh, val, lbl, sub, accent_color=col)

    add_bullets(s7, Inches(1.0), Inches(4.2), col_w2 - Inches(0.4), Inches(2.6), [
        "• Stratified Dataset Split: 9,339 total binaries split into 70% Train (6,537), 15% Validation (1,401), and 15% Test (1,401).",
        "• Perfect F1-Score Families: 18 out of 26 families achieved 100% precision and recall (F1 = 1.000).",
        "• Rapid Convergence: Reached peak accuracy at Epoch 3 with early stopping, preventing model overfitting.",
        "• Generalization: Consistent performance across both small (<20KB) and large (>5MB) binaries."
    ], font_size=8.5, line_spacing_pt=5)

    # Right: Comparative Benchmark Evaluation
    add_card(s7, Inches(6.833), Inches(1.55), col_w2, Inches(5.45),
             title="Comparative Benchmark Evaluation",
             subtitle="MalVision ResNet-18 vs. State-of-the-Art & Traditional Antivirus",
             tag="STATE-OF-THE-ART", tag_color=COLOR_GREEN)

    # Native PPTX Comparison Table
    tb_comp = s7.shapes.add_table(6, 5, Inches(7.05), Inches(2.25), col_w2 - Inches(0.4), Inches(2.8))
    t_comp = tb_comp.table
    t_comp.columns[0].width = Inches(1.6)
    t_comp.columns[1].width = Inches(0.9)
    t_comp.columns[2].width = Inches(0.9)
    t_comp.columns[3].width = Inches(0.9)
    t_comp.columns[4].width = Inches(1.0)

    comp_headers = ["Model / Approach", "Accuracy", "Latency", "Safe Exec", "Explainable"]
    comp_rows = [
        ("Traditional AV (Hash)", "58.4%", "1-3 ms", "Yes", "No"),
        ("Dynamic Sandbox", "84.2%", "3-10 min", "No (Risky)", "Yes"),
        ("Random Forest (Opcodes)", "91.3%", "120 ms", "Yes", "Limited"),
        ("VGG-16 Deep Vision", "96.2%", "142 ms", "Yes", "Yes"),
        ("MalVision (ResNet-18)", "97.86%", "34.8 ms", "Yes (100%)", "Yes (Grad-CAM)")
    ]

    for col_idx, h_text in enumerate(comp_headers):
        cell = t_comp.cell(0, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_CARD_ALT
        cell.margin_left = Inches(0.06)
        cell.margin_right = Inches(0.06)
        cell.margin_top = Inches(0.04)
        cell.margin_bottom = Inches(0.04)
        p = cell.text_frame.paragraphs[0]
        p.text = h_text
        p.font.name = "Arial"
        p.font.size = Pt(8.0)
        p.font.bold = True
        p.font.color.rgb = COLOR_CYAN

    for row_idx, rdata in enumerate(comp_rows):
        is_ours = (row_idx == len(comp_rows) - 1)
        for col_idx, val in enumerate(rdata):
            cell = t_comp.cell(row_idx + 1, col_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(12, 28, 44) if is_ours else COLOR_CODE_BG
            cell.margin_left = Inches(0.06)
            cell.margin_right = Inches(0.06)
            cell.margin_top = Inches(0.04)
            cell.margin_bottom = Inches(0.04)
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.name = "Arial"
            p.font.size = Pt(8.0)
            p.font.bold = is_ours
            p.font.color.rgb = COLOR_GREEN if is_ours else COLOR_TEXT_MAIN

    draw_verdict_banner(s7, Inches(7.05), Inches(5.25), col_w2 - Inches(0.4), Inches(1.55),
                        "ARCHITECTURAL SUPERIORITY",
                        "ResNet-18 delivers higher classification accuracy than VGG-16 while requiring 4x fewer parameters and running 4x faster on standard CPU hardware.",
                        accent_color=COLOR_GREEN)

    set_speaker_notes(s7, "Highlight the results: On 1,401 unseen test samples, the model achieved 97.86% test accuracy. 18 out of 26 families had a perfect 1.00 F1 score. Look at the comparison table: MalVision outperforms traditional antivirus, dynamic sandboxing, random forests, and heavier models like VGG-16.")

    # =========================================================================
    # SLIDE 8: EXPLAINABLE AI (GRAD-CAM FORENSICS)
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    apply_dark_background(s8)
    add_header(s8, "Explainable AI: Solving the Black Box with Grad-CAM", "AUDITABILITY & FORENSICS")

    # Left: Why Explainability is Mandatory
    add_card(s8, Inches(0.8), Inches(1.55), col_w2, Inches(5.45),
             title="The Black-Box Crisis in Cybersecurity",
             subtitle="Why High Accuracy Alone Is Insufficient for SOC Incident Response",
             tag="AUDIT INTEGRITY", tag_color=COLOR_RED)

    add_bullets(s8, Inches(1.0), Inches(2.25), col_w2 - Inches(0.4), Inches(3.0), [
        "• The Black-Box Dilemma: In an enterprise Security Operations Center (SOC), an AI alert stating '99% Malware' without evidence cannot be acted upon by human analysts.",
        "• Regulatory Compliance: Auditing standards (NIST, ISO 27001) require verifiable causal explanations for automated system quarantine and endpoint isolation.",
        "• Spurious Correlation Defense: Grad-CAM proves the model triggers on genuine unpacker stubs rather than irrelevant compiler padding (0x00) or PE header artifacts.",
        "• Precision Forensics: Points reverse engineers directly to the byte offset of malicious payloads within multi-megabyte binaries, cutting triage time by 90%."
    ], font_size=9.0, line_spacing_pt=7)

    draw_verdict_banner(s8, Inches(1.0), Inches(5.45), col_w2 - Inches(0.4), Inches(1.35),
                        "ENTERPRISE VALUE PROPOSITION",
                        "Grad-CAM transforms AI from an untrusted 'black-box oracle' into an auditable, courtroom-ready forensic partner for incident responders.",
                        accent_color=COLOR_CYAN)

    # Right: Grad-CAM Mathematical & Forensic Flow
    add_card(s8, Inches(6.833), Inches(1.55), col_w2, Inches(5.45),
             title="Grad-CAM Mathematical & Forensic Flow",
             subtitle="Gradient-Weighted Class Activation Mapping Mechanics",
             tag="MATH MECHANICS", tag_color=COLOR_PURPLE)

    gradcam_steps = [
        ("01. FORWARD PASS -> CLASS SCORE y^c",
         "Target binary image is propagated through ResNet-18 to compute the logit score y^c for predicted malware family c.",
         COLOR_CYAN),
        ("02. BACKWARD PASS -> LAYER 4 GRADIENTS",
         "Compute gradients ∂y^c / ∂A^k with respect to activation feature maps A^k in the final convolutional residual block.",
         COLOR_BLUE),
        ("03. GLOBAL AVERAGE POOLING -> WEIGHTS α_k^c",
         "α_k^c = (1 / Z) * ∑_i ∑_j (∂y^c / ∂A_ij^k); captures the relative importance of each feature map k to decision c.",
         COLOR_PURPLE),
        ("04. RECTIFIED COMBINATION -> HEATMAP L^c",
         "L^c = ReLU( ∑_k α_k^c A^k ); ReLU isolates positive causal features that increase the confidence of the threat label.",
         COLOR_GREEN)
    ]
    gc_top = Inches(2.25)
    gc_h = Inches(0.72)
    gc_g = Inches(0.08)

    for i, (name, desc, col) in enumerate(gradcam_steps):
        gct = gc_top + i * (gc_h + gc_g)
        sb = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.05), gct, col_w2 - Inches(0.4), gc_h)
        sb.fill.solid()
        sb.fill.fore_color.rgb = COLOR_CODE_BG
        sb.line.color.rgb = col
        sb.line.width = Pt(1.0)

        tb_sb = s8.shapes.add_textbox(Inches(7.2), gct + Inches(0.06), col_w2 - Inches(0.7), gc_h - Inches(0.12))
        tf_sb = tb_sb.text_frame
        tf_sb.word_wrap = True
        tf_sb.margin_left = Inches(0)
        tf_sb.margin_top = Inches(0)
        p1 = tf_sb.paragraphs[0]
        p1.text = name
        p1.font.name = "Arial"
        p1.font.size = Pt(8.0)
        p1.font.bold = True
        p1.font.color.rgb = col
        p2 = tf_sb.add_paragraph()
        p2.text = desc
        p2.font.name = "Arial"
        p2.font.size = Pt(7.5)
        p2.font.color.rgb = COLOR_TEXT_MUTED
        p2.space_before = Pt(2)

    # Color Interpretation Key
    draw_verdict_banner(s8, Inches(7.05), Inches(5.45), col_w2 - Inches(0.4), Inches(1.35),
                        "HEATMAP FORENSIC INTERPRETATION KEY",
                        "• RED HOTSPOTS: High causal attention -> Malicious unpacker stubs & encrypted payloads\n• BLUE BACKGROUND: Zero causal attention -> Standard PE compiler headers & zero-fill padding",
                        accent_color=COLOR_GREEN)

    set_speaker_notes(s8, "Explain Grad-CAM: Security analysts cannot trust a black box. With Grad-CAM, we trace the gradients back to Layer 4 to generate a thermal heatmap. The red regions show exactly where the model looked. Notice that it focuses on the active payload and unpacking stubs rather than noise.")

    # =========================================================================
    # SLIDE 9: OPEN-WORLD TRIAGING (CLEAN FILE HANDLING)
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    apply_dark_background(s9)
    add_header(s9, "Open-World Triaging: Handling Clean Files (cmd.exe)", "FALSE POSITIVE MITIGATION")

    # 3 Column Cards
    # Box 1: Critical (Red Accent)
    add_card(s9, c1_left, top_pos, col_w, h_pos,
             title="1. CRITICAL THREAT", subtitle="Definite Malware Family Match",
             tag="CONFIDENCE > 85%", tag_color=COLOR_RED,
             border_color=COLOR_RED)
    add_bullets(s9, c1_left + Inches(0.2), top_pos + Inches(0.75), col_w - Inches(0.4), Inches(3.2), [
        "• Softmax Probability: Strongly peaked score exceeding 85.0% on one known family.",
        "• Shannon Entropy: Extremely low (H < 0.50), proving unanimous neural consensus.",
        "• Tested Sample: Allaple.A scored 99.97% CRITICAL; Yuner.A scored 99.82% CRITICAL.",
        "• Operational Action: Immediate automated endpoint isolation and file quarantine."
    ], font_size=9.0, line_spacing_pt=7)
    draw_verdict_banner(s9, c1_left + Inches(0.2), top_pos + Inches(4.2), col_w - Inches(0.4), Inches(1.0),
                        "TRIAGE TIER: CRITICAL",
                        "Immediate Quarantine • Kill Host Process • Push IOC to Firewall",
                        accent_color=COLOR_RED)

    # Box 2: Suspicious (Amber Accent)
    add_card(s9, c2_left, top_pos, col_w, h_pos,
             title="2. SUSPICIOUS VARIANT", subtitle="Probable Variant or Packed Binary",
             tag="CONFIDENCE 60% – 85%", tag_color=COLOR_ORANGE,
             border_color=COLOR_ORANGE)
    add_bullets(s9, c2_left + Inches(0.2), top_pos + Inches(0.75), col_w - Inches(0.4), Inches(3.2), [
        "• Softmax Probability: Intermediate score between 60.0% and 85.0%.",
        "• Shannon Entropy: Moderate (0.50 <= H <= 1.50), showing secondary family correlations.",
        "• Tested Sample: Polymorphic droppers and multi-layer crypter re-packs.",
        "• Operational Action: Route to secondary deep sandbox queue for behavioral verification."
    ], font_size=9.0, line_spacing_pt=7)
    draw_verdict_banner(s9, c2_left + Inches(0.2), top_pos + Inches(4.2), col_w - Inches(0.4), Inches(1.0),
                        "TRIAGE TIER: SUSPICIOUS",
                        "Secondary Sandbox Queue • Flag Hash in SIEM • Await Analyst Review",
                        accent_color=COLOR_ORANGE)

    # Box 3: Inconclusive / Benign (Green Accent)
    add_card(s9, c3_left, top_pos, col_w, h_pos,
             title="3. INCONCLUSIVE / CLEAN", subtitle="Benign Windows Utility / Clean Executable",
             tag="CONFIDENCE < 60%", tag_color=COLOR_GREEN,
             border_color=COLOR_GREEN)
    add_bullets(s9, c3_left + Inches(0.2), top_pos + Inches(0.75), col_w - Inches(0.4), Inches(3.2), [
        "• Softmax Probability: Peak score remains well below 60.0% threshold.",
        "• Shannon Entropy: High (H > 1.80); probabilities scatter uniformly across all classes.",
        "• Real Tested Samples: cmd.exe (35.6%), calc.exe (34.8%), notepad.exe (36.1%).",
        "• Operational Action: Classified as SAFE/BENIGN. Zero false alarms raised!"
    ], font_size=9.0, line_spacing_pt=7)
    draw_verdict_banner(s9, c3_left + Inches(0.2), top_pos + Inches(4.2), col_w - Inches(0.4), Inches(1.0),
                        "TRIAGE TIER: SAFE / BENIGN",
                        "Zero False Positives • Native Windows Tools Whitelisted Safely",
                        accent_color=COLOR_GREEN)

    set_speaker_notes(s9, "Address the clean file question: In traditional closed-world academic ML models, if you feed in cmd.exe or calc.exe, the model is forced to pick one of the 26 malware families. We solved this using confidence and Shannon entropy thresholding. When clean files are uploaded, the probabilities scatter under 60%, triggering an INCONCLUSIVE badge. This prevents false alarms on clean system files.")

    # =========================================================================
    # SLIDE 10: OPERATIONAL THREAT INTEL & WEB DASHBOARD
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    apply_dark_background(s10)
    add_header(s10, "Threat Intelligence & Live Interactive Web UI", "SOFTWARE PLATFORM & APPLICATION")

    # Left: malware_intel.py Knowledge Base
    add_card(s10, Inches(0.8), Inches(1.55), col_w2, Inches(5.45),
             title="Threat Intelligence Engine (malware_intel.py)",
             subtitle="Connecting Raw AI Predictions to Actionable Incident Response",
             tag="CYBER INTELLIGENCE", tag_color=COLOR_CYAN)

    intel_items = [
        ("EXHAUSTIVE THREAT REPOSITORY",
         "Embedded knowledge base containing rich dossiers for all 26 cataloged families (worms, trojans, rootkits, droppers).",
         COLOR_CYAN),
        ("SEVERITY & IMPACT SCORING",
         "Automated risk rating (CRITICAL, HIGH, MODERATE) with technical breakdown of registry keys, process hooks, and network sockets.",
         COLOR_RED),
        ("INFECTION PATHWAY ANALYSIS",
         "Identifies primary vector: email attachments, drive-by downloads, cracked software installers, or lateral SMB movement.",
         COLOR_ORANGE),
        ("INCIDENT RESPONSE PLAYBOOKS",
         "Prescriptive removal commands, host isolation guidelines, and IOC telemetry signatures for enterprise SIEM ingestion.",
         COLOR_GREEN)
    ]
    it_top = Inches(2.25)
    it_h = Inches(0.9)
    it_g = Inches(0.12)
    for i, (name, desc, col) in enumerate(intel_items):
        itt = it_top + i * (it_h + it_g)
        sb = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), itt, col_w2 - Inches(0.4), it_h)
        sb.fill.solid()
        sb.fill.fore_color.rgb = COLOR_CODE_BG
        sb.line.color.rgb = col
        sb.line.width = Pt(1.0)

        tb_sb = s10.shapes.add_textbox(Inches(1.15), itt + Inches(0.06), col_w2 - Inches(0.7), it_h - Inches(0.12))
        tf_sb = tb_sb.text_frame
        tf_sb.word_wrap = True
        tf_sb.margin_left = Inches(0)
        tf_sb.margin_top = Inches(0)
        p1 = tf_sb.paragraphs[0]
        p1.text = name
        p1.font.name = "Arial"
        p1.font.size = Pt(8.5)
        p1.font.bold = True
        p1.font.color.rgb = col
        p2 = tf_sb.add_paragraph()
        p2.text = desc
        p2.font.name = "Arial"
        p2.font.size = Pt(8.0)
        p2.font.color.rgb = COLOR_TEXT_MUTED
        p2.space_before = Pt(2)

    draw_verdict_banner(s10, Inches(1.0), Inches(6.35), col_w2 - Inches(0.4), Inches(0.55),
                        "MITRE ATT&CK ALIGNED",
                        "Maps every detected family directly to tactical enterprise attack frameworks.",
                        accent_color=COLOR_GREEN)

    # Right: Full-Stack System Architecture Stack
    add_card(s10, Inches(6.833), Inches(1.55), col_w2, Inches(5.45),
             title="Full-Stack Application Architecture",
             subtitle="Modular Component Hierarchy & Deployment Setup",
             tag="SYSTEM STACK", tag_color=COLOR_PURPLE)

    stack_tiers = [
        ("TIER 1: PRESENTATION & USER EXPERIENCE (app.py)",
         "Streamlit dark-mode cybersecurity dashboard with drag-and-drop file ingestion, real-time byteplot viewer, and Top-K gauge meters.",
         COLOR_CYAN),
        ("TIER 2: AI INFERENCE & EXPLAINABILITY (models/)",
         "PyTorch ResNet-18 engine with weight-surgeried Conv1 and backward-hook Grad-CAM thermal attention generator.",
         COLOR_BLUE),
        ("TIER 3: KNOWLEDGE & MITRE INTELLIGENCE (malware_intel.py)",
         "Structured JSON threat intelligence engine providing automated impact analysis, severity grading, and remediation playbooks.",
         COLOR_PURPLE),
        ("TIER 4: AUTOMATED WINDOWS DEPLOYMENT (start.bat)",
         "1-click launch script performing automatic Python environment verification, dependency resolution, and browser launching.",
         COLOR_GREEN)
    ]
    st_t = Inches(2.25)
    st_h = Inches(0.9)
    st_g = Inches(0.12)
    for i, (name, desc, col) in enumerate(stack_tiers):
        stt = st_t + i * (st_h + st_g)
        sb = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.05), stt, col_w2 - Inches(0.4), st_h)
        sb.fill.solid()
        sb.fill.fore_color.rgb = COLOR_CODE_BG
        sb.line.color.rgb = col
        sb.line.width = Pt(1.0)

        tb_sb = s10.shapes.add_textbox(Inches(7.2), stt + Inches(0.06), col_w2 - Inches(0.7), st_h - Inches(0.12))
        tf_sb = tb_sb.text_frame
        tf_sb.word_wrap = True
        tf_sb.margin_left = Inches(0)
        tf_sb.margin_top = Inches(0)
        p1 = tf_sb.paragraphs[0]
        p1.text = name
        p1.font.name = "Arial"
        p1.font.size = Pt(8.5)
        p1.font.bold = True
        p1.font.color.rgb = col
        p2 = tf_sb.add_paragraph()
        p2.text = desc
        p2.font.name = "Arial"
        p2.font.size = Pt(8.0)
        p2.font.color.rgb = COLOR_TEXT_MUTED
        p2.space_before = Pt(2)

    draw_verdict_banner(s10, Inches(7.05), Inches(6.35), col_w2 - Inches(0.4), Inches(0.55),
                        "DEPLOYMENT READY",
                        "One command: .\\start.bat launches the complete web dashboard in under 3 seconds.",
                        accent_color=COLOR_CYAN)

    set_speaker_notes(s10, "Showcase the application: Instead of just returning a number, MalVision pairs every detection with a complete threat dossier—what it does, how it spreads, and how to remove it. Our Streamlit dashboard supports drag-and-drop file ingestion, batch scanning, and on-click byteplot inspection, launchable with a single click via start.bat.")

    # =========================================================================
    # SLIDE 11: CORE NOVELTY & PEER REVIEW DEFENSE
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    apply_dark_background(s11)
    add_header(s11, "Core Novelty & Defense Q&A Cheat Sheet", "ACADEMIC & TECHNICAL DEFENSE")

    # Left: The 5 Pillars of Novelty
    add_card(s11, Inches(0.8), Inches(1.55), col_w2, Inches(5.45),
             title="The 5 Pillars of Scientific Novelty",
             subtitle="Distinct Contributions Beyond Prior Academic Literature",
             tag="RESEARCH NOVELTY", tag_color=COLOR_CYAN)

    novelty_pillars = [
        ("1. CROSS-DOMAIN COMPUTER VISION",
         "Treats binary analysis as spatial texture recognition, bypassing fragile code disassembly entirely.",
         COLOR_CYAN),
        ("2. ZERO-EXECUTION STATIC SAFETY",
         "100% static analysis immune to sandbox sleep loops, hypervisor checks, and hostile code leakage.",
         COLOR_GREEN),
        ("3. GRAYSCALE TRANSFER LEARNING",
         "Mathematical weight surgery transfers ImageNet RGB filters to 1-channel grayscale in 3 epochs.",
         COLOR_BLUE),
        ("4. AUDITABLE GRAD-CAM FORENSICS",
         "Hooks Layer 4 gradients to eliminate black-box skepticism with verifiable thermal attention heatmaps.",
         COLOR_PURPLE),
        ("5. DUAL CONFIDENCE-ENTROPY TRIAGE",
         "Shannon entropy gating solves the open-world dilemma, preventing false alarms on clean files.",
         COLOR_ORANGE)
    ]
    np_top = Inches(2.25)
    np_h = Inches(0.72)
    np_g = Inches(0.08)

    for i, (name, desc, col) in enumerate(novelty_pillars):
        npt = np_top + i * (np_h + np_g)
        sb = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), npt, col_w2 - Inches(0.4), np_h)
        sb.fill.solid()
        sb.fill.fore_color.rgb = COLOR_CODE_BG
        sb.line.color.rgb = col
        sb.line.width = Pt(1.0)

        tb_sb = s11.shapes.add_textbox(Inches(1.15), npt + Inches(0.06), col_w2 - Inches(0.7), np_h - Inches(0.12))
        tf_sb = tb_sb.text_frame
        tf_sb.word_wrap = True
        tf_sb.margin_left = Inches(0)
        tf_sb.margin_top = Inches(0)
        p1 = tf_sb.paragraphs[0]
        p1.text = name
        p1.font.name = "Arial"
        p1.font.size = Pt(8.0)
        p1.font.bold = True
        p1.font.color.rgb = col
        p2 = tf_sb.add_paragraph()
        p2.text = desc
        p2.font.name = "Arial"
        p2.font.size = Pt(7.5)
        p2.font.color.rgb = COLOR_TEXT_MUTED
        p2.space_before = Pt(2)

    draw_verdict_banner(s11, Inches(1.0), Inches(6.35), col_w2 - Inches(0.4), Inches(0.55),
                        "PEER REVIEW CONTRIBUTION",
                        "Bridges computer vision and threat hunting into an evasion-resilient, production-ready system.",
                        accent_color=COLOR_GREEN)

    # Right: Examiner Viva Q&A Guide
    add_card(s11, Inches(6.833), Inches(1.55), col_w2, Inches(5.45),
             title="Top Examiner Viva Questions & Answers",
             subtitle="Prepared Defense Answers for Technical Evaluation Committees",
             tag="VIVA CHEAT SHEET", tag_color=COLOR_GREEN)

    viva_qas = [
        ("Q: CAN MALWARE EVADE BY ALTERING VARIABLE NAMES?",
         "A: Changing variable names or opcodes only alters local micro-textures. The macro-level PE section blueprint (.text, .rdata, payload ratios) remains structurally consistent across the family.",
         COLOR_CYAN),
        ("Q: WHY USE RESNET-18 OVER DEEPER NETWORKS (RESNET-50/VGG)?",
         "A: ResNet-18 offers optimal parameter efficiency (11.2M params). Deeper networks overfit on 2D byteplots and add unnecessary inference latency on commodity hardware.",
         COLOR_BLUE),
        ("Q: HOW ARE CLEAN FILES PREVENTED FROM FALSE FLAGGING?",
         "A: Clean files lack specific malware family textures, scattering probability mass across classes. Shannon entropy thresholding (H > 1.80) safely categorizes them as INCONCLUSIVE/BENIGN.",
         COLOR_PURPLE)
    ]
    vq_top = Inches(2.25)
    vq_h = Inches(1.22)
    vq_g = Inches(0.12)

    for i, (q_txt, a_txt, col) in enumerate(viva_qas):
        vqt = vq_top + i * (vq_h + vq_g)
        sb = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.05), vqt, col_w2 - Inches(0.4), vq_h)
        sb.fill.solid()
        sb.fill.fore_color.rgb = COLOR_CODE_BG
        sb.line.color.rgb = col
        sb.line.width = Pt(1.0)

        tb_sb = s11.shapes.add_textbox(Inches(7.2), vqt + Inches(0.08), col_w2 - Inches(0.7), vq_h - Inches(0.16))
        tf_sb = tb_sb.text_frame
        tf_sb.word_wrap = True
        tf_sb.margin_left = Inches(0)
        tf_sb.margin_top = Inches(0)
        p1 = tf_sb.paragraphs[0]
        p1.text = q_txt
        p1.font.name = "Arial"
        p1.font.size = Pt(8.5)
        p1.font.bold = True
        p1.font.color.rgb = col
        p2 = tf_sb.add_paragraph()
        p2.text = a_txt
        p2.font.name = "Arial"
        p2.font.size = Pt(8.0)
        p2.font.color.rgb = COLOR_TEXT_MUTED
        p2.space_before = Pt(3)

    draw_verdict_banner(s11, Inches(7.05), Inches(6.35), col_w2 - Inches(0.4), Inches(0.55),
                        "EXAMINER DEFENSE READY",
                        "Grounded in empirical benchmarks, mathematical formulations, and rigorous evaluation.",
                        accent_color=COLOR_CYAN)

    set_speaker_notes(s11, "Summarize novelty: When examiners ask what is novel: (1) we treat malware as visual textures rather than running code, (2) we adapt transfer learning to grayscale, (3) we solve the black-box problem with Grad-CAM, and (4) we handle clean files like cmd.exe through entropy triaging.")

    # =========================================================================
    # SLIDE 12: CONCLUSION & LIVE DEMO
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    apply_dark_background(s12)
    add_header(s12, "Conclusion & Interactive Demonstration", "SUMMARY & SYSTEM LAUNCH")

    # Full-Width Hero Container Card
    add_card(s12, Inches(0.8), Inches(1.55), Inches(11.733), Inches(5.45),
             title="MALVISION PROJECT SUMMARY & STRATEGIC IMPACT",
             subtitle="A Validated, Production-Grade Paradigm for Zero-Execution Threat Hunting",
             tag="READY FOR DEFENSE", tag_color=COLOR_GREEN,
             border_color=COLOR_CYAN)

    # 4 KPI Milestone Callouts (Horizontal row)
    milestones = [
        ("97.86% ACCURACY", "1,401 Unseen Samples", "Validated on Malimg across 26 families with 0.0574 validation loss.", COLOR_GREEN),
        ("34.8ms SCAN TIME", "Real-Time CPU Speed", "Instantaneous gateway scanning without expensive GPU clusters.", COLOR_CYAN),
        ("100% HOST SAFE", "Zero Execution Risk", "Immune to sandbox escape, anti-VM sleep tricks, and payload detonation.", COLOR_BLUE),
        ("AUDITABLE AI", "Layer 4 Grad-CAM", "Causal thermal heatmaps prove decisions to human incident responders.", COLOR_PURPLE)
    ]
    m_w = Inches(2.65)
    m_h = Inches(1.5)
    m_gap = Inches(0.3)
    m_top = Inches(2.35)

    for i, (m_val, m_lbl, m_desc, m_col) in enumerate(milestones):
        ml = Inches(1.1) + i * (m_w + m_gap)
        mb = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, ml, m_top, m_w, m_h)
        mb.fill.solid()
        mb.fill.fore_color.rgb = COLOR_CODE_BG
        mb.line.color.rgb = m_col
        mb.line.width = Pt(1.2)

        tb_mb = s12.shapes.add_textbox(ml + Inches(0.1), m_top + Inches(0.1), m_w - Inches(0.2), m_h - Inches(0.2))
        tf_mb = tb_mb.text_frame
        tf_mb.word_wrap = True
        tf_mb.margin_left = Inches(0)
        tf_mb.margin_top = Inches(0)

        p1 = tf_mb.paragraphs[0]
        p1.text = m_val
        p1.font.name = "Arial"
        p1.font.size = Pt(14)
        p1.font.bold = True
        p1.font.color.rgb = m_col

        p2 = tf_mb.add_paragraph()
        p2.text = m_lbl
        p2.font.name = "Arial"
        p2.font.size = Pt(9.0)
        p2.font.bold = True
        p2.font.color.rgb = COLOR_TEXT_MAIN
        p2.space_before = Pt(2)

        p3 = tf_mb.add_paragraph()
        p3.text = m_desc
        p3.font.name = "Arial"
        p3.font.size = Pt(8.0)
        p3.font.color.rgb = COLOR_TEXT_MUTED
        p3.space_before = Pt(4)

    # Bottom Live Demo Launch Panel
    demo_box = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.1), Inches(4.1), Inches(11.133), Inches(2.0))
    demo_box.fill.solid()
    demo_box.fill.fore_color.rgb = COLOR_CODE_BG
    demo_box.line.color.rgb = COLOR_GREEN
    demo_box.line.width = Pt(1.2)

    tb_demo = s12.shapes.add_textbox(Inches(1.3), Inches(4.2), Inches(10.7), Inches(1.8))
    tf_demo = tb_demo.text_frame
    tf_demo.word_wrap = True
    tf_demo.margin_left = Inches(0)
    tf_demo.margin_top = Inches(0)

    p_d1 = tf_demo.paragraphs[0]
    p_d1.text = "READY FOR LIVE INTERACTIVE DEMONSTRATION"
    p_d1.font.name = "Arial"
    p_d1.font.size = Pt(12)
    p_d1.font.bold = True
    p_d1.font.color.rgb = COLOR_GREEN

    p_d2 = tf_demo.add_paragraph()
    p_d2.text = "Windows PowerShell Execution:  .\\start.bat    |    Terminal Command:  python -m streamlit run app.py"
    p_d2.font.name = "Courier New"
    p_d2.font.size = Pt(10)
    p_d2.font.bold = True
    p_d2.font.color.rgb = COLOR_CYAN
    p_d2.space_before = Pt(6)

    p_d3 = tf_demo.add_paragraph()
    p_d3.text = "Open-Source Codebase: https://github.com/ManasPatel126/MalVision  •  MIT License  •  Full Documentation Included"
    p_d3.font.name = "Arial"
    p_d3.font.size = Pt(9.5)
    p_d3.font.color.rgb = COLOR_TEXT_MAIN
    p_d3.space_before = Pt(6)

    p_d4 = tf_demo.add_paragraph()
    p_d4.text = "Thank you for your consideration. The floor is now open for questions, technical discussion, and live system testing."
    p_d4.font.name = "Arial"
    p_d4.font.size = Pt(9.5)
    p_d4.font.bold = True
    p_d4.font.color.rgb = COLOR_TEXT_MUTED
    p_d4.space_before = Pt(6)

    set_speaker_notes(s12, "Conclude: In summary, MalVision proves that computer vision and deep learning can replace slow, risky malware sandboxes with instant, explainable texture classification. All code, models, and papers are open-sourced on GitHub. I would now like to invite the committee to the live interactive demonstration. Thank you, and I look forward to your questions.")

    prs.save(output_path)
    print(f"[SUCCESS] Presentation generated: {output_path}")
    return output_path


if __name__ == "__main__":
    build_malvision_presentation()
