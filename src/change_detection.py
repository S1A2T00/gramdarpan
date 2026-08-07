"""
src/change_detection.py
--------------------------
GramDarpan - Image Analysis Module: Change Detection Agent

Compares two satellite/drone images of the same village captured at
different times (e.g. two crop seasons, before/after monsoon) to
detect meaningful change in vegetation cover and water extent —
useful for spotting crop stress trends, water depletion, encroachment,
or new construction over time.

Approach:
    1. Compute NDVI and NDWI independently for time T1 and T2
       (using vegetation_analysis.py and water_detection.py)
    2. Difference the rasters: delta = index_T2 - index_T1
    3. Flag pixels/zones with significant negative change as risk areas

Usage:
    from src.change_detection import detect_change
    result = detect_change(t1_rgb, t1_nir, t2_rgb, t2_nir, out_dir)
"""

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import os
import json

from src.vegetation_analysis import compute_ndvi, _load_band as _load_veg_band
from src.water_detection import compute_ndwi

SIGNIFICANT_DROP = -0.15  # NDVI/NDWI drop considered significant


def detect_change(t1_rgb_path, t1_nir_path, t2_rgb_path, t2_nir_path, out_dir,
                   label="village"):
    os.makedirs(out_dir, exist_ok=True)

    rgb1 = _load_veg_band(t1_rgb_path)
    nir1 = _load_veg_band(t1_nir_path, as_gray=True)
    rgb2 = _load_veg_band(t2_rgb_path)
    nir2 = _load_veg_band(t2_nir_path, as_gray=True)

    ndvi1 = compute_ndvi(rgb1[:, :, 0], nir1)
    ndvi2 = compute_ndvi(rgb2[:, :, 0], nir2)
    ndvi_delta = ndvi2 - ndvi1

    ndwi1 = compute_ndwi(rgb1[:, :, 1], nir1)
    ndwi2 = compute_ndwi(rgb2[:, :, 1], nir2)
    ndwi_delta = ndwi2 - ndwi1

    veg_loss_mask = ndvi_delta < SIGNIFICANT_DROP
    water_loss_mask = ndwi_delta < SIGNIFICANT_DROP

    veg_loss_percent = round(100 * np.sum(veg_loss_mask) / ndvi_delta.size, 2)
    water_loss_percent = round(100 * np.sum(water_loss_mask) / ndwi_delta.size, 2)

    # Visualization
    change_path = os.path.join(out_dir, f"{label}_change_detection.png")
    fig, axes = plt.subplots(1, 2, figsize=(11, 5))

    im0 = axes[0].imshow(ndvi_delta, cmap="RdYlGn", vmin=-0.5, vmax=0.5)
    axes[0].set_title(f"Vegetation Change (NDVI Δ)\n{veg_loss_percent}% area with significant decline")
    axes[0].axis("off")
    plt.colorbar(im0, ax=axes[0], fraction=0.046)

    im1 = axes[1].imshow(ndwi_delta, cmap="RdBu", vmin=-0.5, vmax=0.5)
    axes[1].set_title(f"Water Extent Change (NDWI Δ)\n{water_loss_percent}% area with significant decline")
    axes[1].axis("off")
    plt.colorbar(im1, ax=axes[1], fraction=0.046)

    plt.tight_layout()
    plt.savefig(change_path, dpi=130)
    plt.close()

    alerts = []
    if veg_loss_percent > 5:
        alerts.append({
            "type": "Vegetation Decline",
            "severity": "High" if veg_loss_percent > 15 else "Medium",
            "message": f"{veg_loss_percent}% of monitored agriculture area shows significant "
                       f"vegetation decline between the two time periods. Possible crop stress, "
                       f"pest attack, or irrigation shortage — recommend field verification."
        })
    if water_loss_percent > 5:
        alerts.append({
            "type": "Water Body Shrinkage",
            "severity": "High" if water_loss_percent > 15 else "Medium",
            "message": f"{water_loss_percent}% reduction detected in water body extent. "
                       f"Possible drought stress or over-extraction — recommend water resource review."
        })
    if not alerts:
        alerts.append({
            "type": "No Significant Change",
            "severity": "Low",
            "message": "No major vegetation or water extent decline detected between the two periods."
        })

    report = {
        "label": label,
        "vegetation_loss_percent": veg_loss_percent,
        "water_loss_percent": water_loss_percent,
        "change_map_path": change_path,
        "alerts": alerts
    }
    return report


if __name__ == "__main__":
    base = os.path.dirname(os.path.dirname(__file__))
    imgs = os.path.join(base, "sample_images")
    out_dir = os.path.join(base, "output")

    report = detect_change(
        os.path.join(imgs, "village_t1_rgb.png"),
        os.path.join(imgs, "village_t1_nir.png"),
        os.path.join(imgs, "village_t2_rgb.png"),
        os.path.join(imgs, "village_t2_nir.png"),
        out_dir,
        label="village"
    )
    print(json.dumps(report, indent=2))
