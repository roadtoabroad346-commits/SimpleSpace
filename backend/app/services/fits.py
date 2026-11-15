from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO

import numpy as np
from astropy.io import fits
from PIL import Image


@dataclass(frozen=True)
class FitsInspection:
    extensions: list[str]
    image_shape: list[int]
    flags_present: bool
    variance_present: bool
    wavelength_wcs_present: bool
    sky_wcs_present: bool
    finite_pixel_fraction: float
    nonzero_flag_values: list[int]
    warnings: list[str]


def _extension_map(hdul: fits.HDUList) -> dict[str, fits.hdu.base.ExtensionHDU]:
    result: dict[str, fits.hdu.base.ExtensionHDU] = {}
    for hdu in hdul:
        name = str(hdu.header.get("EXTNAME", "")).strip().upper()
        if name and name not in result:
            result[name] = hdu
    return result


def _open_image(payload: bytes) -> tuple[np.ndarray, dict[str, fits.hdu.base.ExtensionHDU], fits.Header]:
    if not payload:
        raise ValueError("The uploaded FITS file is empty.")
    try:
        hdul = fits.open(BytesIO(payload), memmap=False, checksum=True)
    except Exception as exc:
        raise ValueError("The upload is not a readable FITS file.") from exc

    with hdul:
        extensions = _extension_map(hdul)
        image_hdu = extensions.get("IMAGE")
        if image_hdu is None:
            # A primary image is accepted only as a generic FITS image, not
            # silently treated as a complete SPHEREx MEF product.
            if hdul[0].data is None:
                raise ValueError("FITS file has no IMAGE extension or primary image.")
            image_hdu = hdul[0]
        if image_hdu.data is None:
            raise ValueError("IMAGE extension contains no pixel data.")
        image = np.asarray(image_hdu.data, dtype=np.float32)
        if image.ndim != 2:
            raise ValueError("Only two-dimensional image planes are supported.")
        header = image_hdu.header.copy()
        # Copy arrays before the HDUList closes.
        copied: dict[str, fits.hdu.base.ExtensionHDU] = {}
        for name, hdu in extensions.items():
            clone = fits.ImageHDU(data=np.array(hdu.data, copy=True), header=hdu.header.copy(), name=name) if hdu.data is not None else fits.ImageHDU(name=name)
            copied[name] = clone
        return image, copied, header


def inspect_fits(payload: bytes) -> FitsInspection:
    image, extensions, image_header = _open_image(payload)
    warnings: list[str] = []
    finite = np.isfinite(image)
    finite_fraction = float(finite.mean()) if image.size else 0.0

    flags_hdu = extensions.get("FLAGS")
    variance_hdu = extensions.get("VARIANCE")
    if flags_hdu is not None and flags_hdu.data is not None:
        flags = np.asarray(flags_hdu.data)
        if flags.shape != image.shape:
            warnings.append("FLAGS shape does not match IMAGE; no pixel-level flag interpretation was attempted.")
            flag_values: list[int] = []
        else:
            # Preserve bit patterns for release-aware decoding downstream.
            # Non-zero bits are reported, never guessed to mean 'bad pixel'.
            unique = np.unique(flags)
            flag_values = [int(value) for value in unique if int(value) != 0][:32]
    else:
        flag_values = []
        warnings.append("FLAGS extension is absent; pixel-quality status is unknown.")

    if variance_hdu is not None and variance_hdu.data is not None:
        if np.asarray(variance_hdu.data).shape != image.shape:
            warnings.append("VARIANCE shape does not match IMAGE.")

    if "WCS-WAVE" not in extensions:
        warnings.append("WCS-WAVE extension is absent; wavelength mapping is unavailable.")
    if not (image_header.get("CTYPE1") and image_header.get("CTYPE2")):
        warnings.append("IMAGE header does not expose a complete two-axis sky WCS.")

    return FitsInspection(
        extensions=sorted(extensions.keys()),
        image_shape=[int(image.shape[0]), int(image.shape[1])],
        flags_present=flags_hdu is not None,
        variance_present=variance_hdu is not None,
        wavelength_wcs_present="WCS-WAVE" in extensions,
        sky_wcs_present=bool(image_header.get("CTYPE1") and image_header.get("CTYPE2")),
        finite_pixel_fraction=finite_fraction,
        nonzero_flag_values=flag_values,
        warnings=warnings,
    )


def render_preview_png(payload: bytes) -> bytes:
    image, _, _ = _open_image(payload)
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
    Image.fromarray(pixels, mode="L").save(output, format="PNG", optimize=True)
    return output.getvalue()
