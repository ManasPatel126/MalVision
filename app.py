"""
app.py -- Interactive Malware Threat Hunting Web Application

A Streamlit-based web UI that wraps the trained ResNet-18 malware classifier,
letting security analysts drag-and-drop suspicious files and get instant
visual classification with Grad-CAM explainability.

Features:
    1. Drag-and-drop file upload (.exe, .dll, .bin, .png, .jpg)
    2. Real-time 2D grayscale byteplot rendering
    3. Top-K predicted malware families with confidence gauge bars
    4. Threat level assessment (CRITICAL / SUSPICIOUS / INCONCLUSIVE)
    5. One-click Grad-CAM heatmap visualization
    6. Batch analysis mode for multiple files
    7. Sample gallery from the Malimg dataset

Launch:
    streamlit run app.py
"""

import os
import sys
import io
import tempfile
import numpy as np
import torch
import torch.nn.functional as TF
from PIL import Image
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for server
import matplotlib.pyplot as plt
import matplotlib.cm as cm

# ---------------------------------------------------------------------------
# Ensure project root is on the Python path so relative imports work
# regardless of where Streamlit launches from.
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st

# Import our existing pipeline modules
from binary_to_image import binary_to_grayscale_array, get_image_width
from model import build_model
from config import IMAGE_SIZE, MODEL_SAVE_DIR, IMAGE_OUTPUT_DIR
from malware_intel import get_malware_intel
# ---------------------------------------------------------------------------
# Professional Cyber Vector Icons (Replaces emojis with crisp SVG artwork)
# ---------------------------------------------------------------------------
SVG_SHIELD = """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#00d4ff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;margin-right:6px;"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>"""
SVG_TARGET = """<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#00d4ff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;margin-right:6px;"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="4"/></svg>"""
SVG_ACTIVITY = """<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#ff9100" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;margin-right:6px;"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>"""
SVG_NETWORK = """<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#448aff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;margin-right:6px;"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>"""
SVG_CHECK = """<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#00e676" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;margin-right:6px;"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg>"""



