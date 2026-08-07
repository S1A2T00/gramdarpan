"""
src/vegetation_analysis.py
----------------------------
GramDarpan - Image Analysis Module: Agriculture / Vegetation Agent

Computes NDVI (Normalized Difference Vegetation Index) from Red + NIR
bands to assess crop / vegetation health across a village's agriculture
zones — the core remote-sensing technique used in real satellite-based
crop monitoring (Sentinel-2, Landsat, drone multispectral cameras).

    NDVI = (NIR - Red) / (NIR + Red)

NDVI ranges from -1 to 1:
    < 0.1         -> bare soil / water / no vegetation
    0.1 - 0.3     -> sparse / stressed vegetation
    0.3 - 0.6     -> moderate vegetation health
    > 0.6         -> dense, healthy vegetation

Usage:
    from src.vegetation_analysis import analyze_vegetation
    result = analyze_vegetation(rgb_path, nir_path, out_dir)
"""

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import os
import json


def _load_band(path, as_gray=False):
    img = Image.open(path)
    if as_gray:
        img = img.convert("L")
    return np.array(img).astype(np.float32)


def compute_ndvi(red_band, nir_band):
    """Compute NDVI array, safely handling division by zero."""
    denom = (nir_band + red_band)
    denom[denom == 0] = 1e-6
    ndvi = (nir_band - red_band) / denom
    return np.clip(ndvi, -1, 1)


def classify_health(ndvi_value):
    if ndvi_value < 0.1:
        return "No Vegetation / Bare"
    elif ndvi_value < 0.3:
        return "Poor"
    elif ndvi_value < 0.6:
        return "Moderate"
    else:
        return "Good"


def analyze_vegetation(rgb_path, nir_path, out_dir, label="scene"):
    """
    Full vegetation analysis pipeline:
      1. Load RGB (for Red band) + NIR band images
      2. Compute NDVI raster
      3. Classify overall + zonal health
      4. Save an NDVI heatmap image
      5. Return a structured JSON-able report

    Returns dict:
        {
          "label": ...,
          "mean_ndvi": float,
          "health_status": str,
          "vegetation_pixel_percent": float,
          "heatmap_path": str
        }
    """
    os.makedirs(out_dir, exist_ok=True)

    rgb = _load_band(rgb_path)
    red_band = rgb[:, :, 0]
    nir_band = _load_band(nir_path, as_gray=True)

    ndvi = compute_ndvi(red_band, nir_band)
    mean_ndvi = float(np.mean(ndvi))
    veg_pixels = np.sum(ndvi > 0.3)
    total_pixels = ndvi.size
    veg_percent = round(100 * veg_pixels / total_pixels, 2)

    # Save NDVI heatmap visualization
    heatmap_path = os.path.join(out_dir, f"{label}_ndvi_heatmap.png")
    cmap = mcolors.LinearSegmentedColormap.from_list(
        "ndvi_cmap", ["#8B4513", "#D2B48C", "#FFFF66", "#7CFC00", "#006400"]
    )
    plt.figure(figsize=(6, 6))
    plt.imshow(ndvi, cmap=cmap, vmin=-1, vmax=1)
    plt.colorbar(label="NDVI")
    plt.title(f"Vegetation Health (NDVI) — {label}\nMean NDVI: {mean_ndvi:.3f} | Status: {classify_health(mean_ndvi)}")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(heatmap_path, dpi=130)
    plt.close()

    # Zonal stats split into a 4x4 grid of plots to simulate multiple field parcels
    zones = []
    gh, gw = ndvi.shape[0] // 4, ndvi.shape[1] // 4
    for i in range(4):
        for j in range(4):
            block = ndvi[i * gh:(i + 1) * gh, j * gw:(j + 1) * gw]
            z_mean = float(np.mean(block))
            zones.append({
                "zone_id": f"Z-{i}{j}",
                "mean_ndvi": round(z_mean, 3),
                "health_status": classify_health(z_mean)
            })

    report = {
        "label": label,
        "mean_ndvi": round(mean_ndvi, 3),
        "health_status": classify_health(mean_ndvi),
        "vegetation_pixel_percent": veg_percent,
        "heatmap_path": heatmap_path,
        "zones": zones
    }
    return report


if __name__ == "__main__":
    base = os.path.dirname(os.path.dirname(__file__))
    rgb_path = os.path.join(base, "sample_images", "village_t1_rgb.png")
    nir_path = os.path.join(base, "sample_images", "village_t1_nir.png")
    out_dir = os.path.join(base, "output")

    report = analyze_vegetation(rgb_path, nir_path, out_dir, label="village_t1")
    print(json.dumps(report, indent=2))
