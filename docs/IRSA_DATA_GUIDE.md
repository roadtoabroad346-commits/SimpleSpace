# IRSA / SPHEREx Data Guide

## Current archive products

IRSA's current SIA2 collections for the SimpleSpace baseline are:
- `spherex_dr1` — DR1 Wide Survey spectral-image MEFs.
- `spherex_dr1_deep` — DR1 Deep Survey MEFs.
- `spherex_qr3` — QR3 Wide Survey spectral-image MEFs.
- `spherex_qr3_deep` — QR3 Deep Survey MEFs.
- `spherex_dr1_cube` — separate DR1 All-Sky Cube product.

DR1 + QR3 supersede QR2 for new work. The cube is a separate product, not another Level-2 MEF collection. New data are ingested weekly; SIA2 availability may lag the browsable archive by approximately one day.

## Level-2 MEF

Locate HDUs by `EXTNAME`, not fixed index. The common scientific extensions include:
- `IMAGE`: calibrated surface brightness in MJy/sr.
- `FLAGS`: 32-bit per-pixel bitmask.
- `VARIANCE`: per-pixel variance.
- `ZODI`: zodiacal-light model; subtract from IMAGE before mosaicking.
- `EPSF`: effective PSF model in DR1/QR3.
- `WCS-WAVE`: spectral lookup table for visualization.

DR1/QR3 use ePSF products; QR2 used PSF products. Do not assume a single PSF extension name across releases.

## Spectral mapping

The all-sky cube contains 102 nominal channels, represented as six detectors × 17 subchannels. The detector's wavelength gradient is spatially varying. Use the official SPECTRAL_CHANNELS calibration product for channel metadata and CWAVE/CBAND maps for science-grade per-pixel wavelength/bandwidth. WCS-WAVE is useful for visualization, but its precision limitations are stated in the official supplement.

## Cutouts and cloud access

SIA2 results expose an on-premises `access_url` and cloud-hosted `cloud_access` metadata. Parse cloud_access as JSON; do not hardcode S3 keys or derive a path from a filename. IRSA Cutout Service accepts center and size query parameters on on-premises image URLs. Preserve original archive URLs and provenance.

## Processing order

1. Read/copy FITS arrays with memmap disabled.
2. Validate IMAGE, FLAGS, ZODI and optional VARIANCE shapes.
3. Subtract ZODI.
4. Apply release-aware FLAGS selection before reprojection and photometry.
5. Apply official solid-angle calibration only when its version matches the image product.
6. Estimate background and perform source extraction/photometry.
7. Reproject flux and categorical flags with appropriate algorithms.
8. Record detector, collection, observation time, processing version, calibration versions, source URL and DOI.

See `PIPELINE_IMPLEMENTATION.md` and the official [SPHEREx Archive User Guide](https://caltech-ipac.github.io/spherex-archive-documentation/).
