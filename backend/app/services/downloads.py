from __future__ import annotations
from io import BytesIO
import time
from urllib.parse import parse_qsl,urlencode,urlsplit,urlunsplit
import httpx
from astropy.io import fits
from app.services.archive import validate_archive_url

class CutoutUnavailable(RuntimeError):
    """Raised when IRSA cannot provide a valid cutout after bounded retries."""

def build_cutout_url(access_url:str,ra:float,dec:float,size_deg:float)->str:
    validate_archive_url(access_url)
    parts=urlsplit(access_url)
    if parts.scheme!="https" or parts.hostname!="irsa.ipac.caltech.edu":
        raise ValueError("IRSA cutouts require an allow-listed on-premises access_url.")
    if not 0.01<=size_deg<=0.5:raise ValueError("Cutout size must be between 0.01 and 0.5 degrees.")
    params=dict(parse_qsl(parts.query,keep_blank_values=True))
    params.update({"center":f"{ra:.8f},{dec:.8f}","size":f"{size_deg:.5f}"})
    return urlunsplit((parts.scheme,parts.netloc,parts.path,urlencode(params),parts.fragment))

def _validate_mef(payload:bytes)->None:
    try:
        with fits.open(BytesIO(payload),memmap=False,checksum=True) as hdul:
            names={str(h.header.get("EXTNAME","")).upper() for h in hdul}
            required={"IMAGE","FLAGS","ZODI"}
            if not required.issubset(names):raise ValueError("Cutout MEF is missing IMAGE, FLAGS or ZODI.")
            for hdu in hdul:
                if hdu.data is not None:
                    _=hdu.data.shape
    except Exception as exc:
        raise ValueError("IRSA response is not a valid SPHEREx Level-2 MEF.") from exc

def download_cutout(access_url:str,ra:float,dec:float,size_deg:float,max_bytes:int=50*1024*1024,retries:int=3)->bytes:
    url=build_cutout_url(access_url,ra,dec,size_deg)
    last_error=None
    timeout=httpx.Timeout(120.0,connect=20.0)
    for attempt in range(retries):
        try:
            with httpx.Client(timeout=timeout,follow_redirects=True) as client:
                with client.stream("GET",url) as response:
                    response.raise_for_status()
                    final_url=str(response.url)
                    validate_archive_url(final_url)
                    chunks=[];total=0
                    for chunk in response.iter_bytes():
                        total+=len(chunk)
                        if total>max_bytes:raise ValueError("IRSA cutout exceeds the configured download limit.")
                        chunks.append(chunk)
                    payload=b"".join(chunks)
            _validate_mef(payload)
            return payload
        except ValueError:
            raise
        except (httpx.HTTPError,OSError,TimeoutError) as exc:
            last_error=exc
            if attempt+1<retries:time.sleep(2**attempt)
    raise CutoutUnavailable(f"IRSA cutout download failed after {retries} attempts: {type(last_error).__name__ if last_error else 'unknown error'}")
