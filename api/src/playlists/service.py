from typing import List, Dict, Any, Optional

import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.logging import get_logger
from api.src.playlists.repository import PlaylistRepository
from api.src.playlists.models import Playlist
from api.src.playlists.schemas import PlaylistCreate, PlaylistUpdate

logger = get_logger(__name__)


class PlaylistService:
    """Service for handling playlist business logic."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = PlaylistRepository(session)

    async def create_playlist(self, user_id: str, playlist_data: PlaylistCreate) -> Playlist:
        """Create a new playlist for a user.
        
        Args:
            user_id: ID of the user creating the playlist
            playlist_data: Playlist creation data
            
        Returns:
            Playlist: Created playlist
        """
        # Set the user ID
        playlist_data.user_id = user_id
        
        # Generate ID if not provided
        if not playlist_data.id:
            playlist_data.id = str(uuid.uuid4())
            
        return await self.repository.create(playlist_data)

    async def get_playlist(self, playlist_id: str) -> Playlist:
        """Get a playlist by ID.
        
        Args:
            playlist_id: ID of the playlist
            
        Returns:
            Playlist: Found playlist
        """
        return await self.repository.get_by_id(playlist_id)

    async def get_playlist_detail(self, playlist_id: str) -> Dict[str, Any]:
        """Get a playlist with all its songs.
        
        Args:
            playlist_id: ID of the playlist
            
        Returns:
            Dict: Playlist data with songs
        """
        return await self.repository.get_playlist_with_songs(playlist_id)

    async def get_user_playlists(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Playlist]:
        """Get all playlists for a user.
        
        Args:
            user_id: ID of the user
            skip: Number of playlists to skip
            limit: Maximum number of playlists to return
            
        Returns:
            List[Playlist]: List of playlists
        """
        playlists = await self.repository.get_by_user_id(user_id, skip, limit)
        
        # Add song count to each playlist
        for playlist in playlists:
            setattr(playlist, 'song_count', await self.repository.get_song_count(playlist.id))
            
        return playlists

    async def update_playlist(self, playlist_id: str, user_id: str, playlist_data: PlaylistUpdate) -> Playlist:
        """Update a playlist.
        
        Args:
            playlist_id: ID of the playlist
            user_id: ID of the user (for authorization)
            playlist_data: Playlist update data
            
        Returns:
            Playlist: Updated playlist
        """
        return await self.repository.update(playlist_id, user_id, playlist_data)

    async def delete_playlist(self, playlist_id: str, user_id: str) -> None:
        """Delete a playlist.
        
        Args:
            playlist_id: ID of the playlist
            user_id: ID of the user (for authorization)
        """
        await self.repository.delete(playlist_id, user_id)

    async def add_song_to_playlist(self, playlist_id: str, user_id: str, song_id: str, order: Optional[int] = None) -> None:
        """Add a song to a playlist.
        
        Args:
            playlist_id: ID of the playlist
            user_id: ID of the user (for authorization)
            song_id: ID of the song to add
            order: Position of the song in the playlist (optional)
        """
        await self.repository.add_song(playlist_id, user_id, song_id, order)

    async def remove_song_from_playlist(self, playlist_id: str, user_id: str, song_id: str) -> None:
        """Remove a song from a playlist.
        
        Args:
            playlist_id: ID of the playlist
            user_id: ID of the user (for authorization)
            song_id: ID of the song to remove
        """
        await self.repository.remove_song(playlist_id, user_id, song_id)

    async def reorder_song_in_playlist(self, playlist_id: str, user_id: str, song_id: str, new_order: int) -> None:
        """Reorder a song in a playlist.
        
        Args:
            playlist_id: ID of the playlist
            user_id: ID of the user (for authorization)
            song_id: ID of the song to reorder
            new_order: New position of the song
        """
        await self.repository.reorder_song(playlist_id, user_id, song_id, new_order)