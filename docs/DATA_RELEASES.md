# SPHEREx Data Release Registry

**SimpleSpace baseline: DR1 + QR3. QR2 is excluded from new default searches.**

The official IRSA archive documentation (2026-11-12) states that DR1 contains Survey 1 and 2 reprocessed with the same improved pipeline/calibrations as QR3; QR3 contains Survey 3 and 4. DR1 also includes the All-Sky Cube.

| Product | SIA2 collection | Use |
|---|---|---|
| DR1 Wide Spectral Images | `spherex_dr1` | All-sky Level-2 MEFs |
| DR1 Deep Spectral Images | `spherex_dr1_deep` | Deep field MEFs |
| QR3 Wide Spectral Images | `spherex_qr3` | Current survey Level-2 MEFs |
| QR3 Deep Spectral Images | `spherex_qr3_deep` | Deep field MEFs |
| DR1 All-Sky Cube | `spherex_dr1_cube` | Separate 102-channel cube product |

QR2 data are no longer searchable through SIA2 and remain available for direct download through February 2027. They are not part of the default SimpleSpace search path.

Weekly ingestion means SIA2 can lag new archive files by about one day. Record query timestamp, collection, release, product URI and DOI in the provenance record.
