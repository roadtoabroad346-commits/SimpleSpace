# Backend implementation status

## Implemented
- FastAPI health endpoint and validated coordinate request schema.
- Configurable IRSA TAP/SIA settings; default collections use DR1 + QR3 and the DR1 cube, not QR2.
- Initial PyVO ObsCore metadata adapter (live schema compatibility still requires verification).
- SIA2 collection fan-out endpoint with partial-failure reporting and cloud_access JSON parsing.
- FITS MEF inspection by EXTNAME.
- Strict Level-2 32-bit FLAGS masking with SOURCE retained.
- ZODI subtraction before any optional unit conversion.
- Optional solid-angle conversion from MJy/sr to microJy/pixel when the official calibration map is supplied.
- SEP background estimation and source extraction utilities.
- Exact flux and nearest-neighbour FLAGS reprojection primitives.
- Separate 64-bit Level-3 photometry flag filtering.
- 102-channel detector/subchannel index helpers.
- Render Docker and Blueprint configuration.

## Not yet complete
1. Live SIA2/TAP validation against current archive and complete cloud_access S3 retrieval.
2. Safe cutout downloader with retry/backoff, bounded concurrency, checksum validation and cache.
3. Version-matched SAPM, CWAVE, CBAND and SPECTRAL_CHANNELS calibration retrieval.
4. Full spectral WCS and channel assignment from official calibration products.
5. Robust source photometry, 1D spectra, difference imaging and multi-epoch evidence ledger.
6. Complete Gaia DR3, AllWISE and CatWISE2020 TAP adapters with uncertainty-aware epoch propagation.
7. End-to-end frontend integration and live deployment smoke tests.

No item in the second list should be represented as complete.
