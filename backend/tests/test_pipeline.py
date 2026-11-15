import numpy as np
import pytest
from app.services.flags import mask_level2_pixels,reject_l3_photometry_points
from app.services.spectral import global_channel_id,detector_subchannel

def test_strict_flags_mask_and_source_retained():
    result=mask_level2_pixels(np.ones((1,4)),np.array([[1,1<<10,1<<21,0]],dtype=np.uint32))
    assert np.isnan(result.image[0,0]) and np.isnan(result.image[0,1])
    assert result.image[0,2]==1 and result.retained_source_flag_count==1

def test_signed_flags_retain_raw_bit_pattern():
    result=mask_level2_pixels(np.ones((1,1)),np.array([[-2147483648]],dtype=np.int32))
    assert np.isnan(result.image[0,0])

def test_variance_invalidity_masks_image_and_variance():
    result=mask_level2_pixels(np.ones((1,2)),np.zeros((1,2),dtype=np.uint32),np.array([[1.,-1.]]))
    assert np.isnan(result.image[0,1]) and np.isnan(result.variance[0,1])

def test_l3_flags_are_uint64_and_separate():
    flags=np.array([0,1<<32,1<<33],dtype=np.uint64)
    assert reject_l3_photometry_points([1.,2.,3.],flags).tolist()==[True,False,False]

def test_nominal_channels_are_six_detectors_times_seventeen_subchannels():
    assert global_channel_id(6,17)==102
    assert detector_subchannel(52)==(4,1)
    with pytest.raises(ValueError): global_channel_id(1,18)
