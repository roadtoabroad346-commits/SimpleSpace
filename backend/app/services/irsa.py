from __future__ import annotations

import asyncio
import math
from typing import Any

import pyvo
from astropy.table import Table

from app.config import Settings
from app.schemas import ArchiveObservation, ArchiveSearchRequest


class ArchiveUnavailable(RuntimeError):
    """Raised when IRSA cannot be reached or returns an invalid TAP response."""


def _as_optional_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        number = float(value)
        return number if math.isfinite(number) else None
    except (TypeError, ValueError):
        return None


def _as_optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _query_irsa(settings: Settings, request: ArchiveSearchRequest) -> list[ArchiveObservation]:
    # Numeric values are validated by Pydantic before interpolation. Collection
    # names are configuration-only identifiers, never user-provided SQL input.
    collections = [name for name in settings.collection_names if name.replace("_", "").isalnum()]
    if not collections:
        raise ArchiveUnavailable("No valid SPHEREx collections are configured.")

    collection_sql = ", ".join("'" + name.replace("'", "''") + "'" for name in collections)
    table = settings.irsa_obscore_table
    if not all(part.replace("_", "").isalnum() for part in table.split(".")):
        raise ArchiveUnavailable("Configured ObsCore table name is invalid.")

    query = f"""
        SELECT TOP {min(request.limit, settings.irsa_max_rows)}
            s_ra, s_dec, obs_id, obs_collection, t_min, t_max,
            em_min, em_max, access_url
        FROM {table}
        WHERE CONTAINS(
            POINT('ICRS', s_ra, s_dec),
            CIRCLE('ICRS', {request.ra:.8f}, {request.dec:.8f}, {request.radius_deg:.6f})
        ) = 1
        AND obs_collection IN ({collection_sql})
        ORDER BY t_min ASC
    """

    try:
        service = pyvo.dal.TAPService(settings.irsa_tap_url)
        result = service.search(query, maxrec=min(request.limit, settings.irsa_max_rows))
        table_result: Table = result.to_table()
    except Exception as exc:  # network and remote TAP errors are surfaced as a controlled 503
        raise ArchiveUnavailable(f"IRSA TAP query failed: {type(exc).__name__}") from exc

    rows: list[ArchiveObservation] = []
    for row in table_result:
        rows.append(ArchiveObservation(
            ra_deg=_as_optional_float(row["s_ra"]),
            dec_deg=_as_optional_float(row["s_dec"]),
            obs_id=_as_optional_str(row["obs_id"]),
            obs_collection=_as_optional_str(row["obs_collection"]),
            t_min=_as_optional_float(row["t_min"]),
            t_max=_as_optional_float(row["t_max"]),
            em_min=_as_optional_float(row["em_min"]),
            em_max=_as_optional_float(row["em_max"]),
            access_url=_as_optional_str(row["access_url"]),
        ))
    return rows


async def search_observations(
    settings: Settings, request: ArchiveSearchRequest
) -> list[ArchiveObservation]:
    return await asyncio.to_thread(_query_irsa, settings, request)
