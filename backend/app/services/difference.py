from __future__ import annotations
import numpy as np

def difference_images(first,second,variance_first=None,variance_second=None):
    """Return second-first, propagated independent variance, and SNR significance."""
    a=np.asarray(first,dtype=float);b=np.asarray(second,dtype=float)
    if a.shape!=b.shape:raise ValueError("Difference images must share a common reprojection grid.")
    valid=np.isfinite(a)&np.isfinite(b);difference=np.full(a.shape,np.nan,dtype=float)
    difference[valid]=b[valid]-a[valid]
    propagated=None;significance=None
    if variance_first is not None or variance_second is not None:
        if variance_first is None or variance_second is None:raise ValueError("Both variance maps are required for variance propagation.")
        va=np.asarray(variance_first,dtype=float);vb=np.asarray(variance_second,dtype=float)
        if va.shape!=a.shape or vb.shape!=a.shape:raise ValueError("Variance maps must match the image shapes.")
        propagated=va+vb;valid_var=valid&np.isfinite(propagated)&(propagated>0)
        significance=np.full(a.shape,np.nan,dtype=float)
        significance[valid_var]=difference[valid_var]/np.sqrt(propagated[valid_var])
    return difference,propagated,significance
