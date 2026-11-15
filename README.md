# Simple Space — Team Palanteer

**Explore how the sky changes across real SPHEREx observations.**

Simple Space is a NASA Space Apps Challenge 2026 project by **Team Palanteer**. It is a research-oriented prototype for exploring repeated observations from **SPHEREx** and organizing the evidence needed to review unusual or changing sources.

Our goal is to make the path from archive data to a reviewable scientific candidate clearer and more reproducible: discover observations, inspect the FITS products, apply documented quality handling, compare epochs, and check known-source catalogues.

> [!IMPORTANT]
> **Scientific and demo status (15 November 2026).** The current web interface is still primarily a curated demonstration experience; it is not yet a fully live SPHEREx analysis dashboard. The API contains initial IRSA archive adapters and FITS-processing utilities, but a complete, validated archive-to-candidate workflow and full frontend/API integration have not been completed. Do not interpret demonstration frames or unmatched detections as new astronomical discoveries.

---

## Project at a glance

| | |
|---|---|
| Challenge | NASA Space Apps Challenge 2026 |
| Project | SimpleSpace |
| Team | Palanteer |
| Scientific domain | SPHEREx infrared all-sky spectroscopy and time-domain exploration |
| Frontend | React, TypeScript, Vite |
| Backend | Python, FastAPI |
| Science stack | Astropy, NumPy, SEP, PyVO / Astroquery, Reproject |
| Archive services | NASA/IPAC Infrared Science Archive (IRSA), SIA2 and TAP |
| Deployment targets | GitHub Pages (static frontend), Render (API) |

## Why this matters

SPHEREx observes the sky in many infrared spectral channels. Repeated observations and complementary catalogues can help researchers investigate sources whose brightness, position, or measured properties may change over time.

A useful candidate-review workflow must do more than display a bright pixel. It should preserve the source observation and release, account for data-quality flags, document processing choices, compare observations at their actual epochs, and check whether known catalogued objects can explain the signal.

Simple Space is designed around that evidence-first approach. It is a prototype and research aid, not an automated discovery authority.

## Intended workflow

1. **Find observations.** Search SPHEREx archive collections around a sky position and inspect the returned metadata.
2. **Inspect the FITS product.** Identify relevant MEF extensions by their `EXTNAME`, inspect image dimensions and WCS metadata, and review available quality information.
3. **Apply quality-aware processing.** Respect Level-2 FLAGS, estimate and subtract the zodiacal component where supported, and preserve processing metadata.
4. **Explore sources.** Run source-extraction utilities on processed images and inspect detections as candidates for further review.
5. **Check known objects.** Query supported Gaia, AllWISE, and CatWISE catalogue services and compare positions with epoch awareness.
6. **Review evidence.** Keep the observation, release, epoch, detector, calibration context, and processing history attached to scientific outputs.

The workflow above describes the project's intended scientific direction. Not every step is currently connected end-to-end in the public UI.

## Current implementation status

| Area | Current status |
|---|---|
| React + TypeScript research interface | Implemented; curated/demo data is still used |
| FastAPI service and `GET /health` | Implemented |
| IRSA TAP metadata adapter | Initial implementation; live schema and archive validation remain |
| IRSA SIA2 SPHEREx collection search | Initial endpoint implemented; live archive smoke test remains |
| FITS MEF inspection by `EXTNAME` | Implemented |
| Display-only FITS preview | Implemented; explicitly not calibrated science output |
| Level-2 FLAGS handling | Strict mask utility implemented; verify release-specific semantics against official documentation before scientific interpretation |
| ZODI subtraction utility | Implemented |
| Optional solid-angle conversion support | Utility support exists when the official map is supplied |
| SEP background/source extraction utilities | Implemented |
| Reprojection helpers | Implemented |
| IRSA cutout download and processed preview | Initial endpoint and bounded download safeguards implemented; live service validation remains |
| Gaia / AllWISE / CatWISE TAP query and matching foundation | Implemented as an initial utility; scientific validation and UX remain |
| Full CWAVE / CBAND / SAPM calibration discovery and application | Not complete |
| Complete 102-channel All-Sky Cube spectral workflow | Not complete |
| Validated multi-epoch difference-imaging pipeline | Not complete |
| Fully validated 1D spectral extraction and calibrated photometry | Not complete |
| Live candidate timeline and evidence ledger in frontend | Not complete |
| End-to-end frontend-to-API integration | Not complete |
| Public production deployment and live scientific smoke test | Not yet verified |

**Interpretation guardrails**

