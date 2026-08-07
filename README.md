GramDarpan — Image Analysis Module
This is a pure backend/code module — no frontend/web UI (intentionally kept hidden for now). It performs remote-sensing based image analysis on satellite/drone imagery of a village, forming the core AI/data-processing layer of the GramDarpan Digital Twin.

What it does
Using standard remote-sensing techniques:

Vegetation Health Analysis (NDVI) — src/vegetation_analysis.py Computes crop/vegetation health from Red + NIR bands. Produces a zone-wise (grid) health status for each field: Poor / Moderate / Good.
Water Body Detection (NDWI) — src/water_detection.py Detects water body extent (ponds/canals) from Green + NIR bands and calculates % coverage plus a status (Normal / Low / Critical).
Multi-Temporal Change Detection — src/change_detection.py Compares two images from different time periods to detect vegetation decline or water shrinkage — an early-warning system for crop stress, drought, or encroachment.
Everything runs as plain scripts — results print to the console as a JSON report, and annotated output images (heatmaps, masks, change maps) are saved to the output/ folder.

Folder Structure
gramdarpan-image-analysis/
├── generate_sample_data.py     # Generates synthetic multispectral sample images (for demo)
├── main.py                      # Full pipeline runner — runs all analyses together
├── requirements.txt
├── src/
│   ├── vegetation_analysis.py   # NDVI - crop/vegetation health
│   ├── water_detection.py       # NDWI - water body detection
│   └── change_detection.py      # Time-series change detection
├── sample_images/                # Synthetic RGB + NIR band images (generated)
└── output/                       # Analysis results: heatmaps, masks, JSON report (generated)
Setup & Run
bash
cd gramdarpan-image-analysis
pip install -r requirements.txt

# Step 1: Generate synthetic sample satellite images (first run only)
python generate_sample_data.py

# Step 2: Run the full analysis pipeline
python main.py
You'll get:

Console output: a readable summary + severity-tagged alerts
output/analysis_report.json: the full structured report
output/*.png: NDVI heatmap, NDWI water mask, change detection maps
Using Real Satellite/Drone Data
The sample_images/ folder currently contains synthetic (computer generated) images since real data isn't available for an offline demo. To use this pipeline with real data, simply replace:

village_t1_rgb.png / village_t1_nir.png with your own Red-Green-Blue and Near-Infrared (NIR) band images (e.g. from Sentinel-2: Bands 4/3/2 = RGB, Band 8 = NIR)
Sources: Bhuvan (ISRO), Sentinel Hub / Copernicus, or a drone multispectral camera (DJI P4 Multispectral, MicaSense, etc.)
The rest of the code stays the same — the NDVI/NDWI math is standard and works on any valid Red/Green/NIR band input.

Extending
Next step	File to modify
Real ML crop-disease classifier (CNN on RGB)	Add a new function in src/, call it from main.py
GenAI natural-language advisory for farmers	Feed analysis_report.json into the Claude API (/v1/messages) as a summarization/reasoning step
Scale to many villages	Loop main.py's pipeline over a list of village image folders
GIS/map integration	Once ready, this module's JSON + image outputs can feed directly into the earlier GramDarpan GIS mapping layer (agriculture/water/risk layers)
Notes
This module is frontend-free as requested — just Python scripts and saved image outputs, no Flask/HTML/JS.
NDVI/NDWI thresholds follow standard remote-sensing conventions, but fine-tuning against ground-truth data is recommended for real-world calibration.

