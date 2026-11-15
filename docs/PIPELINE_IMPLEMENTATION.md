# SPHEREx Pipeline — Implementation and Scientific Guardrails

## Current processing order

1. Open the MEF with `memmap=False`; copy extension arrays before closing the HDUList.
2. Resolve extensions by `EXTNAME`, not assumed HDU number.
3. Validate matching IMAGE, FLAGS, ZODI and optional VARIANCE dimensions.
4. Subtract zodiacal model: `IMAGE - ZODI`.
5. Apply the strict SimpleSpace Level-2 quality mask before background estimation, reprojection or source extraction.
6. If the official per-pixel solid-angle calibration is supplied in steradians, convert MJy/sr to microJy/pixel with `1e12 * solid_angle_sr`.
7. Estimate local background on native-endian arrays with SEP.
8. Reproject flux with exact overlap; reproject categorical FLAGS with nearest-neighbour interpolation.
9. Extract sources on the processed image; preserve SNR, flux uncertainty, source coordinates and provenance.
10. Cross-match only against catalog positions propagated to the observation epoch when valid proper motions are present.

## FLAGS namespaces

- Level-2 MEF `FLAGS` is a 32-bit pixel-level bitmask. See `backend/app/services/flags.py`.
- The strict SimpleSpace mask is the conservative policy supplied in the project specification. It masks the specified critical bits and intentionally retains `SOURCE` (bit 21).
- Level-3 photometry `CONTAINS_BAD_PIXEL` (bit 32) and `FIT_ERROR` (bit 33) belong to a separate 64-bit output flag namespace. They must not be shifted into a uint32 pixel mask.
- `CONTAINS_BAD_PIXEL` is a warning about nearby problematic pixels, not an automatic statement that every measurement is unusable. The final selection policy must retain the underlying bit provenance.

The official SPHEREx Explanatory Supplement distinguishes masks used for mosaics, background estimation, and photometry. SimpleSpace's strict policy is deliberately documented as a project policy, not a claim to reproduce every IRSA tool's exact selection.

## Spectral channels

The nominal all-sky cube contains 102 channels: six detector arrays × 17 subchannels. Use the official `SPECTRAL_CHANNELS` calibration product for wavelength edges, central wavelength and bandwidth. Do not use the inconsistent per-band channel-count draft table as a mapping.

For precision science, prefer official `CWAVE` and `CBAND` calibration maps. `WCS-WAVE` is a FITS lookup useful for visualization; its precision limitations are described in the official supplement. If WCSNAMEW is used for visualization, clear inherited SIP distortion as required by the FITS/WCS interpretation.

## Release policy

Default image search collections:
- `spherex_dr1`
- `spherex_dr1_deep`
- `spherex_qr3`
- `spherex_qr3_deep`

The DR1 cube collection `spherex_dr1_cube` is a separate product and can be queried independently. QR2 is excluded from the default workflow because DR1 + QR3 supersede it for new work.

## Candidate labels

- `KNOWN_CATALOG_MATCH`: position matches an enabled catalog within the configured tolerance.
- `PROPER_MOTION_SHIFT`: epoch-propagated catalog position and observed position show statistically significant displacement, with uncertainty support.
- `NEW_CANDIDATE`: a high-SNR detection not matched to the checked catalogs; it is not a confirmed discovery.
- `INSUFFICIENT_EVIDENCE`: data quality, epoch count, SNR or catalog coverage is inadequate.

A non-match is never proof of novelty. Require multiple epochs, artifact checks, WCS validation, and human review before promoting a candidate.

## Implemented modules vs remaining work

Implemented: FITS MEF inspection, Level-2 masking, ZODI subtraction, optional solid-angle conversion, SEP background/source extraction, reprojection helpers, SIA2 collection fan-out, cloud_access parsing, channel indexing, and basic epoch-aware catalog matching utilities.

Remaining: live cutout retrieval with bounded retries/cache, official calibration discovery and version matching, release-aware header validation, calibrated spectral extraction, robust difference imaging, Gaia/WISE TAP adapters and uncertainty propagation, complete provenance ledger, and frontend integration.
