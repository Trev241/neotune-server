from typing import Annotated, List

from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_session
from api.core.logging import get_logger
from api.src.songs.schemas import SongCreate, SongResponse
from api.src.songs.service import SongService
from api.src.songs.models import Song

logger = get_logger(__name__)

router = APIRouter(prefix="/songs", tags=["songs"])


@router.post("", response_model=SongResponse, status_code=status.HTTP_201_CREATED)
async def add_song(
    song_data: SongCreate, session: AsyncSession = Depends(get_session)
) -> SongResponse:
    """Register a new song."""
    logger.debug(f"Adding song: {song_data.title}")
    return await SongService(session).create_song(song_data)


@router.get("", response_model=List[SongResponse])
async def get_songs(
    skip: int = 0, limit: int = 100, session: AsyncSession = Depends(get_session)
) -> List[Song]:
    """Get all artists with pagination."""
    logger.debug(f"Getting artists, skip: {skip}, limit: {limit}")
    return await SongService(session).get_songs(skip, limit)


@router.get("/stream", status_code=status.HTTP_200_OK)
async def stream_song(song_id: str, session: AsyncSession = Depends(get_session)):
    """Stream a song"""
    details = await SongService(session).get_stream(song_id)
    return StreamingResponse(details["stream"], media_type=f"audio/{details['ext']}")


@router.get("/recommend", status_code=status.HTTP_200_OK)
async def recommend_songs(
    song_id: str, top_k: int = 5, session: AsyncSession = Depends(get_session)
):
    """Recommend a song"""
    logger.debug(f"Requesting songs similar to song: {song_id}")
    return await SongService(session).recommend_songs(song_id, top_k)


@router.get("/search", status_code=status.HTTP_200_OK)
async def search(
    query: str,
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_session),
):
    """Search for a song"""
    logger.debug(f"Searching f{query}")
    return await SongService(session).search_songs(query, skip, limit)
