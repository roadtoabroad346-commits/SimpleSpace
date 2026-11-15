import numpy as np
import pytest
from app.services.difference import difference_images
from app.services.spectra import build_spectrum_points

def test_difference_image_and_variance_propagation():
 d,v,s=difference_images(np.array([1.,2.]),np.array([3.,1.]),np.array([1.,4.]),np.array([3.,5.]))
 assert d.tolist()==[2.,-1.]
 assert v.tolist()==[4.,9.]
 assert np.allclose(s,[1.,-1/3])

def test_difference_rejects_mismatched_grids():
 with pytest.raises(ValueError):difference_images(np.ones((2,2)),np.ones((3,3)))

def test_spectrum_rejects_l3_bad_pixel_and_fit_error():
 points=build_spectrum_points([1.,2.,3.],[.01,.02,.03],[10.,20.,30.],[1.,4.,9.],np.array([0,1<<32,1<<33],dtype=np.uint64))
 assert len(points)==1 and points[0]["wavelength_um"]==1.
 assert points[0]["ab_magnitude"] is not None

def test_spectrum_keeps_negative_flux_but_omits_ab_magnitude():
 points=build_spectrum_points([.5,1.,2.],[.01,.01,.01],[-1.,0.,2.],[1.,1.,1.],np.zeros(3,dtype=np.uint64))
 assert len(points)==2
 assert points[0]["ab_magnitude"] is None
 assert points[1]["ab_magnitude"] is not None
