# SimpleSpace API

Run with `uvicorn app.main:app --reload --port 8000`.

- GET /health
- POST /archive/observations — metadata adapter
- POST /archive/spherex — DR1/QR3 SIA2 fan-out
- POST /archive/inspect-fits — MEF inspection
- POST /archive/preview — display-only preview
- POST /pipeline/process — ZODI subtraction and strict Level-2 FLAGS masking

See ../docs/PIPELINE_IMPLEMENTATION.md for scope and limitations.
