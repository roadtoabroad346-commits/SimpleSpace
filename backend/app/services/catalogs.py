from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from astropy import units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord
from astropy.table import Table
@dataclass(frozen=True)
class MatchResult:
    matched:bool
    separation_arcsec:float|None
    catalog_name:str|None
    catalog_index:int|None
def match_catalog(ra_deg,dec_deg,catalog:Table,catalog_name,radius_arcsec=2.0,epoch_mjd=None,catalog_epoch_jyear=None):
    if len(catalog)==0:return MatchResult(False,None,None,None)
    if not {"ra","dec"}.issubset(catalog.colnames):raise ValueError(f"{catalog_name} requires ra and dec.")
    ra=np.asarray(catalog["ra"],dtype=float).copy();dec=np.asarray(catalog["dec"],dtype=float).copy()
    valid=np.isfinite(ra)&np.isfinite(dec)
    if not valid.any():return MatchResult(False,None,None,None)
    if epoch_mjd is not None and catalog_epoch_jyear is not None and {"pmra","pmdec"}.issubset(catalog.colnames):
        pmra=np.asarray(catalog["pmra"],dtype=float);pmdec=np.asarray(catalog["pmdec"],dtype=float)
        moving=valid&np.isfinite(pmra)&np.isfinite(pmdec)
        if moving.any():
            propagated=SkyCoord(ra=ra[moving]*u.deg,dec=dec[moving]*u.deg,pm_ra_cosdec=pmra[moving]*u.mas/u.yr,pm_dec=pmdec[moving]*u.mas/u.yr,obstime=Time(catalog_epoch_jyear,format="jyear")).apply_space_motion(new_obstime=Time(epoch_mjd,format="mjd"))
            ra[moving]=propagated.ra.deg;dec[moving]=propagated.dec.deg
    cat=SkyCoord(ra=ra[valid]*u.deg,dec=dec[valid]*u.deg,frame="icrs")
    target=SkyCoord(ra=ra_deg*u.deg,dec=dec_deg*u.deg,frame="icrs")
    idx,sep,_=target.match_to_catalog_sky(cat);arcsec=float(sep.arcsec)
    source_idx=int(np.flatnonzero(valid)[int(idx)])
    return MatchResult(arcsec<=radius_arcsec,arcsec,catalog_name if arcsec<=radius_arcsec else None,source_idx if arcsec<=radius_arcsec else None)
def classify_candidate(snr,gaia,allwise,catwise,motion_significance=None):
    if motion_significance is not None and motion_significance>3:return "PROPER_MOTION_SHIFT"
    if any(m.matched for m in (gaia,allwise,catwise)):return "KNOWN_CATALOG_MATCH"
    if np.isfinite(snr) and snr>5:return "NEW_CANDIDATE"
    return "INSUFFICIENT_EVIDENCE"
def extract_sources(image,threshold=5.0,min_area=5):
    try:import sep
    except ImportError as exc:raise RuntimeError("SEP is required for source extraction.") from exc
    data=np.asarray(image,dtype=np.float32).astype(np.dtype("=f4"),copy=True);mask=~np.isfinite(data)
    if mask.all():return []
    bg=sep.Background(data,mask=mask,bw=64,bh=64,fw=11,fh=11)
    objects=sep.extract(data-bg.back(),threshold,err=np.asarray(bg.rms(),dtype=np.float32),mask=mask,minarea=min_area)
    result=[]
    for n,obj in enumerate(objects,1):
        flux=float(obj["flux"]);err=float(obj["fluxerr"])
        result.append({"number":n,"x":float(obj["x"]),"y":float(obj["y"]),"flux":flux,"flux_error":err,"snr":flux/err if err>0 else None})
    return result
