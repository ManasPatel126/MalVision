"""
convert_real_binaries.py — Test Binary-to-Image Conversion on Real Windows Executables

This script gathers actual compiled Portable Executable (PE) binaries from the system
into categories (representing distinct functional 'families'), runs the Nataraj et al.
binary-to-image conversion, and saves the resulting grayscale images.

Categories sampled:
    - sys_internals: Core OS commands (cmd, reg, tasklist, whoami, etc.)
    - archivers: Compression and file packaging tools (tar, compact, makecab, etc.)
    - network_diag: Network diagnostic utilities (ping, tracert, ipconfig, netstat, etc.)
    - utilities: System management utilities (cipher, certutil, robocopy, etc.)
"""

import os
import shutil
from binary_to_image import binary_to_grayscale_array, save_image, get_image_width

REAL_BINARIES_DIR = os.path.join("data", "real_raw_binaries")
REAL_IMAGES_DIR = os.path.join("outputs", "real_binary_visualizations")

# Groups of actual Windows executables with their system paths
SAMPLE_FAMILIES = {
    "sys_internals": [
        r"C:\Windows\System32\cmd.exe",
        r"C:\Windows\System32\reg.exe",
        r"C:\Windows\System32\tasklist.exe",
        r"C:\Windows\System32\whoami.exe",
        r"C:\Windows\System32\systeminfo.exe",
    ],
    "archivers": [
        r"C:\Windows\System32\tar.exe",
        r"C:\Windows\System32\compact.exe",
        r"C:\Windows\System32\expand.exe",
        r"C:\Windows\System32\makecab.exe",
        r"C:\Windows\System32\extrac32.exe",
    ],
    "network_diag": [
        r"C:\Windows\System32\ping.exe",
        r"C:\Windows\System32\tracert.exe",
        r"C:\Windows\System32\ipconfig.exe",
        r"C:\Windows\System32\netstat.exe",
        r"C:\Windows\System32\nslookup.exe",
    ],
    "utilities": [
        r"C:\Windows\System32\cipher.exe",
        r"C:\Windows\System32\certutil.exe",
        r"C:\Windows\System32\robocopy.exe",
        r"C:\Windows\System32\findstr.exe",
        r"C:\Windows\System32\fc.exe",
    ],
}


def run_conversion():
    print("=" * 70)
    print("  Converting Real Executable Binaries to Grayscale Texture Images")
    print("=" * 70)

    for family, paths in SAMPLE_FAMILIES.items():
        family_bin_dir = os.path.join(REAL_BINARIES_DIR, family)
        family_img_dir = os.path.join(REAL_IMAGES_DIR, family)
        os.makedirs(family_bin_dir, exist_ok=True)
        os.makedirs(family_img_dir, exist_ok=True)

        print(f"\n[Family: {family}]")
        print(f"  {'Filename':<18} | {'File Size':>12} | {'Width':>6} | {'Height':>6} | {'Status'}")
        print("  " + "-" * 62)

        for src_path in paths:
            if not os.path.isfile(src_path):
                continue

            fname = os.path.basename(src_path)
            # Copy raw binary to real_raw_binaries folder
            dest_bin = os.path.join(family_bin_dir, fname)
            if not os.path.exists(dest_bin):
                shutil.copy2(src_path, dest_bin)

            size = os.path.getsize(src_path)
            width = get_image_width(size)

            # Convert using Module 1
            arr = binary_to_grayscale_array(dest_bin)
            if arr is not None:
                png_name = os.path.splitext(fname)[0] + ".png"
                out_png = os.path.join(family_img_dir, png_name)
                save_image(arr, out_png)
                print(f"  {fname:<18} | {size:>10,} B | {width:>6d} | {arr.shape[0]:>6d} | OK -> {png_name}")
            else:
                print(f"  {fname:<18} | {size:>10,} B | {width:>6d} |  FAILED")

    print("\n" + "=" * 70)
    print(f"  [DONE] Converted images saved to: {REAL_IMAGES_DIR}")
    print("=" * 70)


if __name__ == "__main__":
    run_conversion()
