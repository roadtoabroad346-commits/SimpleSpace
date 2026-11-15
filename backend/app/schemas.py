from pydantic import BaseModel,Field,field_validator
class HealthResponse(BaseModel):
    status:str="ok"
    service:str="simplespace-api"
class ArchiveSearchRequest(BaseModel):
    ra:float=Field(ge=0,lt=360)
    dec:float=Field(ge=-90,le=90)
    radius_deg:float=Field(default=0.1,gt=0,le=1.0)
    limit:int=Field(default=50,ge=1,le=100)
    @field_validator("ra","dec","radius_deg")
    @classmethod
    def finite_numbers(cls,value:float)->float:
        if value!=value or value in (float("inf"),float("-inf")):raise ValueError("Coordinates must be finite.")
        return value
class CutoutRequest(BaseModel):
    access_url:str
    ra:float=Field(ge=0,lt=360)
    dec:float=Field(ge=-90,le=90)
    size_deg:float=Field(default=0.1,ge=0.01,le=0.5)
class CatalogCrossmatchRequest(BaseModel):
    ra:float=Field(ge=0,lt=360)
    dec:float=Field(ge=-90,le=90)
    radius_deg:float=Field(default=0.01,gt=0,le=1.0)
    epoch_mjd:float|None=None
    snr:float=0.0
    motion_significance:float|None=None
class ArchiveObservation(BaseModel):
    ra_deg:float|None=None
    dec_deg:float|None=None
    obs_id:str|None=None
    obs_collection:str|None=None
    t_min:float|None=None
    t_max:float|None=None
    em_min:float|None=None
    em_max:float|None=None
    access_url:str|None=None
class ArchiveSearchResponse(BaseModel):
    source:str
    table:str
    count:int
    observations:list[ArchiveObservation]
    note:str
class FITSInspectionResponse(BaseModel):
    extensions:list[str]
    image_shape:list[int]
    flags_present:bool
    variance_present:bool
    wavelength_wcs_present:bool
    sky_wcs_present:bool
    finite_pixel_fraction:float
    nonzero_flag_values:list[int]
    warnings:list[str]
