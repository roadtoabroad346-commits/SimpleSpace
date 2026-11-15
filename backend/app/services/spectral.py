import numpy as np
from astropy.coordinates import SkyCoord
from astropy.wcs import WCS

def global_channel_id(detector:int,subchannel:int)->int:
    if detector not in range(1,7) or subchannel not in range(1,18): raise ValueError("Detector must be 1..6 and subchannel 1..17.")
    return (detector-1)*17+subchannel

def detector_subchannel(channel_id:int)->tuple[int,int]:
    if channel_id not in range(1,103): raise ValueError("Channel must be 1..102.")
    return ((channel_id-1)//17+1,(channel_id-1)%17+1)

def pixel_for_sky_coordinate(header,ra_deg,dec_deg):
    x,y=WCS(header).world_to_pixel(SkyCoord(ra=ra_deg,dec=dec_deg,unit="deg",frame="icrs"))
    if not np.isfinite(x) or not np.isfinite(y): raise ValueError("Coordinate maps to invalid detector pixels.")
    return float(x),float(y)

def wavelength_from_calibration(hdul,x_pixel,y_pixel):
    # Official precision-science products are CWAVE/CBAND; WCS-WAVE is a visualization lookup.
    if not {"CWAVE","CBAND"}.issubset({str(h.header.get("EXTNAME","")).upper() for h in hdul}):
        raise ValueError("CWAVE and CBAND calibration extensions are required for scientific wavelength values.")
    wave=np.asarray(hdul["CWAVE"].data,dtype=float); band=np.asarray(hdul["CBAND"].data,dtype=float)
    x,y=int(round(x_pixel)),int(round(y_pixel))
    if wave.shape!=band.shape or wave.ndim!=2 or not (0<=y<wave.shape[0] and 0<=x<wave.shape[1]): raise ValueError("Calibration map shape or pixel coordinates are invalid.")
    wl,bw=float(wave[y,x]),float(band[y,x])
    if not np.isfinite(wl) or not np.isfinite(bw) or not 0.75<=wl<=5.0 or bw<=0: raise ValueError("No valid calibrated wavelength at this pixel.")
    return wl,bw
