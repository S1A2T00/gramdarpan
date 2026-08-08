# GramDarpan — Image Analysis for Rural Land Monitoring

A small toolkit for analyzing satellite or aerial images to detect land-use changes and features relevant to rural monitoring (vegetation, water bodies, and general change detection).

## Key Features
- Change detection between image pairs
- Vegetation health and coverage analysis
- Water body detection and basic mapping
- Generate sample data for testing and reproducible examples

## Requirements
- Python 3.8+
- See `requirements.txt` for exact dependencies

## Installation
1. Create a virtual environment (recommended):

```powershell
python -m venv venv
venv\Scripts\Activate.ps1   # PowerShell
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

## Quick Usage
Run the main analysis pipeline:

```powershell
python main.py
```

The pipeline now also creates a browser-friendly dashboard:

```text
output/analysis_dashboard.html
```

Use custom folders when needed:

```powershell
python main.py --image-dir sample_images --output-dir output
```

Skip the HTML dashboard and write only JSON/images:

```powershell
python main.py --no-dashboard
```

Generate sample data for experimentation:

```powershell
python generate_sample_data.py
```

Notes:
- Input images can be placed in the `sample_images/` folder (or configured in code).
- Analysis output is written to the `output/` folder; examples include `output/analysis_report.json` and `output/analysis_dashboard.html`.

## Project Structure
- `main.py` — entry point to run the analysis pipeline
- `generate_sample_data.py` — creates synthetic/sample images for testing
- `requirements.txt` — Python package dependencies
- `sample_images/` — example input images
- `output/` — analysis outputs (reports, maps)
- `src/` — core modules
  - `src/change_detection.py` — change detection routines
  - `src/vegetation_analysis.py` — vegetation indexes and metrics
  - `src/water_detection.py` — water detection helpers

## Example Workflow
1. Place your imagery in `sample_images/` (or update input path in `main.py`).
2. Activate environment and install deps.
3. Run `python main.py` to produce `output/analysis_report.json` and any derived artifacts.

## Contributing
PRs and issues are welcome. Please:
- Open an issue describing the bug or feature
- Add tests for changes when possible

## Next Steps / TODOs
- Add CLI arguments to `main.py` for configurable input/output paths and options
- Add unit tests and CI
- Provide an example dataset and sample results

## License
Add a `LICENSE` file to clarify the project license. If none is provided, please assume "All rights reserved" until a license is added.

---

If you'd like, I can add a minimal example command with expected outputs or wire up CLI options in `main.py` next.
