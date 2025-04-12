from typing import List

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_session
from api.core.logging import get_logger
from api.core.security import get_current_user
from api.src.playlists.schemas import (
    PlaylistCreate, PlaylistResponse, PlaylistUpdate, PlaylistDetail,
    AddSongRequest, RemoveSongRequest, ReorderSongRequest
)
from api.src.playlists.service import PlaylistService
from api.src.users.models import User

logger = get_logger(__name__)

router = APIRouter(prefix="/playlists", tags=["playlists"])


@router.post(
    "", response_model=PlaylistResponse, status_code=status.HTTP_201_CREATED
)
async def create_playlist(
    playlist_data: PlaylistCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> PlaylistResponse:
    """Create a new playlist for the current user."""
    logger.debug(f"Creating playlist: {playlist_data.name} for user: {current_user.id}")
    return await PlaylistService(session).create_playlist(current_user.id, playlist_data)


@router.get("", response_model=List[PlaylistResponse])
async def get_user_playlists(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> List[PlaylistResponse]:
    """Get all playlists for the current user."""
    logger.debug(f"Getting playlists for user: {current_user.id}")
    return await PlaylistService(session).get_user_playlists(current_user.id, skip, limit)


@router.get("/{playlist_id}", response_model=PlaylistDetail)
async def get_playlist(
    playlist_id: str,
    session: AsyncSession = Depends(get_session)
) -> PlaylistDetail:
    """Get a playlist with all its songs."""
    logger.debug(f"Getting playlist: {playlist_id}")
    return await PlaylistService(session).get_playlist_detail(playlist_id)


@router.put("/{playlist_id}", response_model=PlaylistResponse)
async def update_playlist(
    playlist_id: str,
    playlist_data: PlaylistUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> PlaylistResponse:
    """Update a playlist."""
    logger.debug(f"Updating playlist: {playlist_id}")
    try:
        return await PlaylistService(session).update_playlist(
            playlist_id, current_user.id, playlist_data
        )
    except HTTPException as e:
        logger.error(f"Error updating playlist: {e.detail}")
        raise


@router.delete("/{playlist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_playlist(
    playlist_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> None:
    """Delete a playlist."""
    logger.debug(f"Deleting playlist: {playlist_id}")
    await PlaylistService(session).delete_playlist(playlist_id, current_user.id)


@router.post("/{playlist_id}/songs", status_code=status.HTTP_204_NO_CONTENT)
async def add_song_to_playlist(
    playlist_id: str,
    song_data: AddSongRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> None:
    """Add a song to a playlist."""
    logger.debug(f"Adding song {song_data.song_id} to playlist: {playlist_id}")
    await PlaylistService(session).add_song_to_playlist(
        playlist_id, current_user.id, song_data.song_id, song_data.order
    )


@router.delete("/{playlist_id}/songs", status_code=status.HTTP_204_NO_CONTENT)
async def remove_song_from_playlist(
    playlist_id: str,
    song_data: RemoveSongRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> None:
    """Remove a song from a playlist."""
    logger.debug(f"Removing song {song_data.song_id} from playlist: {playlist_id}")
    await PlaylistService(session).remove_song_from_playlist(
        playlist_id, current_user.id, song_data.song_id
    )


@router.put("/{playlist_id}/songs", status_code=status.HTTP_204_NO_CONTENT)
async def reorder_song_in_playlist(
    playlist_id: str,
    song_data: ReorderSongRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> None:
    """Reorder a song in a playlist."""
    logger.debug(f"Reordering song {song_data.song_id} in playlist: {playlist_id}")
    await PlaylistService(session).reorder_song_in_playlist(
        playlist_id, current_user.id, song_data.song_id, song_data.new_order
    )