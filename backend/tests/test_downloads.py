import pytest
from app.services.downloads import build_cutout_url
def test_cutout_url_adds_center_and_size_without_losing_query():
 url=build_cutout_url("https://irsa.ipac.caltech.edu/ibe/data/spherex/dr1/file.fits?foo=bar",150.0,2.0,0.1)
 assert "foo=bar" in url and "center=150.00000000%2C2.00000000" in url and "size=0.10000" in url
def test_cutout_url_rejects_untrusted_hosts():
 with pytest.raises(ValueError):build_cutout_url("https://example.com/file.fits",1,2,0.1)
def test_cutout_url_rejects_oversized_cutout():
 with pytest.raises(ValueError):build_cutout_url("https://irsa.ipac.caltech.edu/file.fits",1,2,1.0)
