from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_session
from api.core.logging import get_logger
from api.src.songs.schemas import SongCreate, SongResponse
from api.src.songs.service import SongService

logger = get_logger(__name__)

router = APIRouter(prefix="/songs", tags=["songs"])


@router.post(
    "/register", response_model=SongResponse, status_code=status.HTTP_201_CREATED
)
async def add_song(
    song_data: SongCreate, session: AsyncSession = Depends(get_session)
) -> SongResponse:
    """Register a new song."""
    logger.debug(f"Adding song: {song_data.title}")
    return await SongService(session).create_song(song_data)
