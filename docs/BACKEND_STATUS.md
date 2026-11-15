# Backend implementation status

## Implemented in the backend foundation

- FastAPI application and health endpoint.
- Validated coordinate/radius/limit request schema.
- Configurable IRSA TAP endpoint, ObsCore table, collections, timeout-related settings and CORS origins.
- First metadata-only ObsCore query adapter using PyVO.
- Explicit scientific boundary: metadata records are not images, motion detections, or discoveries.
- Basic API validation tests.

## Not yet implemented (must not be represented as complete)

1. FITS cutout download and safe caching.
2. MEF HDU discovery by EXTNAME and validation of IMAGE, FLAGS, VARIANCE, ZODI, PSF and WCS-WAVE.
3. Pixel-quality masking based on release-specific official FLAGS definitions.
4. WCS-aware cutout rendering and browser-friendly image serving.
5. Observation grouping into target timelines and a real sequence endpoint compatible with the frontend.
6. Gaia/WISE cross-match with proper-motion epoch handling.
7. Verified motion evidence ledger and provenance checks.
8. End-to-end deployment and live IRSA smoke tests.

The first backend endpoint is deliberately metadata-only. Do not connect it to the current frontend `/search` contract until image processing and the observation-to-target response mapping are complete.
