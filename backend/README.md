# SimpleSpace API

FastAPI service for querying SPHEREx observation metadata through the official IRSA TAP service.

## Local development

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

- Health: `GET /health`
- Archive metadata: `POST /archive/observations`
- FITS inspection: `POST /archive/inspect-fits` (multipart file upload)\n- Preview PNG: `POST /archive/preview` (multipart file upload; percentile stretch, no FLAGS decoding)\n- OpenAPI: `/docs`

Example request:

```json
{"ra": 7.413807, "dec": 9.976979, "radius_deg": 0.1, "limit": 50}
```

## Scientific boundary

The archive endpoint returns ObsCore metadata and access URLs only. The upload inspector locates extensions by `EXTNAME` and reports observed non-zero FLAGS values without guessing their meanings. The preview is only a display aid: it does not decode or mask FLAGS and is not a calibrated scientific product. The service does **not** yet fetch IRSA cutouts, group observations into target timelines, calculate source motion, or identify new objects. Those steps must be implemented and validated separately before the frontend labels a result as a candidate. Unknown or unavailable metadata must remain unknown; it must not be filled with invented values.

Collections and TAP table are configurable because IRSA releases and archive schemas can evolve. Check the official [SPHEREx archive documentation](https://caltech-ipac.github.io/spherex-archive-documentation/) before changing production configuration.