- A display stretch is for visual inspection only. It is not a calibrated flux image.
- A source-extraction result is a detection candidate, not a discovery.
- A missing catalogue match does not prove that an object is new.
- A cross-match must account for catalogue epoch and astrometric uncertainty.
- Do not compare fluxes across observations until the relevant calibration, masks, units, and image registration have been validated.
- Do not claim a moving object, transient, or Planet X detection from the current prototype.

## Architecture

```text
SimpleSpace/
├── frontend/                 # React + TypeScript + Vite interface
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI routes
│   │   └── services/          # Archive, FITS, processing and catalogue utilities
│   ├── requirements.txt
│   ├── environment.yml
│   └── Dockerfile
├── docs/                      # Scientific implementation notes and credits
├── .github/workflows/         # CI and GitHub Pages deployment
├── render.yaml                # Render Blueprint
├── AI_USAGE.md
└── README.md
```

### Technology

- **Frontend:** React, TypeScript, Vite, Framer Motion, Tailwind CSS.
- **API:** FastAPI and Pydantic.
- **Scientific Python:** NumPy, Astropy, Astroquery, PyVO, SEP, Reproject, Pillow.
- **Archive protocols:** IRSA SIA2 and TAP.
- **Automation:** GitHub Actions.
- **Hosting:** GitHub Pages for static files; Render for the Python API.

---

## Run locally

Use two terminals from the repository root.

### 1. Start the API

Python 3.12 is the CI target.

