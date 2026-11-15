from __future__ import annotations
from dataclasses import dataclass
from io import BytesIO
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from app.services.flags import MaskResult,mask_level2_pixels

@dataclass(frozen=True)
class ProcessedFrame:
    image: np.ndarray
    image_unit: str
    variance: np.ndarray|None
    flags: np.ndarray
    wcs: WCS
    detector: int|None
    observation_id: str|None
    mjd_obs: float|None
    mask: MaskResult

def _copy_hdu_data(hdul,name,required=False):
    try:h=hdul[name]
    except (KeyError,IndexError):
        if required:raise ValueError(f"Required extension {name} is missing.")
        return None,None
    if h.data is None:
        if required:raise ValueError(f"Extension {name} has no data.")
        return None,h.header
    return np.array(h.data,copy=True),h.header

def process_level2_mef(payload:bytes,solid_angle_sr=None)->ProcessedFrame:
    if not payload:raise ValueError("FITS payload is empty.")
    try:hdul=fits.open(BytesIO(payload),memmap=False,checksum=True)
    except Exception as exc:raise ValueError("Unable to read FITS MEF.") from exc
    with hdul:
        image,header=_copy_hdu_data(hdul,"IMAGE",True);flags,_=_copy_hdu_data(hdul,"FLAGS",True);zodi,_=_copy_hdu_data(hdul,"ZODI",True);variance,_=_copy_hdu_data(hdul,"VARIANCE")
        if image.ndim!=2:raise ValueError("Level-2 IMAGE must be 2D.")
        if flags.shape!=image.shape or zodi.shape!=image.shape:raise ValueError("IMAGE, FLAGS and ZODI shapes must match.")
        if variance is not None and variance.shape!=image.shape:raise ValueError("VARIANCE shape does not match IMAGE.")
        cleaned=np.asarray(image,dtype=np.float32)-np.asarray(zodi,dtype=np.float32)
        mask=mask_level2_pixels(cleaned,flags,variance);output=mask.image.astype(np.float64);outvar=mask.variance;unit="MJy/sr"
        if solid_angle_sr is not None:
            omega=np.asarray(solid_angle_sr,dtype=float)
            if omega.shape!=output.shape:raise ValueError("Solid-angle map shape does not match IMAGE.")
            valid=np.isfinite(omega)&(omega>0);output[~valid]=np.nan;output=output*omega*1e12;unit="microJy/pixel"
            if outvar is not None:outvar=outvar.astype(float)*np.square(omega*1e12)
        try:wcs=WCS(header)
        except Exception as exc:raise ValueError("IMAGE contains invalid spatial WCS.") from exc
        det=header.get("DETECTOR");obs=header.get("OBSID") or header.get("OBS_ID");mjd=header.get("MJD-OBS")
        return ProcessedFrame(output,unit,outvar,flags.copy(),wcs,int(det) if det is not None else None,str(obs) if obs is not None else None,float(mjd) if mjd is not None else None,mask)

def estimate_background(image,mask=None):
    try:import sep
    except ImportError as exc:raise RuntimeError("Install SEP to estimate local background.") from exc
    data=np.asarray(image,dtype=np.float32).astype(np.dtype("=f4"),copy=True)
    bg=sep.Background(data,mask=mask,bw=64,bh=64,fw=11,fh=11)
    return bg,data-bg.back()

def reproject_frame(image,input_wcs,output_wcs,shape_out,flags=None):
    try:from reproject import reproject_exact,reproject_interp
    except ImportError as exc:raise RuntimeError("Install reproject to reproject frames.") from exc
    flux,footprint=reproject_exact((np.asarray(image,dtype=float),input_wcs),output_wcs,shape_out=shape_out)
    outflags=None
    if flags is not None:
        outflags,_=reproject_interp((np.asarray(flags,dtype=np.float32),input_wcs),output_wcs,shape_out=shape_out,order="nearest-neighbor")
        outflags=np.where(np.isfinite(outflags),np.rint(outflags),0).astype(np.uint32)
    flux[footprint<=0]=np.nan
    return flux,footprint,outflags
