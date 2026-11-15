from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.schemas import (
    ArchiveSearchRequest,
    ArchiveSearchResponse,
    HealthResponse,
)
from app.services.irsa import ArchiveUnavailable, search_observations

settings = get_settings()

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
