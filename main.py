"""
main.py
--------
GramDarpan - Image Analysis Module: Full Pipeline

Runs the complete satellite/drone image analysis pipeline for a village:
  1. Vegetation health analysis (NDVI) -> src/vegetation_analysis.py
  2. Water body detection and level analysis (NDWI) -> src/water_detection.py
  3. Multi-temporal change detection -> src/change_detection.py

Usage:
    python generate_sample_data.py
    python main.py
    python main.py --image-dir sample_images --output-dir output
"""

import argparse
import json
import os
from html import escape

BASE_DIR = os.path.dirname(__file__)
IMG_DIR = os.path.join(BASE_DIR, "sample_images")
OUT_DIR = os.path.join(BASE_DIR, "output")


def _relative_path(path, start_dir):
    return os.path.relpath(path, start=start_dir).replace("\\", "/")


def create_html_report(report, out_dir):
    """Create a browser-friendly dashboard that links the generated maps."""
    html_path = os.path.join(out_dir, "analysis_dashboard.html")
    veg_t1 = report["vegetation_analysis"]["time1"]
    veg_t2 = report["vegetation_analysis"]["time2"]
    water_t1 = report["water_analysis"]["time1"]
    water_t2 = report["water_analysis"]["time2"]
    change = report["change_detection"]

    image_cards = [
        ("T1 NDVI Heatmap", veg_t1["heatmap_path"]),
        ("T2 NDVI Heatmap", veg_t2["heatmap_path"]),
        ("T1 Water Mask", water_t1["mask_path"]),
        ("T2 Water Mask", water_t2["mask_path"]),
        ("Change Detection", change["change_map_path"]),
    ]

    alert_items = "\n".join(
        f"<li><strong>{escape(alert['severity'])}</strong> - "
        f"{escape(alert['type'])}: {escape(alert['message'])}</li>"
        for alert in change["alerts"]
    )
    image_items = "\n".join(
        f"""
        <article class="card">
          <h3>{escape(title)}</h3>
          <img src="{escape(_relative_path(path, out_dir))}" alt="{escape(title)}">
        </article>
        """
        for title, path in image_cards
    )

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>GramDarpan Analysis Dashboard</title>
  <style>
    body {{
      margin: 0;
      font-family: Arial, sans-serif;
      background: #f5f7fa;
      color: #1f2933;
    }}
    header {{
      padding: 28px 32px;
      background: #12343b;
      color: white;
    }}
    main {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 24px;
    }}
    .metrics, .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 16px;
    }}
    .metric, .card, .alerts {{
      background: white;
      border: 1px solid #d8e0e7;
      border-radius: 8px;
      padding: 16px;
      box-shadow: 0 1px 2px rgba(15, 23, 42, 0.06);
    }}
    .metric span {{
      display: block;
      color: #627282;
      font-size: 13px;
      margin-bottom: 8px;
    }}
    .metric strong {{
      font-size: 24px;
    }}
    h1, h2, h3 {{
      margin-top: 0;
    }}
    h2 {{
      margin-top: 28px;
    }}
    img {{
      width: 100%;
      height: auto;
      border: 1px solid #e1e7ed;
      border-radius: 6px;
      background: #fff;
    }}
    li {{
      margin: 10px 0;
      line-height: 1.45;
    }}
  </style>
