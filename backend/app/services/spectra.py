from __future__ import annotations
import numpy as np
from app.services.flags import reject_l3_photometry_points

def aperture_photometry(image,x,y,variance=None,radii=(3.0,4.0,5.0)):
    try:import sep
    except ImportError as exc:raise RuntimeError("SEP is required for aperture photometry.") from exc
    data=np.asarray(image,dtype=np.float32).astype(np.dtype("=f4"),copy=True)
    mask=~np.isfinite(data)
    err=None
    if variance is not None:
        var=np.asarray(variance,dtype=float)
        if var.shape!=data.shape:raise ValueError("Variance map must match image shape.")
        err=np.sqrt(np.where(np.isfinite(var)&(var>0),var,np.nan)).astype(np.float32)
        mask |= ~np.isfinite(err)
    measurements=[]
    for radius in radii:
        flux,flux_error,flags=sep.sum_circle(data,np.asarray(x,dtype=float),np.asarray(y,dtype=float),float(radius),err=err,mask=mask,subpix=5)
        measurements.append({"radius_px":float(radius),"flux":np.asarray(flux),"flux_error":np.asarray(flux_error),"sep_flags":np.asarray(flags)})
    return measurements

def build_spectrum_points(wavelength_um,bandwidth_um,flux_ujy,variance_ujy2,photometry_flags):
    wave=np.asarray(wavelength_um,dtype=float);band=np.asarray(bandwidth_um,dtype=float)
    flux=np.asarray(flux_ujy,dtype=float);variance=np.asarray(variance_ujy2,dtype=float);flags=np.asarray(photometry_flags)
    if not (wave.shape==band.shape==flux.shape==variance.shape==flags.shape):raise ValueError("All spectrum arrays must have identical shapes.")
    valid=reject_l3_photometry_points(flux,flags)&np.isfinite(wave)&(wave>=0.75)&(wave<=5.0)&np.isfinite(band)&(band>0)&np.isfinite(variance)&(variance>=0)
    points=[]
    for i in np.flatnonzero(valid):
        value=float(flux[i]);ab=float(23.9-2.5*np.log10(value)) if value>0 else None
        points.append({"wavelength_um":float(wave[i]),"bandwidth_um":float(band[i]),"flux_ujy":value,"flux_error_ujy":float(np.sqrt(variance[i])),"ab_magnitude":ab,"photometry_flags":int(flags[i])})
    return sorted(points,key=lambda p:p["wavelength_um"])
