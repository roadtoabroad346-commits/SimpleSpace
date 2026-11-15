from fastapi import FastAPI,File,HTTPException,UploadFile
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from io import BytesIO
import asyncio
import numpy as np
from PIL import Image
from app.config import get_settings
from app.schemas import ArchiveSearchRequest,ArchiveSearchResponse,HealthResponse,FITSInspectionResponse
from app.services.irsa import ArchiveUnavailable,search_observations
from app.services.fits import inspect_fits,render_preview_png
from app.services.archive import search_spherex_sia
from app.services.processing import process_level2_mef
from app.services.catalogs import extract_sources

settings=get_settings();MAX_FITS_UPLOAD_BYTES=20*1024*1024
app=FastAPI(title="SimpleSpace API",version="0.2.0",description="Scientific data access and processing for SPHEREx observations.")
app.add_middleware(CORSMiddleware,allow_origins=settings.allowed_origins,allow_credentials=False,allow_methods=["GET","POST"],allow_headers=["Content-Type"])

@app.get("/health",response_model=HealthResponse,tags=["system"])
async def health():return HealthResponse()

@app.post("/archive/observations",response_model=ArchiveSearchResponse,tags=["archive"])
async def archive_observations(request:ArchiveSearchRequest):
    try:observations=await search_observations(settings,request)
    except ArchiveUnavailable as exc:raise HTTPException(status_code=503,detail=str(exc)) from exc
    return ArchiveSearchResponse(source="NASA/IPAC IRSA TAP",table=settings.irsa_obscore_table,count=len(observations),observations=observations,note="Metadata only; not a source detection or discovery claim.")

@app.post("/archive/spherex",tags=["archive"])
async def search_spherex(request:ArchiveSearchRequest):
    try:result=await asyncio.wait_for(asyncio.to_thread(search_spherex_sia,request.ra,request.dec,request.radius_deg,settings.collection_names),timeout=settings.irsa_query_timeout_seconds)
    except TimeoutError as exc:raise HTTPException(status_code=504,detail="IRSA SIA2 query timed out.") from exc
    except ValueError as exc:raise HTTPException(status_code=422,detail=str(exc)) from exc
    return {"source":"NASA/IPAC IRSA SIA2","collections":settings.collection_names,**result}

async def _read_fits(file:UploadFile):
    data=await file.read(MAX_FITS_UPLOAD_BYTES+1)
    if len(data)>MAX_FITS_UPLOAD_BYTES:raise HTTPException(status_code=413,detail="FITS upload exceeds 20 MiB.")
    return data

@app.post("/archive/inspect-fits",response_model=FITSInspectionResponse,tags=["fits"])
async def inspect_fits_upload(file:UploadFile=File(...)):
    try:return FITSInspectionResponse(**inspect_fits(await _read_fits(file)))
    except ValueError as exc:raise HTTPException(status_code=422,detail=str(exc)) from exc

@app.post("/archive/preview",tags=["fits"])
async def preview_fits_upload(file:UploadFile=File(...)):
    try:png=render_preview_png(await _read_fits(file))
    except ValueError as exc:raise HTTPException(status_code=422,detail=str(exc)) from exc
    return Response(png,media_type="image/png",headers={"X-Preview-Note":"Display-only stretch; no calibration or FLAGS masking."})

@app.post("/pipeline/process",tags=["pipeline"])
async def process_fits_upload(file:UploadFile=File(...)):
    try:
        frame=process_level2_mef(await _read_fits(file));finite=np.isfinite(frame.image)
        if not finite.any():raise ValueError("No valid pixels remain after quality masking.")
        low,high=np.nanpercentile(frame.image,[1,99])
        scaled=np.zeros(frame.image.shape,dtype=np.uint8) if high<=low else np.asarray(np.clip((frame.image-low)/(high-low),0,1)*255,dtype=np.uint8)
        scaled[~finite]=0;out=BytesIO();Image.fromarray(scaled).save(out,format="PNG",optimize=True)
    except ValueError as exc:raise HTTPException(status_code=422,detail=str(exc)) from exc
    headers={"X-Science-Unit":frame.image_unit,"X-Processing":"IMAGE-ZODI; strict-Level2-FLAGS-mask","X-Masked-Pixels":str(frame.mask.masked_count),"X-Total-Pixels":str(frame.mask.total_count),"X-Calibrated":"false"}
    if frame.detector is not None:headers["X-Detector"]=str(frame.detector)
    if frame.observation_id:headers["X-Observation-ID"]=frame.observation_id
    return Response(out.getvalue(),media_type="image/png",headers=headers)

@app.post("/pipeline/detect",tags=["pipeline"])
async def detect_sources_upload(file:UploadFile=File(...)):
    try:
        frame=process_level2_mef(await _read_fits(file));sources=await asyncio.to_thread(extract_sources,frame.image)
    except (ValueError,RuntimeError) as exc:raise HTTPException(status_code=422,detail=str(exc)) from exc
    return {"count":len(sources),"detector":frame.detector,"observation_id":frame.observation_id,"mjd_obs":frame.mjd_obs,"unit":frame.image_unit,"threshold_sigma":5.0,"classification":"UNMATCHED_DETECTIONS_NOT_DISCOVERIES","sources":sources}
