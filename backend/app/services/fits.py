from __future__ import annotations

from io import BytesIO

import numpy as np
from astropy.io import fits
from astropy.io.fits import Header
from PIL import Image


def _read_mef(payload: bytes) -> tuple[np.ndarray, dict[str, np.ndarray | None], Header]:
    if not payload:
        raise ValueError("The uploaded FITS file is empty.")
    try:
        hdul = fits.open(BytesIO(payload), memmap=False, checksum=True)
    except Exception as exc:
        raise ValueError("The upload is not a readable FITS file.") from exc

    with hdul:
        extensions: dict[str, np.ndarray | None] = {}
        image_hdu = None
        for hdu in hdul:
            name = str(hdu.header.get("EXTNAME", "")).strip().upper()
            if name:
                extensions.setdefault(name, None if hdu.data is None else np.array(hdu.data, copy=True))
                if name == "IMAGE" and image_hdu is None:
                    image_hdu = hdu

        # Accept a primary image for generic FITS inspection, but don't pretend
        # that it is a full SPHEREx MEF product.
        if image_hdu is None:
            if hdul[0].data is None:
                raise ValueError("FITS file has no IMAGE extension or primary image.")
            image_data = np.array(hdul[0].data, copy=True)
            image_header = hdul[0].header.copy()
        else:
            if image_hdu.data is None:
                raise ValueError("IMAGE extension contains no pixel data.")
            image_data = np.array(image_hdu.data, copy=True)
            image_header = image_hdu.header.copy()

    image = np.asarray(image_data, dtype=np.float32)
    if image.ndim != 2:
        raise ValueError("Only two-dimensional image planes are supported.")
    return image, extensions, image_header


def inspect_fits(payload: bytes) -> dict:
    image, extensions, image_header = _read_mef(payload)
    warnings: list[str] = []
    finite = np.isfinite(image)
    finite_fraction = float(finite.mean()) if image.size else 0.0

    flags = extensions.get("FLAGS")
    variance = extensions.get("VARIANCE")
    if flags is not None:
        if flags.shape != image.shape:
            warnings.append("FLAGS shape does not match IMAGE; no pixel-level flag interpretation was attempted.")
            flag_values: list[int] = []
        else:
            # Preserve observed bit patterns; never guess their release-specific meaning.
            unique = np.unique(flags)
            flag_values = [int(value) for value in unique if int(value) != 0][:32]
    else:
        flag_values = []
        warnings.append("FLAGS extension is absent; pixel-quality status is unknown.")

    if variance is not None and variance.shape != image.shape:
        warnings.append("VARIANCE shape does not match IMAGE.")
    if "WCS-WAVE" not in extensions:
        warnings.append("WCS-WAVE extension is absent; wavelength mapping is unavailable.")
    sky_wcs = bool(image_header.get("CTYPE1") and image_header.get("CTYPE2"))
    if not sky_wcs:
        warnings.append("IMAGE header does not expose a complete two-axis sky WCS.")

    return {
        "extensions": sorted(extensions.keys()),
        "image_shape": [int(image.shape[0]), int(image.shape[1])],
        "flags_present": flags is not None,
        "variance_present": variance is not None,
        "wavelength_wcs_present": "WCS-WAVE" in extensions,
        "sky_wcs_present": sky_wcs,
        "finite_pixel_fraction": finite_fraction,
        "nonzero_flag_values": flag_values,
        "warnings": warnings,
    }


def render_preview_png(payload: bytes) -> bytes:
    image, _, _ = _read_mef(payload)
    finite = np.isfinite(image)
    if not finite.any():
        raise ValueError("IMAGE contains no finite pixels to preview.")

    low, high = np.nanpercentile(image, [1, 99])
    if not np.isfinite(low) or not np.isfinite(high) or high <= low:
        pixels = np.zeros(image.shape, dtype=np.uint8)
    else:
        scaled = np.clip((image - low) / (high - low), 0.0, 1.0)
        scaled[~finite] = 0.0
        pixels = np.asarray(scaled * 255.0, dtype=np.uint8)

    output = BytesIO()
    Image.fromarray(pixels).save(output, format="PNG", optimize=True)
    return output.getvalue()