# ============================================================================
#  PAGE CONFIG
# ============================================================================
st.set_page_config(
    page_title="MalVision -- Malware Threat Hunter",
    page_icon="outputs/favicon.png",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================================
#  CUSTOM CSS -- dark cyber-security theme
# ============================================================================
st.markdown("""
<style>
    /* Main container */
    .stApp {
        background: linear-gradient(135deg, #0a0e17 0%, #111927 50%, #0d1321 100%);
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #0f1724;
        border-right: 1px solid #1e2d3d;
    }

    /* Headers */
    h1, h2, h3 {
        color: #00d4ff !important;
    }

    /* Threat level badges */
    .threat-critical {
        background: linear-gradient(90deg, #ff1744, #d50000);
        color: white;
        padding: 12px 24px;
        border-radius: 8px;
        font-size: 20px;
        font-weight: bold;
        text-align: center;
        box-shadow: 0 0 20px rgba(255, 23, 68, 0.4);
        animation: pulse-red 2s infinite;
    }
    .threat-suspicious {
        background: linear-gradient(90deg, #ff9100, #ff6d00);
        color: white;
        padding: 12px 24px;
        border-radius: 8px;
        font-size: 20px;
        font-weight: bold;
        text-align: center;
        box-shadow: 0 0 20px rgba(255, 145, 0, 0.3);
    }
    .threat-low {
        background: linear-gradient(90deg, #00c853, #009624);
        color: white;
        padding: 12px 24px;
        border-radius: 8px;
        font-size: 20px;
        font-weight: bold;
        text-align: center;
        box-shadow: 0 0 20px rgba(0, 200, 83, 0.3);
    }

    @keyframes pulse-red {
        0%, 100% { box-shadow: 0 0 20px rgba(255, 23, 68, 0.4); }
        50% { box-shadow: 0 0 40px rgba(255, 23, 68, 0.8); }
    }

    /* Metric cards */
    .metric-card {
        background: #141e2e;
        border: 1px solid #1e3a5f;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        margin-bottom: 10px;
    }
    .metric-card .value {
        font-size: 32px;
        font-weight: bold;
        color: #00d4ff;
    }
    .metric-card .label {
        font-size: 14px;
        color: #8899aa;
        margin-top: 5px;
    }

    /* Confidence bar */
    .conf-bar-outer {
        background: #1a2332;
        border-radius: 6px;
        height: 28px;
        width: 100%;
        overflow: hidden;
        margin: 4px 0;
    }
    .conf-bar-inner {
        height: 100%;
        border-radius: 6px;
        display: flex;
        align-items: center;
        padding-left: 8px;
        font-weight: bold;
        font-size: 13px;
        color: white;
        transition: width 0.8s ease-in-out;
    }

    /* File info panel */
    .file-info {
        background: #0f1724;
        border: 1px solid #1e3a5f;
        border-radius: 8px;
        padding: 16px;
        font-family: 'Courier New', monospace;
        color: #8899aa;
        font-size: 14px;
        line-height: 1.8;
    }

    /* Threat Intelligence Dossier Card */
    .intel-card {
        background: #101928;
        border: 1px solid #1e3a5f;
        border-radius: 8px;
        padding: 22px;
        margin-top: 15px;
        margin-bottom: 20px;
        color: #d0d8e5;
    }
    .intel-badge {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-left: 8px;
    }
    .intel-title {
        font-size: 22px;
        font-weight: bold;
        color: #ffffff;
    }
    .intel-section-title {
        font-size: 13px;
        font-weight: bold;
        color: #00d4ff;
        margin-top: 16px;
        margin-bottom: 6px;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    .intel-bullet {
        margin: 5px 0;
        font-size: 14px;
        line-height: 1.6;
        color: #b8c8dc;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ============================================================================
#  CACHED MODEL LOADING
# ============================================================================
@st.cache_resource(show_spinner=False)
def load_model():
    """Load the trained ResNet-18 model once and cache it."""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Build class label mapping
    idx_to_class = _get_class_labels()
    num_classes = len(idx_to_class)

    # Build model
    model = build_model(num_classes)

    checkpoint_path = os.path.join(MODEL_SAVE_DIR, "best_model.pth")
    if not os.path.isfile(checkpoint_path):
        st.error(f"Model checkpoint not found at `{checkpoint_path}`. Please train the model first.")
        st.stop()

    state_dict = torch.load(checkpoint_path, map_location=device, weights_only=True)
    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()

    return model, idx_to_class, device


def _get_class_labels():
    """Retrieve class labels from the dataset directory."""
    if os.path.isdir(IMAGE_OUTPUT_DIR):
        families = sorted([
            d for d in os.listdir(IMAGE_OUTPUT_DIR)
            if os.path.isdir(os.path.join(IMAGE_OUTPUT_DIR, d))
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


# ============================================================================
#  CORE ANALYSIS FUNCTIONS
# ============================================================================

def bytes_to_pil_image(file_bytes: bytes) -> Image.Image:
    """Convert raw file bytes to a grayscale PIL image (byteplot)."""
    byte_array = np.frombuffer(file_bytes, dtype=np.uint8)
    if byte_array.size == 0:
        return None

    import math
    file_size = byte_array.size
    width = get_image_width(file_size)
    height = math.ceil(file_size / width)

    padding_needed = (height * width) - file_size
    if padding_needed > 0:
        byte_array = np.pad(byte_array, (0, padding_needed), mode="constant", constant_values=0)

    image_array = byte_array.reshape((height, width))
    return Image.fromarray(image_array, mode="L")


def preprocess_for_model(pil_image: Image.Image) -> torch.Tensor:
    """Resize, normalize, and prepare a grayscale image for inference."""
    from torchvision import transforms
    transform = transforms.Compose([
        transforms.Resize(IMAGE_SIZE),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5], std=[0.5]),
    ])
    tensor = transform(pil_image.convert("L"))
    return tensor.unsqueeze(0)


def run_inference(model, input_tensor, device, idx_to_class, top_k=5):
    """Run forward pass and return prediction results."""
    input_tensor = input_tensor.to(device)
    with torch.no_grad():
        logits = model(input_tensor)
        probs = TF.softmax(logits, dim=1).squeeze(0).cpu().numpy()

    top_indices = np.argsort(probs)[::-1][:top_k]

    results = []
    for idx in top_indices:
        results.append({
            "family": idx_to_class[idx],
            "confidence": float(probs[idx]),
        })

    return results, probs


def generate_gradcam(model, input_tensor, device, target_class=None):
    """Generate Grad-CAM heatmap for the predicted class."""
    model.eval()
    model.zero_grad()

    # Register hooks on layer4 (final conv block of ResNet-18)
    activations = {}
    gradients = {}

    def fwd_hook(module, inp, out):
        activations["value"] = out.detach()

    def bwd_hook(module, grad_in, grad_out):
        gradients["value"] = grad_out[0].detach()

    handle_fwd = model.layer4.register_forward_hook(fwd_hook)
    handle_bwd = model.layer4.register_full_backward_hook(bwd_hook)

    input_tensor = input_tensor.to(device)
    input_tensor.requires_grad_(True)

    logits = model(input_tensor)
    if target_class is None:
        target_class = logits.argmax(dim=1).item()

    score = logits[0, target_class]
    score.backward()

    # Compute Grad-CAM
    pooled_gradients = torch.mean(gradients["value"], dim=[0, 2, 3])
    act = activations["value"][0]

    cam = torch.zeros(act.shape[1:], dtype=torch.float32)
    for i, w in enumerate(pooled_gradients):
        cam += w * act[i]

    cam = torch.relu(cam)
    cam_np = cam.cpu().numpy()
    if cam_np.max() > 0:
        cam_np = (cam_np - cam_np.min()) / (cam_np.max() - cam_np.min())
    else:
        cam_np = np.zeros_like(cam_np)

    handle_fwd.remove()
    handle_bwd.remove()

    return cam_np, target_class


def create_gradcam_figure(pil_img, cam_np, predicted_family, filename):
    """Create a 3-panel Grad-CAM visualization and return the figure."""
    vis_img = pil_img.resize(IMAGE_SIZE, Image.Resampling.BILINEAR)
    vis_arr = np.array(vis_img) / 255.0

    cam_pil = Image.fromarray(np.uint8(255 * cam_np)).resize(IMAGE_SIZE, Image.Resampling.BICUBIC)
    cam_resized = np.array(cam_pil) / 255.0

    try:
        jet = plt.colormaps["jet"]
    except AttributeError:
        jet = cm.get_cmap("jet")

    colored_heatmap = jet(cam_resized)[:, :, :3]

    vis_rgb = np.stack([vis_arr] * 3, axis=-1)
    overlay = 0.6 * vis_rgb + 0.4 * colored_heatmap
    overlay = np.clip(overlay, 0, 1)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5), facecolor="#0a0e17")

    for ax in axes:
        ax.set_facecolor("#0a0e17")

    axes[0].imshow(vis_arr, cmap="gray")
    axes[0].set_title(f"Original Byteplot\n{filename}", fontsize=11, color="white")
    axes[0].axis("off")

    axes[1].imshow(cam_resized, cmap="jet")
    axes[1].set_title("Grad-CAM Heatmap\n(Activation Intensity)", fontsize=11, color="white")
    axes[1].axis("off")

    axes[2].imshow(overlay)
    axes[2].set_title(f"Predicted: {predicted_family}\nKey Decision Regions", fontsize=11,
                      fontweight="bold", color="#00d4ff")
    axes[2].axis("off")

    plt.suptitle(f"CNN Interpretability via Grad-CAM: {filename}",
                 fontsize=14, fontweight="bold", color="#00d4ff")
    plt.tight_layout()

    return fig


def get_threat_level(confidence):
    """Return threat level string and CSS class based on confidence."""
    if confidence > 0.85:
        return "CRITICAL -- HIGH CONFIDENCE MATCH", "threat-critical"
    elif confidence > 0.60:
        return "SUSPICIOUS -- MEDIUM CONFIDENCE", "threat-suspicious"
    else:
        return "INCONCLUSIVE -- LOW CONFIDENCE (Possible Benign/Unseen)", "threat-low"


def format_file_size(size_bytes):
    """Format bytes into human-readable string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"


def render_malware_intel_card(family_name: str, confidence: float = 1.0):
    """
    Renders the threat intelligence dossier using multiple small st.markdown
    calls so that nested quotes and HTML entities never break Streamlit rendering.
    """
    intel = get_malware_intel(family_name)

    is_inconclusive = confidence < 0.60
    bc   = intel.get('badge_color', '#ff1744')
    left = '#00c853' if is_inconclusive else bc
    sev  = 'UNCERTAIN' if is_inconclusive else intel.get('severity', 'UNKNOWN')
    cat  = intel.get('category', 'Unknown')

    # ── card wrapper + header ────────────────────────────────────────────
    st.markdown(
        '<div class="intel-card" style="border-left:5px solid ' + left + ';">'
        '<div style="display:flex;justify-content:space-between;align-items:center;'
        'margin-bottom:12px;flex-wrap:wrap;gap:8px;">'
        '<div class="intel-title">' + SVG_SHIELD + 'Threat Profile: '
        '<span style="color:#00d4ff;">' + family_name + '</span></div>'
        '<div>'
        '<span class="intel-badge" style="background:#1e3a5f;color:#00d4ff;">' + cat + '</span> '
        '<span class="intel-badge" style="background:' + bc + ';color:#fff;">' + sev + ' RISK</span>'
        '</div></div>',
        unsafe_allow_html=True
    )

    # ── low-confidence note ──────────────────────────────────────────────
    if is_inconclusive:
        st.markdown(
            '<div style="background:rgba(0,200,83,0.12);border:1px solid #00c853;'
            'border-radius:6px;padding:12px;margin-bottom:15px;font-size:13px;color:#80f0a8;">'
            '<strong>Low Confidence Note:</strong> The sample weakly correlates with '
            '<code>' + family_name + '</code> (' + f'{confidence:.1%}' + '), '
            'which is below the malicious threshold. '
            'This file is likely a benign Windows executable rather than active malware.'
            '</div>',
            unsafe_allow_html=True
        )

    # ── what it does ─────────────────────────────────────────────────────
    st.markdown(
        '<div class="intel-section-title">' + SVG_TARGET + 'What It Does</div>'
        '<p style="font-size:14px;line-height:1.7;color:#c0d0e5;margin-bottom:14px;">'
        + intel['what_it_does'] +
        '</p>',
        unsafe_allow_html=True
    )

    # ── how computers are affected ───────────────────────────────────────
    bullets = ''.join(
        '<li style="margin:6px 0;font-size:14px;line-height:1.6;color:#b8c8dc;">' + pt + '</li>'
        for pt in intel['how_computers_affected']
    )
    st.markdown(
        '<div class="intel-section-title">' + SVG_ACTIVITY + 'How Computers Are Affected</div>'
        '<ul style="margin:0;padding-left:22px;margin-bottom:16px;">' + bullets + '</ul>',
        unsafe_allow_html=True
    )

    # ── infection vector ─────────────────────────────────────────────────
    st.markdown(
        '<div class="intel-section-title">' + SVG_NETWORK + 'Infection Vector &amp; Propagation</div>'
        '<p style="font-size:13px;line-height:1.5;color:#a5b8ce;margin-bottom:14px;">'
        + intel['infection_vector'] +
        '</p>',
        unsafe_allow_html=True
    )

    # ── remediation + close card ─────────────────────────────────────────
    st.markdown(
        '<div class="intel-section-title">' + SVG_CHECK + 'Recommended Remediation</div>'
        '<p style="font-size:13px;line-height:1.5;color:#a5b8ce;margin:0;">'
        + intel['remediation'] +
        '</p></div>',
        unsafe_allow_html=True
    )

# ============================================================================
#  SIDEBAR
# ============================================================================
def render_sidebar():
    """Render sidebar with app info and settings."""
    st.sidebar.markdown("""
    <div style="text-align: center; padding: 14px 0 8px;">
        <div style="display: inline-block; padding: 10px; border-radius: 12px; background: rgba(0, 212, 255, 0.06); border: 1px solid rgba(0, 212, 255, 0.2);">
            <svg width="42" height="42" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L3 6V11C3 16.55 6.84 21.74 12 23C17.16 21.74 21 16.55 21 11V6L12 2Z" fill="#0d1a29" stroke="#00d4ff" stroke-width="1.8" stroke-linejoin="round"/>
                <path d="M9 12L11 14L15 10" stroke="#00d4ff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        </div>
        <div style="color: #ffffff; font-size: 18px; font-weight: 800; letter-spacing: 1.5px; margin-top: 8px;">MALVISION</div>
        <div style="color: #6688aa; font-size: 11px; letter-spacing: 0.8px; text-transform: uppercase;">Threat Intelligence Platform</div>
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.divider()

    st.sidebar.markdown("### Analysis Settings")
    top_k = st.sidebar.slider("Top-K Predictions", min_value=3, max_value=26, value=5)

    st.sidebar.divider()

    st.sidebar.markdown("### Model Info")
    st.sidebar.markdown("""
    <div class="file-info">
    Architecture: ResNet-18<br>
    Input: 224x224 grayscale<br>
    Families: 26 malware classes<br>
    Test Accuracy: 97.86%<br>
    Dataset: Malimg (9,339 samples)
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.divider()

    st.sidebar.markdown("### Supported Formats")
    st.sidebar.markdown("""
    - `.exe` - Windows Executables
    - `.dll` - Dynamic Link Libraries
    - `.bin` - Raw Binary Dumps
    - `.png / .jpg` - Pre-converted Images
    """)

    return top_k


# ============================================================================
#  MAIN UI
# ============================================================================
def main():
    top_k = render_sidebar()

    # -- Header
    st.markdown("""
    <div style="text-align: center; padding: 18px 0 12px;">
        <div style="display: inline-flex; align-items: center; justify-content: center; gap: 12px;">
            <svg width="36" height="36" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L3 6V11C3 16.55 6.84 21.74 12 23C17.16 21.74 21 16.55 21 11V6L12 2Z" fill="#0e1b2d" stroke="#00d4ff" stroke-width="2" stroke-linejoin="round"/>
                <path d="M9 12L11 14L15 10" stroke="#00d4ff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span style="font-size: 34px; font-weight: 800; letter-spacing: 1px; color: #00d4ff;">MALVISION THREAT HUNTER</span>
        </div>
        <p style="color: #7b8e9f; font-size: 14px; margin-top: 6px; letter-spacing: 0.3px;">
            Deep Learning Binary-to-Texture Malware Classification &amp; Explainability Engine
        </p>
    </div>
    """, unsafe_allow_html=True)

    # -- Load model (cached)
    with st.spinner("Loading trained ResNet-18 model..."):
        model, idx_to_class, device = load_model()

    # -- Tabs
    tab_analyze, tab_batch, tab_gallery = st.tabs([
        "Single File Analysis",
        "Batch Analysis",
        "Malimg Gallery"
    ])

    # ========================================================================
    #  TAB 1: SINGLE FILE ANALYSIS
    # ========================================================================
    with tab_analyze:
        st.markdown("### Upload a Suspicious File")

        uploaded_file = st.file_uploader(
            "Drag and drop a file here, or click to browse",
            type=["exe", "dll", "bin", "png", "jpg", "jpeg", "bmp", "sys", "scr", "dat"],
            help="Supports raw binaries (.exe, .dll, .bin) and pre-converted images (.png, .jpg)",
            key="single_upload"
        )

        if uploaded_file is not None:
            file_bytes = uploaded_file.read()
            file_name = uploaded_file.name
            file_ext = os.path.splitext(file_name)[1].lower()
            file_size = len(file_bytes)

            # -- Convert file to image in memory (for classification & optional viewing)
            if file_ext in [".png", ".jpg", ".jpeg", ".bmp"]:
                pil_img = Image.open(io.BytesIO(file_bytes)).convert("L")
            else:
                pil_img = bytes_to_pil_image(file_bytes)

            if pil_img is None:
                st.error("Failed to convert file to image. The file may be empty.")
                return

            # -- File Info Panel (Clean 2-column layout)
            st.markdown("#### File Properties")
            col_info1, col_info2 = st.columns(2)

            with col_info1:
                st.markdown(f"""
                <div class="file-info">
                    <strong>Filename:</strong> {file_name}<br>
                    <strong>Size:</strong> {format_file_size(file_size)} ({file_size:,} bytes)<br>
                    <strong>Type:</strong> {file_ext.upper() if file_ext else "RAW BINARY"}<br>
                    <strong>Heuristic Width:</strong> {get_image_width(file_size)} px
                </div>
                """, unsafe_allow_html=True)

            with col_info2:
                st.markdown(f"""
                <div class="file-info">
                    <strong>Byteplot Dimensions:</strong> {pil_img.width} &times; {pil_img.height} px<br>
                    <strong>Color Space:</strong> 8-bit Grayscale (0–255)<br>
                    <strong>SHA-256:</strong> <span style="font-size: 11px; word-break: break-all;">{_compute_hash(file_bytes)}</span>
                </div>
                """, unsafe_allow_html=True)

            # -- Option to view Byteplot on click
            with st.expander("View 2D Grayscale Byteplot (Spatial Texture)", expanded=False):
                st.markdown("#### 2D Grayscale Byteplot")
                st.image(
                    pil_img,
                    caption=f"Byteplot of {file_name} ({pil_img.width} \u00d7 {pil_img.height} px)",
                    use_container_width=True
                )

            st.divider()

            # -- Run Classification
            st.markdown("### Classification Results")

            with st.spinner("Running inference through ResNet-18..."):
                input_tensor = preprocess_for_model(pil_img)
                results, all_probs = run_inference(model, input_tensor, device, idx_to_class, top_k)

            top_family = results[0]["family"]
            top_conf = results[0]["confidence"]

            # -- Threat Level Banner
            threat_text, threat_css = get_threat_level(top_conf)
            st.markdown(f'<div class="{threat_css}">{threat_text}</div>', unsafe_allow_html=True)
            st.markdown("")

            # -- Metric Cards
            col_m1, col_m2, col_m3 = st.columns(3)

            with col_m1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="value">{top_family}</div>
                    <div class="label">Primary Classification</div>
                </div>
                """, unsafe_allow_html=True)

            with col_m2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="value">{top_conf:.1%}</div>
                    <div class="label">Confidence Score</div>
                </div>
                """, unsafe_allow_html=True)

            with col_m3:
                entropy = -np.sum(all_probs * np.log(all_probs + 1e-10))
                st.markdown(f"""
                <div class="metric-card">
                    <div class="value">{entropy:.3f}</div>
                    <div class="label">Prediction Entropy (lower = more certain)</div>
                </div>
                """, unsafe_allow_html=True)

            # -- Top-K Confidence Bars
            st.markdown(f"#### Top-{top_k} Predicted Families")

            for i, result in enumerate(results):
                conf = result["confidence"]
                family = result["family"]
                pct = conf * 100

                if conf > 0.85:
                    bar_color = "#ff1744"
                elif conf > 0.60:
                    bar_color = "#ff9100"
                elif conf > 0.30:
                    bar_color = "#ffea00"
                else:
                    bar_color = "#00c853"

                rank_num = f"{i+1:02d}"

                st.markdown(f"""
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <span style="width: 32px; height: 26px; display: inline-flex; align-items: center; justify-content: center; border-radius: 4px; background: #132030; border: 1px solid #1f3750; color: #00d4ff; font-family: monospace; font-size: 11px; font-weight: bold; margin-right: 12px;">{rank_num}</span>
                    <span style="width: 180px; color: #ccd; font-weight: bold; font-size: 14px;">{family}</span>
                    <div class="conf-bar-outer" style="flex: 1;">
                        <div class="conf-bar-inner" style="width: {max(pct, 2):.1f}%; background: {bar_color};">
                            {pct:.2f}%
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # -- Threat Intelligence Dossier
            st.markdown("### Threat Intelligence Dossier")
            render_malware_intel_card(top_family, top_conf)

            st.divider()

            # -- Grad-CAM Section
            st.markdown("### Grad-CAM Explainability")
            st.markdown("*Visualize which byte regions triggered the classification decision.*")

            if st.button("Generate Grad-CAM Heatmap", type="primary", use_container_width=True):
                with st.spinner("Computing gradient-weighted class activations..."):
                    input_tensor_grad = preprocess_for_model(pil_img)
                    cam_np, target_class = generate_gradcam(model, input_tensor_grad, device)
                    predicted_family = idx_to_class.get(target_class, f"Class {target_class}")
                    fig = create_gradcam_figure(pil_img, cam_np, predicted_family, file_name)

                st.pyplot(fig, use_container_width=True)
                plt.close(fig)

                st.success(f"Grad-CAM shows regions that most influenced the '{predicted_family}' classification.")

    # ========================================================================
    #  TAB 2: BATCH ANALYSIS
    # ========================================================================
    with tab_batch:
        st.markdown("### Batch File Analysis")
        st.markdown("Upload multiple files to analyze them all at once.")

        batch_files = st.file_uploader(
            "Upload multiple files",
            type=["exe", "dll", "bin", "png", "jpg", "jpeg", "bmp", "sys", "scr", "dat"],
            accept_multiple_files=True,
            key="batch_upload"
        )

        if batch_files:
            st.markdown(f"**{len(batch_files)} files uploaded.** Running batch analysis...")

            progress_bar = st.progress(0)
            batch_results = []

            for i, bf in enumerate(batch_files):
                file_bytes = bf.read()
                file_name = bf.name
                file_ext = os.path.splitext(file_name)[1].lower()

                if file_ext in [".png", ".jpg", ".jpeg", ".bmp"]:
                    pil_img = Image.open(io.BytesIO(file_bytes)).convert("L")
                else:
                    pil_img = bytes_to_pil_image(file_bytes)

                if pil_img is not None:
                    input_tensor = preprocess_for_model(pil_img)
                    results, _ = run_inference(model, input_tensor, device, idx_to_class, top_k=1)
                    top = results[0]
                    threat_text, _ = get_threat_level(top["confidence"])

                    batch_results.append({
                        "File": file_name,
                        "Size": format_file_size(len(file_bytes)),
                        "Predicted Family": top["family"],
                        "Confidence": f"{top['confidence']:.2%}",
                        "Threat Level": threat_text.split(" -- ")[0],
                    })

                progress_bar.progress((i + 1) / len(batch_files))

            if batch_results:
                st.markdown("#### Results Summary")
                st.dataframe(batch_results, use_container_width=True)

                # Summary stats
                critical_count = sum(1 for r in batch_results if r["Threat Level"] == "CRITICAL")
                suspicious_count = sum(1 for r in batch_results if r["Threat Level"] == "SUSPICIOUS")
                low_count = sum(1 for r in batch_results if r["Threat Level"] == "INCONCLUSIVE")

                col1, col2, col3 = st.columns(3)
                col1.metric("Critical", critical_count)
                col2.metric("Suspicious", suspicious_count)
                col3.metric("Inconclusive", low_count)

    # ========================================================================
    #  TAB 3: MALIMG GALLERY
    # ========================================================================
    with tab_gallery:
        st.markdown("### Malimg Dataset Gallery")
        st.markdown("Browse sample byteplots from the training dataset.")

        if os.path.isdir(IMAGE_OUTPUT_DIR):
            families = sorted([
                d for d in os.listdir(IMAGE_OUTPUT_DIR)
                if os.path.isdir(os.path.join(IMAGE_OUTPUT_DIR, d))
            ])

            if families:
                selected_family = st.selectbox(
                    "Select Malware Family",
                    families,
                    index=0
                )

                family_dir = os.path.join(IMAGE_OUTPUT_DIR, selected_family)
                samples = sorted([
                    f for f in os.listdir(family_dir)
                    if f.lower().endswith((".png", ".jpg", ".jpeg"))
                ])

                family_count = len(samples)
                st.markdown(f"**{selected_family}** - {family_count} samples in dataset")

                with st.expander(f"Threat Dossier: {selected_family}", expanded=False):
                    render_malware_intel_card(selected_family, confidence=1.0)

                # Show grid of samples
                num_show = min(12, family_count)
                cols = st.columns(4)

                for j in range(num_show):
                    sample_path = os.path.join(family_dir, samples[j])
                    with cols[j % 4]:
                        img = Image.open(sample_path).convert("L")
                        st.image(img, caption=samples[j][:20], use_container_width=True)

                # Option to classify a gallery sample
                if samples:
                    st.divider()
                    selected_sample = st.selectbox("Pick a sample to classify", samples[:50])
                    if st.button("Classify Selected Sample", type="primary"):
                        sample_path = os.path.join(family_dir, selected_sample)
                        pil_img = Image.open(sample_path).convert("L")
                        input_tensor = preprocess_for_model(pil_img)
                        results, _ = run_inference(model, input_tensor, device, idx_to_class, top_k)

                        for r in results:
                            conf = r["confidence"]
                            bar_color = "#ff1744" if conf > 0.85 else "#ff9100" if conf > 0.6 else "#00c853"
                            st.markdown(f"""
                            <div style="display: flex; align-items: center; margin-bottom: 6px;">
                                <span style="width: 180px; color: #ccd; font-weight: bold;">{r['family']}</span>
                                <div class="conf-bar-outer" style="flex: 1;">
                                    <div class="conf-bar-inner" style="width: {max(conf*100, 2):.1f}%; background: {bar_color};">
                                        {conf:.2%}
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
            else:
                st.info("No families found in the dataset directory.")
        else:
            st.warning(f"Dataset directory not found: `{IMAGE_OUTPUT_DIR}`")


def _compute_hash(file_bytes: bytes) -> str:
    """Compute SHA-256 hash of file bytes."""
    import hashlib
    return hashlib.sha256(file_bytes).hexdigest()


if __name__ == "__main__":
    main()
