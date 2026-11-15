# 🛰️ SimpleSpace

**Explore how the sky changes across real SPHEREx observations.**

A public-facing research viewer for NASA Space Apps Challenge 2026: *Planet X and SPHEREx*.

> **Implementation status:** the frontend currently includes a curated local demonstration dataset. The backend foundation now provides an IRSA TAP metadata-query endpoint. Browser-ready FITS cutouts, full MEF quality processing, and end-to-end live archive timelines are still in progress. Do not interpret fixture data as live search results.

## Current capabilities

- React + TypeScript + Vite research viewer.
- Curated observation sequences and coordinate-based deep links.
- Playback controls, field-of-view controls, spectral-channel interface, and source provenance panel.
- Frontend component and utility tests.
- FastAPI health endpoint and validated archive-search request.
- Initial PyVO adapter for IRSA ObsCore metadata.
- Configurable IRSA endpoint, ObsCore table, and SPHEREx collections.

## Scientific workflow being implemented

1. Search the official IRSA archive by sky coordinates.
2. Retrieve relevant SPHEREx observations across configured releases.
3. Download cutouts and inspect FITS MEF extensions by EXTNAME, not hard-coded HDU positions.
4. Apply release-aware pixel-quality handling using official FLAGS definitions.
5. Convert validated image planes into browser-ready assets while retaining source-file, epoch, release, detector, and DOI provenance.
6. Compare observations in time and distinguish motion from variability, artifacts, and insufficient evidence.
7. Cross-match known sources only with epoch-aware astrometry; a missing catalog match is not proof of discovery.

## Run locally

### Frontend

```bash
cd frontend
npm ci
npm run dev
```

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

Backend API docs: `http://localhost:8000/docs`. Current metadata endpoint: `POST /archive/observations`.

```json
{"ra": 7.413807, "dec": 9.976979, "radius_deg": 0.1, "limit": 50}
```

## Official data references

- [SPHEREx Archive documentation](https://caltech-ipac.github.io/spherex-archive-documentation/)
- [IRSA SPHEREx tutorials](https://caltech-ipac.github.io/irsa-tutorials/)
- [IRSA SPHEREx Data Explorer](https://irsa.ipac.caltech.edu/applications/SPHEREx/)

IRSA notes that SPHEREx data are ingested weekly and SIA2 availability can lag archive ingestion. Release configuration and data freshness must remain explicit.

## Project documentation

- `docs/CHALLENGE.md` — challenge interpretation.
- `docs/JUDGING_CRITERIA.md` — judging criteria.
- `docs/MVP_CUT_LINE.md` — MVP scope.
- `docs/DATA_CONTRACT.md` — frontend/data contract.
- `docs/DATA_RELEASES.md` — release registry notes.
- `docs/IRSA_DATA_GUIDE.md` — archive and FITS notes.
- `docs/BACKEND_STATUS.md` — implemented and outstanding backend work.
- `docs/CREDITS.md` — data and project attribution.
- `AI_USAGE.md` — AI-use disclosure log.

## License and attribution

This repository retains the upstream Apache-2.0 license and attribution. See `LICENSE` and `docs/CREDITS.md`. Astronomical measurements and images must come from traceable archive products; generated or fabricated sky data are not acceptable.