**macOS / Linux**
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Windows PowerShell**
```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

API health check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)  
Interactive API documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 2. Start the frontend

In a second terminal:

```bash
cd frontend
npm ci
npm run dev
```

Open the local Vite URL printed in the terminal (normally [http://localhost:5173](http://localhost:5173)).

> [!NOTE]
> Starting both services does not make every screen live-data-backed. The current frontend still contains curated demonstration content and its full integration with the newer API routes is pending. Use the API docs to demonstrate backend endpoints independently.

### Optional Conda environment

From the repository root:

```bash
conda env create -f backend/environment.yml
conda activate spherex_sdt
```

If the environment file or a dependency fails on your platform, use the Python virtual-environment instructions above and consult the error output.

---

## API reference

The FastAPI application exposes these routes:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Service health |
| POST | `/archive/observations` | Initial IRSA TAP / ObsCore metadata search |
| POST | `/archive/spherex` | SIA2 search across configured SPHEREx collections |
| POST | `/archive/inspect-fits` | Inspect an uploaded FITS MEF |
| POST | `/archive/preview` | Return a display-only PNG preview |
| POST | `/pipeline/process` | Apply current Level-2 processing utilities and return a preview |
| POST | `/pipeline/detect` | Run SEP source extraction on processed image data |
| POST | `/pipeline/cutout-preview` | Request an IRSA cutout, process it, and return a preview |
| POST | `/catalogs/crossmatch` | Query supported catalogues and return initial cross-match results |

All POST request schemas and response examples are available in Swagger at `/docs`.

### Upload and processing constraints

- FITS upload endpoints currently enforce a **20 MiB** request-file limit.
- The preview endpoints return PNG images for display; they do not claim calibrated science products.
- The cutout endpoint validates the remote archive URL and applies bounded download safeguards.
- Archive and TAP services may time out or be temporarily unavailable; callers should handle API errors and partial catalogue results.
- Do not upload private data or credentials to the public repository.

### Example health check

```bash
curl http://127.0.0.1:8000/health
```

For exact request bodies, use the generated OpenAPI documentation rather than guessing parameter names.

---

## Demo guide for reviewers

The safest current demonstration is to separate the **interface demo** from the **API prototype**.

### Interface walkthrough

1. Open the deployed frontend, if the GitHub Pages workflow has completed successfully.
2. Explain that the current observation sequence is curated demonstration content.
3. Walk through the available sky/exploration views and explain the intended repeated-observation workflow.
4. Do not label fixture images as live IRSA results.

### API walkthrough

1. Open the backend Swagger page at `/docs`.
2. Call `GET /health` to confirm that the API is responding.
3. Use `POST /archive/spherex` to demonstrate the initial SIA2 search adapter, if the live archive is reachable.
4. Use the FITS inspection and preview routes with a valid, appropriately sized SPHEREx FITS MEF file.
5. Explain that the preview is display-only and that a source extraction is not a discovery.

**Before a judged live demo:** verify the deployed frontend and API in a clean browser session, test the exact archive query, and have a small permitted FITS sample ready. Do not rely on a live archive response without a fallback explanation.

---

## Deployment

### Frontend — GitHub Pages

A workflow is provided at `.github/workflows/pages.yml`. It builds the Vite frontend with the repository base path and publishes the generated `frontend/dist` directory.

To enable it:

1. Open **Settings → Pages** in the GitHub repository.
2. Under **Build and deployment**, select **GitHub Actions** as the source.
3. Open the **Actions** tab and check the run named **Deploy SimpleSpace to GitHub Pages**.
4. Wait for the deploy job to finish successfully before sharing the URL.

Expected project-site URL after successful publication:

[https://roadtoabroad346-commits.github.io/SimpleSpace/](https://roadtoabroad346-commits.github.io/SimpleSpace/)

The URL is an expected address, not proof that Pages is already enabled or that the latest workflow has succeeded.

### Backend — Render

A Render Blueprint is included in `render.yaml`. It defines a containerized FastAPI service and a static frontend service.

- Review the Blueprint and environment variables before creating resources.
- Confirm that the API health check `/health` passes.
- Configure CORS to allow the actual frontend origin.
- Configure the frontend API base URL only when the frontend API integration is ready.
- Check service logs and test archive connectivity after deployment.

The Render deployment is not considered production-ready until both services build successfully and the API is smoke-tested. Free services may sleep when idle.

---

## Testing and quality checks

The repository CI workflow is configured to run:

**Frontend**
```bash
cd frontend
npm ci
npm test
npm run build
```

**Backend**
```bash
cd backend
pip install -r requirements.txt
pytest -q
```

CI also includes a secret scan and a guard against committing raw FITS files or files larger than 5 MiB. The API's own FITS upload limit is separate from this repository file-size guard.

A workflow being present does not mean the latest run passed. Check the repository's **Actions** tab for the actual status of the current commit.

---

## Scientific data, releases and references

The current archive search baseline is **SPHEREx DR1 + QR3**. The DR1 All-Sky Cube is a separate data product and should not be confused with the spectral-image collections. Confirm collection names, product availability, calibration files, and release-specific flag definitions against the official documentation before scientific use.

Official references:

- [SPHEREx Archive — Data Releases](https://irsa.ipac.caltech.edu/spherex-archive-documentation/spherex-data-releases/)
- [SPHEREx Archive — Data Access](https://caltech-ipac.github.io/spherex-archive-documentation/spherex-data-access/)
- [SPHEREx Archive — Data Products](https://caltech-ipac.github.io/spherex-archive-documentation/spherex-data-products/)
- [SPHEREx Explanatory Supplement v2.1 (PDF)](https://irsa.ipac.caltech.edu/data/SPHEREx/docs/SPHEREx_Expsupp.pdf)
- [IRSA SPHEREx tutorials](https://caltech-ipac.github.io/irsa-tutorials/)
- [SPHEREx Cutout Service](https://irsa.ipac.caltech.edu/data/SPHEREx/docs/cutout_tool.html)
- [IRSA acknowledgement guidelines](https://irsa.ipac.caltech.edu/ack.html)
- [IRSA data use terms](https://irsa.ipac.caltech.edu/data_use_terms.html)

### Data citations and acknowledgement

Cite the DOI for each SPHEREx release/product actually used in the submission or generated scientific output. The project tracks relevant DOI information and the required acknowledgement in [docs/CREDITS.md](docs/CREDITS.md).

Required SPHEREx acknowledgement:

> This publication makes use of data products from the Spectro-Photometer for the History of the Universe, Epoch of Reionization and Ices Explorer (SPHEREx), which is a joint project of the Jet Propulsion Laboratory and the California Institute of Technology, and is funded by the National Aeronautics and Space Administration.

Every scientific output should retain, where available, its source product identifier, collection/release, observation epoch, detector, calibration context, and processing history.

---

## AI-use disclosure

This project uses AI-assisted coding and documentation. Team members remain responsible for reviewing, testing, and validating the software and all scientific interpretations.

**No astronomical observations, FITS measurements, sky images, or candidate detections are AI-generated or fabricated.** The current UI's curated demonstration content must be identified as such. See [AI_USAGE.md](AI_USAGE.md) for the project disclosure.

## Credits and licensing

See [docs/CREDITS.md](docs/CREDITS.md) for data acknowledgements, scientific references, and software credits.

The repository retains the upstream **Apache License 2.0** and attribution. See [LICENSE](LICENSE). Third-party dependencies remain under their respective licenses.

---

## Team

**Palanteer** — NASA Space Apps Challenge 2026.

Built to make SPHEREx data exploration more transparent, reproducible, and accessible.