</head>
<body>
  <header>
    <h1>GramDarpan Analysis Dashboard</h1>
    <p>Vegetation health, water coverage, and multi-temporal change summary.</p>
  </header>
  <main>
    <section class="metrics">
      <div class="metric"><span>T1 Vegetation</span><strong>{escape(veg_t1['health_status'])}</strong><br>Mean NDVI {veg_t1['mean_ndvi']}</div>
      <div class="metric"><span>T2 Vegetation</span><strong>{escape(veg_t2['health_status'])}</strong><br>Mean NDVI {veg_t2['mean_ndvi']}</div>
      <div class="metric"><span>T1 Water Coverage</span><strong>{water_t1['water_area_percent']}%</strong><br>{escape(water_t1['status'])}</div>
      <div class="metric"><span>T2 Water Coverage</span><strong>{water_t2['water_area_percent']}%</strong><br>{escape(water_t2['status'])}</div>
      <div class="metric"><span>Vegetation Loss</span><strong>{change['vegetation_loss_percent']}%</strong><br>Significant decline area</div>
      <div class="metric"><span>Water Loss</span><strong>{change['water_loss_percent']}%</strong><br>Significant decline area</div>
    </section>

    <section class="alerts">
      <h2>Alerts</h2>
      <ul>{alert_items}</ul>
    </section>

    <h2>Generated Maps</h2>
    <section class="grid">
      {image_items}
    </section>
  </main>
</body>
</html>
"""
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    return html_path


def run_pipeline(img_dir=IMG_DIR, out_dir=OUT_DIR, create_dashboard=True):
    from src.change_detection import detect_change
    from src.vegetation_analysis import analyze_vegetation
    from src.water_detection import analyze_water

    os.makedirs(out_dir, exist_ok=True)

    t1_rgb = os.path.join(img_dir, "village_t1_rgb.png")
    t1_nir = os.path.join(img_dir, "village_t1_nir.png")
    t2_rgb = os.path.join(img_dir, "village_t2_rgb.png")
    t2_nir = os.path.join(img_dir, "village_t2_nir.png")

    for path in [t1_rgb, t1_nir, t2_rgb, t2_nir]:
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Missing sample image: {path}\n"
                "Run `python generate_sample_data.py` first, or replace "
                "sample_images/*.png with real satellite/drone band images."
            )

    print("=" * 60)
    print("GramDarpan Image Analysis Pipeline")
    print("=" * 60)

    print("\n[1/3] Running Vegetation Health Analysis (NDVI) - Time 1 ...")
    veg_t1 = analyze_vegetation(t1_rgb, t1_nir, out_dir, label="village_t1")

    print("[1/3] Running Vegetation Health Analysis (NDVI) - Time 2 ...")
    veg_t2 = analyze_vegetation(t2_rgb, t2_nir, out_dir, label="village_t2")

    print("[2/3] Running Water Body Detection (NDWI) - Time 1 ...")
    water_t1 = analyze_water(t1_rgb, t1_nir, out_dir, label="village_t1")

    print("[2/3] Running Water Body Detection (NDWI) - Time 2 ...")
    water_t2 = analyze_water(t2_rgb, t2_nir, out_dir, label="village_t2")

    print("[3/3] Running Multi-Temporal Change Detection ...")
    change = detect_change(t1_rgb, t1_nir, t2_rgb, t2_nir, out_dir, label="village")

    report = {
        "vegetation_analysis": {"time1": veg_t1, "time2": veg_t2},
        "water_analysis": {"time1": water_t1, "time2": water_t2},
        "change_detection": change,
    }

    report_path = os.path.join(out_dir, "analysis_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    dashboard_path = None
    if create_dashboard:
        dashboard_path = create_html_report(report, out_dir)

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
    if dashboard_path:
        print(f"HTML dashboard saved to: {dashboard_path}")
    print(f"Output images saved to: {out_dir}/")
    print("=" * 60)

    return report


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run the GramDarpan image analysis pipeline."
    )
    parser.add_argument(
        "--image-dir",
        default=IMG_DIR,
        help="Folder containing village_t1/t2 RGB and NIR images.",
    )
    parser.add_argument(
        "--output-dir",
        default=OUT_DIR,
        help="Folder where reports and map images will be saved.",
    )
    parser.add_argument(
        "--no-dashboard",
        action="store_true",
        help="Skip writing the HTML dashboard report.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_pipeline(
        img_dir=args.image_dir,
        out_dir=args.output_dir,
        create_dashboard=not args.no_dashboard,
    )
