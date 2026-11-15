import numpy as np
import pytest
from io import BytesIO
from astropy.io import fits
from app.services.flags import mask_level2_pixels,reject_l3_photometry_points
from app.services.processing import process_level2_mef
from app.services.spectral import global_channel_id,detector_subchannel

def test_strict_flags_mask_and_source_retained():
 r=mask_level2_pixels(np.ones((1,4)),np.array([[1,1<<10,1<<21,0]],dtype=np.uint32))
 assert np.isnan(r.image[0,0]) and np.isnan(r.image[0,1])
 assert r.image[0,2]==1 and r.retained_source_flag_count==1

def test_signed_flags_preserve_raw_bit_pattern():
 r=mask_level2_pixels(np.ones((1,1)),np.array([[-2147483647]],dtype=np.int32))
 assert np.isnan(r.image[0,0])

def test_variance_invalidity_masks_image_and_variance():
 r=mask_level2_pixels(np.ones((1,2)),np.zeros((1,2),dtype=np.uint32),np.array([[1.,-1.]]))
 assert np.isnan(r.image[0,1]) and np.isnan(r.variance[0,1])

def test_l3_flags_are_uint64_and_separate():
 assert reject_l3_photometry_points([1.,2.,3.],np.array([0,1<<32,1<<33],dtype=np.uint64)).tolist()==[True,False,False]

def test_nominal_channels_are_six_times_seventeen():
 assert global_channel_id(6,17)==102 and detector_subchannel(52)==(4,1)
 with pytest.raises(ValueError):global_channel_id(1,18)

def test_mef_processing_subtracts_zodi_and_masks():
 hdus=fits.HDUList([fits.PrimaryHDU(),fits.ImageHDU(data=np.full((4,4),10.,dtype=np.float32),name="IMAGE"),fits.ImageHDU(data=np.zeros((4,4),dtype=np.uint32),name="FLAGS"),fits.ImageHDU(data=np.ones((4,4),dtype=np.float32)*2,name="ZODI")])
 hdus[1].header.update({"CTYPE1":"RA---TAN","CTYPE2":"DEC--TAN","CRPIX1":2.5,"CRPIX2":2.5,"CRVAL1":10.,"CRVAL2":20.,"CDELT1":-0.001,"CDELT2":0.001})
 hdus["FLAGS"].data[0,0]=1
 b=BytesIO();hdus.writeto(b)
 result=process_level2_mef(b.getvalue())
 assert result.image_unit=="MJy/sr" and np.isnan(result.image[0,0]) and result.image[1,1]==8.
