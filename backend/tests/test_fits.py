from io import BytesIO

import numpy as np
import pytest
from astropy.io import fits

from app.services.fits import inspect_fits, render_preview_png


def make_mef(flags_shape: tuple[int, int] = (8, 8)) -> bytes:
    image = np.arange(64, dtype=np.float32).reshape(8, 8)
    flags = np.zeros(flags_shape, dtype=np.uint16)
    if flags.size:
        flags.flat[0] = 4
    variance = np.ones((8, 8), dtype=np.float32)
    primary = fits.PrimaryHDU()
    image_hdu = fits.ImageHDU(data=image, name="IMAGE")
    image_hdu.header["CTYPE1"] = "RA---TAN"
    image_hdu.header["CTYPE2"] = "DEC--TAN"
    hdus = fits.HDUList([
        primary,
        image_hdu,
        fits.ImageHDU(data=flags, name="FLAGS"),
        fits.ImageHDU(data=variance, name="VARIANCE"),
        fits.ImageHDU(data=np.ones((2, 2), dtype=np.float32), name="WCS-WAVE"),
    ])
    buffer = BytesIO()
    hdus.writeto(buffer)
    return buffer.getvalue()


def test_inspection_finds_extensions_without_assuming_hdu_numbers() -> None:
    result = inspect_fits(make_mef())
    assert "IMAGE" in result["extensions"]
    assert "FLAGS" in result["extensions"]
    assert result["flags_present"] is True
    assert result["variance_present"] is True
    assert result["wavelength_wcs_present"] is True
    assert result["sky_wcs_present"] is True
    assert result["image_shape"] == [8, 8]


def test_nonzero_flags_are_preserved_without_assigning_meaning() -> None:
    result = inspect_fits(make_mef())
    assert result["nonzero_flag_values"] == [4]
    assert not any("bad pixel" in warning.lower() for warning in result["warnings"])


def test_shape_mismatch_is_reported_not_silently_applied() -> None:
    result = inspect_fits(make_mef(flags_shape=(4, 4)))
    assert any("FLAGS shape does not match IMAGE" in warning for warning in result["warnings"])


def test_preview_is_a_png() -> None:
    result = render_preview_png(make_mef())
    assert result.startswith(b"\x89PNG\r\n\x1a\n")


def test_invalid_fits_is_rejected() -> None:
    with pytest.raises(ValueError, match="readable FITS"):
        inspect_fits(b"not a fits file")
