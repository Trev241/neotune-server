from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_session
from api.core.logging import get_logger
from api.core.security import get_current_user
from api.src.artists.schemas import ArtistCreate, ArtistResponse, ArtistUpdate
from api.src.artists.service import ArtistService

logger = get_logger(__name__)

router = APIRouter(prefix="/artists", tags=["artists"])


@router.post(
    "", response_model=ArtistResponse, status_code=status.HTTP_201_CREATED
)
async def create_artist(
    artist_data: ArtistCreate, session: AsyncSession = Depends(get_session)
) -> ArtistResponse:
    """Create a new artist."""
    logger.debug(f"Creating artist: {artist_data.name}")
    return await ArtistService(session).create_artist(artist_data)


@router.get("/{artist_id}", response_model=ArtistResponse)
async def get_artist(
    artist_id: str, session: AsyncSession = Depends(get_session)
) -> ArtistResponse:
    """Get artist by ID."""
    logger.debug(f"Getting artist: {artist_id}")
    return await ArtistService(session).get_artist(artist_id)


@router.get("", response_model=List[ArtistResponse])
async def get_artists(
    skip: int = 0, 
    limit: int = 100, 
    session: AsyncSession = Depends(get_session)
) -> List[ArtistResponse]:
    """Get all artists with pagination."""
    logger.debug(f"Getting artists, skip: {skip}, limit: {limit}")
    return await ArtistService(session).get_artists(skip, limit)


@router.put("/{artist_id}", response_model=ArtistResponse)
async def update_artist(
    artist_id: str,
    artist_data: ArtistUpdate,
    session: AsyncSession = Depends(get_session)
) -> ArtistResponse:
    """Update artist by ID."""
    logger.debug(f"Updating artist: {artist_id}")
    return await ArtistService(session).update_artist(artist_id, artist_data)


@router.delete("/{artist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_artist(
    artist_id: str, session: AsyncSession = Depends(get_session)
) -> None:
    """Delete artist by ID."""
    logger.debug(f"Deleting artist: {artist_id}")
    await ArtistService(session).delete_artist(artist_id)