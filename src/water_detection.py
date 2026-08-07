"""
src/water_detection.py
------------------------
GramDarpan - Image Analysis Module: Water Resource Agent

Computes NDWI (Normalized Difference Water Index) from Green + NIR bands
to detect and quantify water body extent (ponds, canals, reservoirs).

    NDWI = (Green - NIR) / (Green + NIR)

NDWI > 0.2 is typically classified as water. This is the standard
remote-sensing technique (McFeeters, 1996) used for satellite-based
water body mapping and level monitoring.

Usage:
    from src.water_detection import analyze_water
    result = analyze_water(rgb_path, nir_path, out_dir)
"""

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import os
import json

WATER_THRESHOLD = 0.2


def _load_band(path, as_gray=False):
    img = Image.open(path)
    if as_gray:
        img = img.convert("L")
    return np.array(img).astype(np.float32)


def compute_ndwi(green_band, nir_band):
    denom = (green_band + nir_band)
    denom[denom == 0] = 1e-6
    ndwi = (green_band - nir_band) / denom
    return np.clip(ndwi, -1, 1)


def analyze_water(rgb_path, nir_path, out_dir, label="scene"):
    """
    Full water-body detection pipeline:
      1. Load RGB (for Green band) + NIR band images
      2. Compute NDWI raster
      3. Threshold to get a binary water mask
      4. Estimate water body area (% of frame)
      5. Save visualization
      6. Return structured report
    """
    os.makedirs(out_dir, exist_ok=True)

    rgb = _load_band(rgb_path)
    green_band = rgb[:, :, 1]
    nir_band = _load_band(nir_path, as_gray=True)

    ndwi = compute_ndwi(green_band, nir_band)
    water_mask = ndwi > WATER_THRESHOLD
    water_pixels = int(np.sum(water_mask))
    total_pixels = ndwi.size
    water_percent = round(100 * water_pixels / total_pixels, 2)

    status = "Normal"
    if water_percent < 2:
        status = "Critical - Very Low / Dried"
    elif water_percent < 4:
        status = "Low - Alert"

    heatmap_path = os.path.join(out_dir, f"{label}_ndwi_mask.png")
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    axes[0].imshow(ndwi, cmap="Blues", vmin=-1, vmax=1)
    axes[0].set_title(f"NDWI Index — {label}")
    axes[0].axis("off")

    axes[1].imshow(water_mask, cmap="Blues")
    axes[1].set_title(f"Detected Water Mask\n{water_percent}% of frame | {status}")
    axes[1].axis("off")

    plt.tight_layout()
    plt.savefig(heatmap_path, dpi=130)
    plt.close()

    report = {
        "label": label,
        "water_area_percent": water_percent,
        "status": status,
        "mask_path": heatmap_path
    }
    return report


if __name__ == "__main__":
    base = os.path.dirname(os.path.dirname(__file__))
    rgb_path = os.path.join(base, "sample_images", "village_t1_rgb.png")
    nir_path = os.path.join(base, "sample_images", "village_t1_nir.png")
    out_dir = os.path.join(base, "output")

    report = analyze_water(rgb_path, nir_path, out_dir, label="village_t1")
    print(json.dumps(report, indent=2))
