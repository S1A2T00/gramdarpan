"""
main.py
--------
GramDarpan - Image Analysis Module: Full Pipeline

Runs the complete satellite/drone image analysis pipeline for a village:
  1. Vegetation health analysis (NDVI)          -> src/vegetation_analysis.py
  2. Water body detection & level analysis (NDWI) -> src/water_detection.py
  3. Multi-temporal change detection            -> src/change_detection.py

This is a pure backend/code module — no web UI. Run it directly and it
will print a JSON analysis report to the console and save annotated
result images (heatmaps / masks / change maps) to output/.

Usage:
    python generate_sample_data.py   # creates sample multispectral images (first time only)
    python main.py
"""

import os
import json

from src.vegetation_analysis import analyze_vegetation
from src.water_detection import analyze_water
from src.change_detection import detect_change

BASE_DIR = os.path.dirname(__file__)
IMG_DIR = os.path.join(BASE_DIR, "sample_images")
OUT_DIR = os.path.join(BASE_DIR, "output")


def run_pipeline():
    os.makedirs(OUT_DIR, exist_ok=True)

    t1_rgb = os.path.join(IMG_DIR, "village_t1_rgb.png")
    t1_nir = os.path.join(IMG_DIR, "village_t1_nir.png")
    t2_rgb = os.path.join(IMG_DIR, "village_t2_rgb.png")
    t2_nir = os.path.join(IMG_DIR, "village_t2_nir.png")

    for p in [t1_rgb, t1_nir, t2_rgb, t2_nir]:
        if not os.path.exists(p):
            raise FileNotFoundError(
                f"Missing sample image: {p}\n"
                f"Run `python generate_sample_data.py` first, or replace "
                f"sample_images/*.png with real satellite/drone band images."
            )

    print("=" * 60)
    print("GramDarpan Image Analysis Pipeline")
    print("=" * 60)

    print("\n[1/3] Running Vegetation Health Analysis (NDVI) — Time 1 ...")
    veg_t1 = analyze_vegetation(t1_rgb, t1_nir, OUT_DIR, label="village_t1")

    print("[1/3] Running Vegetation Health Analysis (NDVI) — Time 2 ...")
    veg_t2 = analyze_vegetation(t2_rgb, t2_nir, OUT_DIR, label="village_t2")

    print("[2/3] Running Water Body Detection (NDWI) — Time 1 ...")
    water_t1 = analyze_water(t1_rgb, t1_nir, OUT_DIR, label="village_t1")

    print("[2/3] Running Water Body Detection (NDWI) — Time 2 ...")
    water_t2 = analyze_water(t2_rgb, t2_nir, OUT_DIR, label="village_t2")

    print("[3/3] Running Multi-Temporal Change Detection ...")
    change = detect_change(t1_rgb, t1_nir, t2_rgb, t2_nir, OUT_DIR, label="village")

    report = {
        "vegetation_analysis": {"time1": veg_t1, "time2": veg_t2},
        "water_analysis": {"time1": water_t1, "time2": water_t2},
        "change_detection": change,
    }

    report_path = os.path.join(OUT_DIR, "analysis_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("\n" + "=" * 60)
    print("ANALYSIS SUMMARY")
    print("=" * 60)
    print(f"Vegetation Health (T1): {veg_t1['health_status']} (mean NDVI {veg_t1['mean_ndvi']})")
    print(f"Vegetation Health (T2): {veg_t2['health_status']} (mean NDVI {veg_t2['mean_ndvi']})")
    print(f"Water Body Status (T1): {water_t1['status']} ({water_t1['water_area_percent']}% coverage)")
    print(f"Water Body Status (T2): {water_t2['status']} ({water_t2['water_area_percent']}% coverage)")
    print("\nChange Detection Alerts:")
    for alert in change["alerts"]:
        print(f"  - [{alert['severity']}] {alert['type']}: {alert['message']}")

    print(f"\nFull JSON report saved to: {report_path}")
    print(f"Output images saved to: {OUT_DIR}/")
    print("=" * 60)

    return report


if __name__ == "__main__":
    run_pipeline()
