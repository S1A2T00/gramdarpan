"""
generate_sample_data.py
------------------------
GramDarpan - Image Analysis Module

Since real satellite/drone imagery isn't available offline, this script
generates synthetic multispectral sample images (RGB + a simulated NIR
band) that mimic a village scene: agriculture fields, a water body, and
bare/built-up land. This lets the image-analysis pipeline (NDVI, NDWI,
change detection) be demonstrated end-to-end without external data.

Replace these generated images with real satellite band exports
(Sentinel-2, Bhuvan, drone orthomosaics, etc.) when available — the
analysis modules only expect standard RGB + NIR numpy arrays / images,
so the source doesn't matter.

Output:
    sample_images/village_t1_rgb.png   - RGB image, Time 1 (e.g. June)
    sample_images/village_t1_nir.png   - Simulated NIR band, Time 1
    sample_images/village_t2_rgb.png   - RGB image, Time 2 (e.g. August)
    sample_images/village_t2_nir.png   - Simulated NIR band, Time 2
"""

import numpy as np
from PIL import Image
import os

OUT_DIR = os.path.join(os.path.dirname(__file__), "sample_images")
os.makedirs(OUT_DIR, exist_ok=True)

H, W = 400, 400


def make_scene(seed, veg_strength=1.0, water_level=1.0):
    """
    Builds a synthetic village scene with 3 zones:
      - Top-left: agriculture field (vegetation)
      - Bottom-right: water body (pond)
      - Rest: bare soil / built-up land

    veg_strength: multiplier controlling vegetation vigor (NIR reflectance)
    water_level:  multiplier controlling water body extent
    """
    rng = np.random.default_rng(seed)

    red = np.full((H, W), 90, dtype=np.float32)
    green = np.full((H, W), 95, dtype=np.float32)
    blue = np.full((H, W), 80, dtype=np.float32)
    nir = np.full((H, W), 100, dtype=np.float32)

    # --- Agriculture field zone (healthy vegetation reflects strongly in NIR, less in Red) ---
    yy, xx = np.mgrid[0:H, 0:W]
    field_mask = (xx < 220) & (yy < 260) & (xx > 20) & (yy > 20)
    veg_noise = rng.normal(0, 8, size=(H, W))

    red[field_mask] = 60 + veg_noise[field_mask] * 0.3
    green[field_mask] = 110 + veg_noise[field_mask] * 0.3
    blue[field_mask] = 50
    nir[field_mask] = np.clip(180 * veg_strength + veg_noise[field_mask], 40, 255)

    # --- Water body zone (low NIR reflectance, higher green/blue) ---
    cy, cx, base_r = 300, 300, 70
    r = int(base_r * water_level)
    water_mask = (xx - cx) ** 2 + (yy - cy) ** 2 <= r ** 2
    red[water_mask] = 30
    green[water_mask] = 60
    blue[water_mask] = 120
    nir[water_mask] = 15

    # --- Bare soil / built-up background noise ---
    bg_mask = ~field_mask & ~water_mask
    soil_noise = rng.normal(0, 5, size=(H, W))
    red[bg_mask] = np.clip(120 + soil_noise[bg_mask], 60, 200)
    green[bg_mask] = np.clip(105 + soil_noise[bg_mask], 60, 200)
    blue[bg_mask] = np.clip(85 + soil_noise[bg_mask], 50, 180)
    nir[bg_mask] = np.clip(90 + soil_noise[bg_mask], 40, 180)

    rgb = np.stack([red, green, blue], axis=-1).astype(np.uint8)
    nir_img = nir.astype(np.uint8)
    return rgb, nir_img


def save(arr, path, mode=None):
    Image.fromarray(arr, mode=mode).save(path)


if __name__ == "__main__":
    # Time 1: healthy season, water at normal level
    rgb1, nir1 = make_scene(seed=1, veg_strength=1.0, water_level=1.0)
    save(rgb1, os.path.join(OUT_DIR, "village_t1_rgb.png"))
    save(nir1, os.path.join(OUT_DIR, "village_t1_nir.png"), mode="L")

    # Time 2: simulate crop stress (lower NIR reflectance) + shrinking water body
    rgb2, nir2 = make_scene(seed=2, veg_strength=0.55, water_level=0.6)
    save(rgb2, os.path.join(OUT_DIR, "village_t2_rgb.png"))
    save(nir2, os.path.join(OUT_DIR, "village_t2_nir.png"), mode="L")

    print("Sample multispectral images generated in:", OUT_DIR)
    print(" - village_t1_rgb.png / village_t1_nir.png   (Time 1)")
    print(" - village_t2_rgb.png / village_t2_nir.png   (Time 2)")
