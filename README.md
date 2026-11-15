# 🛰️ SimpleSpace — Team Palanteer

**Explore how the sky changes across real SPHEREx observations.**

SimpleSpace is Team Palanteer's NASA Space Apps Challenge 2026 project for **Planet X and SPHEREx**. We are building an evidence-first research experience that combines real NASA/IPAC IRSA SPHEREx observations, reproducible FITS processing, spectral context, and multi-epoch candidate review.

> **Current truth about the build:** the research UI still uses curated demonstration sequences. The API now has an IRSA SIA2 collection-search adapter and scientific processing primitives for FITS MEFs: ZODI subtraction, a strict Level-2 FLAGS mask, optional solid-angle conversion, SEP background/source extraction, and reprojection helpers. The complete live SIA2 → cutout → calibrated processing → time-series viewer workflow is not yet finished. Demonstration frames must never be described as live archive results.

## What we are building

- Search current SPHEREx observations by sky coordinates across DR1 and QR3 Wide/Deep collections, with the DR1 All-Sky Cube available as a separate product.
- Inspect Level-2 MEF extensions by EXTNAME rather than relying on fixed HDU positions.
- Mask quality-affected pixels before photometry/reprojection, while preserving source flags and provenance.
- Subtract zodiacal background and apply official per-pixel solid-angle calibration when supplied.
- Detect sources and compare repeated observations; separate likely artifacts, known objects, variables, and possible movers.
- Cross-match Gaia DR3, AllWISE, and CatWISE2020 with epoch-aware astrometry.
- Present the observation epoch, collection/release, detector, wavelength, bandwidth, and archive provenance for each measurement.

## Implementation status

| Component | Status |
|---|---|
| React + TypeScript + Vite research UI | Implemented; currently fixture-backed |
| FastAPI backend and health endpoint | Implemented |
| IRSA TAP metadata adapter | Initial adapter; live schema validation pending |
| IRSA SIA2 DR1/QR3 fan-out endpoint | Implemented; live archive smoke test pending |
| FITS MEF inspection by EXTNAME | Implemented |
| Strict 32-bit Level-2 FLAGS masking | Implemented with tests |
| ZODI subtraction | Implemented |
| MJy/sr → μJy/pixel | Implemented when official solid-angle map is supplied |
| SEP background/source extraction | Implemented as backend utilities/API |
| Flux and FLAGS reprojection primitives | Implemented |
| Official CWAVE/CBAND wavelength calibration | Helper implemented; calibration discovery/loading pending |
| Live cutout download, retries and caching | Not yet complete |
| Automated SAPM/CWAVE/CBAND/SPECTRAL_CHANNELS retrieval | Not yet complete |
| End-to-end difference imaging and 1D spectra | Not yet complete |
| Validated Gaia/WISE catalog TAP matching | Utility foundation only |
| Candidate evidence ledger and live viewer integration | Not yet complete |
| Public production deployment | Blueprint prepared; deployment not yet verified |

## Architecture

- **Frontend:** React, TypeScript, Vite, Framer Motion.
- **API:** FastAPI + Pydantic.
- **Science:** NumPy, Astropy, Astroquery, PyVO, SEP, Reproject.
- **Archive:** NASA/IPAC IRSA SIA2/TAP and anonymous AWS Open Data access.
- **Deployment:** Render Blueprint in `render.yaml` (static frontend + containerized API).

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
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

### Scientific Conda environment
```bash
conda env create -f backend/environment.yml
conda activate spherex_sdt
```

## API endpoints

- `GET /health`
- `POST /archive/observations` — initial ObsCore metadata adapter.
- `POST /archive/spherex` — concurrent SIA2 searches across enabled collections.
- `POST /archive/inspect-fits` — MEF structure and quality inspection.
- `POST /archive/preview` — display-only preview (not calibrated).
- `POST /pipeline/process` — ZODI subtraction and strict Level-2 FLAGS masking.
- `POST /pipeline/detect` — SEP detections on processed images; output is not a discovery claim.

## Deployment

A Render Blueprint is included. Create a Blueprint from this public repository and select the working branch for a preview. Review the proposed resources and any costs before approving deployment. The API health check is `/health`. The public website is not live until the deployment succeeds and is smoke-tested.

## Official scientific references

- [SPHEREx Archive — Data Releases](https://irsa.ipac.caltech.edu/spherex-archive-documentation/spherex-data-releases/)
- [SPHEREx Archive — Data Access](https://caltech-ipac.github.io/spherex-archive-documentation/spherex-data-access/)
- [SPHEREx Archive — Data Products](https://caltech-ipac.github.io/spherex-archive-documentation/spherex-data-products/)
- [SPHEREx Explanatory Supplement v2.1](https://irsa.ipac.caltech.edu/data/SPHEREx/docs/SPHEREx_Expsupp.pdf)
- [IRSA SPHEREx tutorials](https://caltech-ipac.github.io/irsa-tutorials/)
- [SPHEREx Cutout Service](https://irsa.ipac.caltech.edu/data/SPHEREx/docs/cutout_tool.html)

The current archive baseline is DR1 + QR3. DR1 contains Survey 1 and 2 data reprocessed with the same improved pipeline/calibrations as QR3; QR3 contains Survey 3 and 4. The DR1 All-Sky Cube is a separate 102-channel product. SIA2 availability may lag archive ingestion by about a day, and new data are ingested weekly.

## Team

**Palanteer** — NASA Space Apps Challenge 2026.

## Required SPHEREx acknowledgement

This project uses public data products from SPHEREx, a joint project of the Jet Propulsion Laboratory and the California Institute of Technology, funded by NASA:

> This publication makes use of data products from the Spectro-Photometer for the History of the Universe, Epoch of Reionization and Ices Explorer (SPHEREx), which is a joint project of the Jet Propulsion Laboratory and the California Institute of Technology, and is funded by the National Aeronautics and Space Administration.

Dataset-specific DOI citations and acknowledgements are listed in `docs/CREDITS.md`. Every scientific output must retain its source product, collection, observation epoch, detector, calibration version, and processing history.

## AI-use disclosure

AI-assisted development is disclosed in [AI_USAGE.md](AI_USAGE.md). No astronomical image, measurement, or candidate is AI-generated. All sky data must trace to actual archive products.

## License

The repository retains the upstream Apache-2.0 license and attribution. See [LICENSE](LICENSE) and [docs/CREDITS.md](docs/CREDITS.md).
