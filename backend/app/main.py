from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.schemas import (
    ArchiveSearchRequest,
    ArchiveSearchResponse,
    HealthResponse,
    FITSInspectionResponse,
)
from app.services.irsa import ArchiveUnavailable, search_observations
from app.services.fits import inspect_fits, render_preview_png

settings = get_settings()

MAX_FITS_UPLOAD_BYTES = 20 * 1024 * 1024

app = FastAPI(
    title="SimpleSpace API",
    version="0.1.0",
    description=(
        "Scientific data access layer for exploring SPHEREx observations. "
        "Archive results are metadata, not discovery claims."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/health", response_model=HealthResponse, tags=["system"])
async def health() -> HealthResponse:
    return HealthResponse()


@app.post(
    "/archive/observations",
    response_model=ArchiveSearchResponse,
    tags=["archive"],
)
async def archive_observations(
    request: ArchiveSearchRequest,
) -> ArchiveSearchResponse:
    try:
        observations = await search_observations(settings, request)
    except ArchiveUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return ArchiveSearchResponse(
        source="NASA/IPAC IRSA TAP",
        table=settings.irsa_obscore_table,
        count=len(observations),
        observations=observations,
        note=(
            "These are archive metadata records. They are not yet converted into "
            "browser-ready image cutouts and must not be presented as confirmed "
            "moving or newly discovered objects."
        ),
    )


async def _read_fits_upload(file: UploadFile) -> bytes:
    payload = await file.read(MAX_FITS_UPLOAD_BYTES + 1)
    if len(payload) > MAX_FITS_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="FITS upload exceeds the 20 MiB limit.")
    return payload


@app.post("/archive/inspect-fits", response_model=FITSInspectionResponse, tags=["fits"])
async def inspect_fits_upload(file: UploadFile = File(...)) -> FITSInspectionResponse:
    payload = await _read_fits_upload(file)
    try:
        return FITSInspectionResponse(**inspect_fits(payload))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/archive/preview", tags=["fits"])
async def preview_fits_upload(file: UploadFile = File(...)) -> Response:
    payload = await _read_fits_upload(file)
    try:
        png = render_preview_png(payload)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return Response(
        content=png,
        media_type="image/png",
        headers={"X-Preview-Note": "Percentile-stretched preview; FLAGS are not decoded or masked."},
    )
