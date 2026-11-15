# SimpleSpace API

Run with `uvicorn app.main:app --reload --port 8000`.

- GET /health
- POST /archive/observations — initial metadata adapter
- POST /archive/spherex — current DR1/QR3 SIA2 collection fan-out
- POST /archive/inspect-fits — MEF inspection
- POST /archive/preview — display-only preview
- POST /pipeline/process — ZODI subtraction and strict Level-2 FLAGS masking\n- POST /pipeline/cutout-preview — safe IRSA cutout download, MEF validation and processed preview
- POST /pipeline/detect — SEP detections on processed data (not discovery claims)

See ../docs/PIPELINE_IMPLEMENTATION.md for scientific scope and limitations.
