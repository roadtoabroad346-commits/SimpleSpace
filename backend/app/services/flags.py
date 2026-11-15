from __future__ import annotations
from dataclasses import dataclass
import numpy as np

# SPHEREx Level-2 FLAGS are unsigned 32-bit bit fields.
PIXEL_FLAG_BITS = {"TRANSIENT":0,"OVERFLOW":1,"SUR_ERROR":2,"NONFUNC":6,"DICHROIC":7,"MISSING_DATA":9,"HOT":10,"COLD":11,"FULLSAMPLE":12,"PHANMISS":14,"NONLINEAR":15,"PERSIST":17,"OUTLIER":19,"CROSSTALK":20,"SOURCE":21,"GHOST":22,"GHOST_FPA":23,"GHOST_EXT":24,"STREAK":25,"BLOOM":26,"SNOWBALL":27,"HALO":28,"SATELLITE_HALO":29}
STRICT_BAD_BITS=(0,1,2,6,7,9,10,11,12,14,15,17,19,20,22,23,24,25,26,27,28,29)
CRITICAL_BAD_MASK=np.uint32(sum(1<<b for b in STRICT_BAD_BITS))
SOURCE_MASK=np.uint32(1<<21)
CONTAINS_BAD_PIXEL_BIT=32
FIT_ERROR_BIT=33

def as_uint32_flags(flags):
    a=np.asarray(flags)
    if a.dtype.kind not in "ui" or a.dtype.itemsize!=4: raise ValueError("Level-2 FLAGS must be 32-bit integers.")
    return a.view(np.uint32) if a.dtype.kind=="i" else a.astype(np.uint32,copy=False)

@dataclass(frozen=True)
class MaskResult:
    image: np.ndarray
    variance: np.ndarray|None
    bad_pixel_mask: np.ndarray
    masked_count: int
    total_count: int
    retained_source_flag_count: int

def mask_level2_pixels(image,flags,variance=None,bad_mask=int(CRITICAL_BAD_MASK)):
    data=np.asarray(image,dtype=np.float32).copy()
    bits=as_uint32_flags(flags)
    if data.shape!=bits.shape: raise ValueError("IMAGE and FLAGS shapes must match.")
    if variance is not None and np.shape(variance)!=data.shape: raise ValueError("VARIANCE and IMAGE shapes must match.")
    bad=((bits & np.uint32(bad_mask))!=0)|~np.isfinite(data)
    var=None if variance is None else np.asarray(variance,dtype=np.float32).copy()
    if var is not None:
        bad |= ~np.isfinite(var)|(var<0)
        var[bad]=np.nan
    data[bad]=np.nan
    return MaskResult(data,var,bad,int(bad.sum()),int(data.size),int(np.count_nonzero(bits & SOURCE_MASK)))

def reject_l3_photometry_points(flux,flags):
    values=np.asarray(flux,dtype=float); bits=np.asarray(flags)
    if bits.shape!=values.shape or bits.dtype.kind not in "ui" or bits.dtype.itemsize!=8: raise ValueError("L3 flags must be aligned uint64 values.")
    bits=bits.view(np.uint64) if bits.dtype.kind=="i" else bits.astype(np.uint64,copy=False)
    rejected=(np.uint64(1)<<32)|(np.uint64(1)<<33)
    return np.isfinite(values)&((bits&rejected)==0)
