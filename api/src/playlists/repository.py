from typing import List, Optional, Dict, Any
import uuid
from sqlalchemy import select, func, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

from api.core.exceptions import AlreadyExistsException, NotFoundException, ForbiddenException
from api.core.logging import get_logger
from api.src.playlists.models import Playlist, PlaylistSong
from api.src.playlists.schemas import PlaylistCreate, PlaylistUpdate
from api.src.songs.models import Song

logger = get_logger(__name__)


class PlaylistRepository:
    """Repository for handling playlist database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, playlist_data: PlaylistCreate) -> Playlist:
        """Create a new playlist.

        Args:
            playlist_data: Playlist creation data

        Returns:
            Playlist: Created playlist
        """
        # Generate ID if not provided
        if not playlist_data.id:
            playlist_data.id = str(uuid.uuid4())

        # Create playlist
        playlist = Playlist(
            id=playlist_data.id,
            name=playlist_data.name,
            user_id=playlist_data.user_id,
            cover_image_url=playlist_data.cover_image_url
        )
        self.session.add(playlist)
        await self.session.commit()
        await self.session.refresh(playlist)

        logger.info(f"Created playlist: {playlist.name} for user: {playlist.user_id}")
        return playlist

    async def get_by_id(self, playlist_id: str) -> Playlist:
        """Get playlist by ID.

        Args:
            playlist_id: Playlist ID

        Returns:
            Playlist: Found playlist

        Raises:
            NotFoundException: If playlist not found
        """
        query = select(Playlist).where(Playlist.id == playlist_id)
        result = await self.session.execute(query)
        playlist = result.scalar_one_or_none()

        if not playlist:
            raise NotFoundException("Playlist not found")

        return playlist

    async def get_by_user_id(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Playlist]:
        """Get all playlists for a user with pagination.

        Args:
            user_id: User ID
            skip: Number of playlists to skip
            limit: Maximum number of playlists to return

        Returns:
            List[Playlist]: List of playlists
        """
        query = select(Playlist).where(Playlist.user_id == user_id).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_playlist_with_songs(self, playlist_id: str) -> Dict[str, Any]:
        """Get a playlist with all its songs.

        Args:
            playlist_id: Playlist ID

        Returns:
            Dict: Playlist data with songs

        Raises:
            NotFoundException: If playlist not found
        """
        # Get the playlist
        playlist = await self.get_by_id(playlist_id)
        
        # Get songs in the playlist with their details
        query = select(
            Song,
            PlaylistSong.order,
            PlaylistSong.added_at
        ).join(
            PlaylistSong, PlaylistSong.song_id == Song.id
        ).where(
            PlaylistSong.playlist_id == playlist_id
        ).order_by(
            PlaylistSong.order
        )
        
        result = await self.session.execute(query)
        songs_data = []
        
        for song, order, added_at in result:
            songs_data.append({
                "id": song.id,
                "title": song.title,
                "artist_id": song.artist_id,
                "duration": song.duration,
                "thumbnail_url": song.thumbnail_url,
                "order": order,
                "added_at": added_at
            })
        
        # Count the songs
        query = select(func.count()).where(PlaylistSong.playlist_id == playlist_id)
        result = await self.session.execute(query)
        song_count = result.scalar_one() or 0
        
        # Build response
        playlist_data = {
            "id": playlist.id,
            "name": playlist.name,
            "user_id": playlist.user_id,
            "cover_image_url": playlist.cover_image_url,
            "created_at": playlist.created_at,
            "updated_at": playlist.updated_at,
            "song_count": song_count,
            "songs": songs_data
        }
        
        return playlist_data

    async def update(self, playlist_id: str, user_id: str, playlist_data: PlaylistUpdate) -> Playlist:
        """Update playlist by ID.

        Args:
            playlist_id: Playlist ID
            user_id: User ID for authorization
            playlist_data: Playlist update data

        Returns:
            Playlist: Updated playlist

        Raises:
            NotFoundException: If playlist not found
            ForbiddenException: If user is not the owner of the playlist
        """
        # Get playlist
        playlist = await self.get_by_id(playlist_id)
        
        # Check ownership
        if playlist.user_id != user_id:
            raise ForbiddenException("You don't have permission to update this playlist")
        
        # Update fields if they are provided and not None
        if playlist_data.name is not None:
            playlist.name = playlist_data.name
            
        if playlist_data.cover_image_url is not None:
            playlist.cover_image_url = playlist_data.cover_image_url
            
        await self.session.commit()
        await self.session.refresh(playlist)
        
        logger.info(f"Updated playlist: {playlist.name}")
        return playlist

    async def delete(self, playlist_id: str, user_id: str) -> None:
        """Delete playlist by ID.

        Args:
            playlist_id: Playlist ID
            user_id: User ID for authorization

        Raises:
            NotFoundException: If playlist not found
            ForbiddenException: If user is not the owner of the playlist
        """
        # Get playlist
        playlist = await self.get_by_id(playlist_id)
        
        # Check ownership
        if playlist.user_id != user_id:
            raise ForbiddenException("You don't have permission to delete this playlist")
        
        # Delete playlist
        await self.session.delete(playlist)
        await self.session.commit()
        
        logger.info(f"Deleted playlist: {playlist.name}")

    async def add_song(self, playlist_id: str, user_id: str, song_id: str, order: Optional[int] = None) -> None:
        """Add a song to a playlist.

        Args:
            playlist_id: Playlist ID
            user_id: User ID for authorization
            song_id: Song ID to add
            order: Position of the song in the playlist (optional)

        Raises:
            NotFoundException: If playlist or song not found
            ForbiddenException: If user is not the owner of the playlist
            AlreadyExistsException: If song is already in the playlist
        """
        # Get playlist
        playlist = await self.get_by_id(playlist_id)
        
        # Check ownership
        if playlist.user_id != user_id:
            raise ForbiddenException("You don't have permission to modify this playlist")
        
        # Check if song exists
        song_query = select(Song).where(Song.id == song_id)
        song_result = await self.session.execute(song_query)
        song = song_result.scalar_one_or_none()
        
        if not song:
            raise NotFoundException("Song not found")
        
        # Check if song is already in playlist
        check_query = select(PlaylistSong).where(
            PlaylistSong.playlist_id == playlist_id,
            PlaylistSong.song_id == song_id
        )
        check_result = await self.session.execute(check_query)
        existing = check_result.scalar_one_or_none()
        
        if existing:
            raise AlreadyExistsException("Song is already in this playlist")
        
        # If order is not specified, add to the end
        if order is None:
            count_query = select(func.count()).where(PlaylistSong.playlist_id == playlist_id)
            count_result = await self.session.execute(count_query)
            order = count_result.scalar_one() or 0
        else:
            # If inserting at a specific position, shift existing songs
            shift_query = update(PlaylistSong).where(
                PlaylistSong.playlist_id == playlist_id,
                PlaylistSong.order >= order
            ).values(
                order=PlaylistSong.order + 1
            )
            await self.session.execute(shift_query)
        
        # Add song to playlist
        playlist_song = PlaylistSong(
            playlist_id=playlist_id,
            song_id=song_id,
            order=order
        )
        self.session.add(playlist_song)
        await self.session.commit()
        
        logger.info(f"Added song {song_id} to playlist {playlist_id} at position {order}")

    async def remove_song(self, playlist_id: str, user_id: str, song_id: str) -> None:
        """Remove a song from a playlist.

        Args:
            playlist_id: Playlist ID
            user_id: User ID for authorization
            song_id: Song ID to remove

        Raises:
            NotFoundException: If playlist or song in playlist not found
            ForbiddenException: If user is not the owner of the playlist
        """
        # Get playlist
        playlist = await self.get_by_id(playlist_id)
        
        # Check ownership
        if playlist.user_id != user_id:
            raise ForbiddenException("You don't have permission to modify this playlist")
        
        # Check if song is in playlist
        find_query = select(PlaylistSong).where(
            PlaylistSong.playlist_id == playlist_id,
            PlaylistSong.song_id == song_id
        )
        find_result = await self.session.execute(find_query)
        playlist_song = find_result.scalar_one_or_none()
        
        if not playlist_song:
            raise NotFoundException("Song not found in this playlist")
        
        # Get the order of the song to be removed
        removed_order = playlist_song.order
        
        # Remove song from playlist
        delete_query = delete(PlaylistSong).where(
            PlaylistSong.playlist_id == playlist_id,
            PlaylistSong.song_id == song_id
        )
        await self.session.execute(delete_query)
        
        # Reorder remaining songs
        reorder_query = update(PlaylistSong).where(
            PlaylistSong.playlist_id == playlist_id,
            PlaylistSong.order > removed_order
        ).values(
            order=PlaylistSong.order - 1
        )
        await self.session.execute(reorder_query)
        
        await self.session.commit()
        logger.info(f"Removed song {song_id} from playlist {playlist_id}")

    async def reorder_song(self, playlist_id: str, user_id: str, song_id: str, new_order: int) -> None:
        """Reorder a song in a playlist.

        Args:
            playlist_id: Playlist ID
            user_id: User ID for authorization
            song_id: Song ID to reorder
            new_order: New position of the song

        Raises:
            NotFoundException: If playlist or song in playlist not found
            ForbiddenException: If user is not the owner of the playlist
        """
        # Get playlist
        playlist = await self.get_by_id(playlist_id)
        
        # Check ownership
        if playlist.user_id != user_id:
            raise ForbiddenException("You don't have permission to modify this playlist")
        
        # Check if song is in playlist
        find_query = select(PlaylistSong).where(
            PlaylistSong.playlist_id == playlist_id,
            PlaylistSong.song_id == song_id
        )
        find_result = await self.session.execute(find_query)
        playlist_song = find_result.scalar_one_or_none()
        
        if not playlist_song:
            raise NotFoundException("Song not found in this playlist")
        
        # Get the current order of the song
        current_order = playlist_song.order
        
        # Don't do anything if order doesn't change
        if current_order == new_order:
            return
        
        # Count songs to validate new_order
        count_query = select(func.count()).where(PlaylistSong.playlist_id == playlist_id)
        count_result = await self.session.execute(count_query)
        song_count = count_result.scalar_one() or 0
        
        if new_order < 0 or new_order >= song_count:
            raise ValueError(f"Invalid order. Order must be between 0 and {song_count - 1}")
        
        # Update orders of affected songs
        if current_order < new_order:
            # Moving down: decrease order for songs between current and new
            shift_query = update(PlaylistSong).where(
                PlaylistSong.playlist_id == playlist_id,
                PlaylistSong.order > current_order,
                PlaylistSong.order <= new_order
            ).values(
                order=PlaylistSong.order - 1
            )
        else:
            # Moving up: increase order for songs between new and current
            shift_query = update(PlaylistSong).where(
                PlaylistSong.playlist_id == playlist_id,
                PlaylistSong.order >= new_order,
                PlaylistSong.order < current_order
            ).values(
                order=PlaylistSong.order + 1
            )
        
        await self.session.execute(shift_query)
        
        # Update the target song order
        update_query = update(PlaylistSong).where(
            PlaylistSong.playlist_id == playlist_id,
            PlaylistSong.song_id == song_id
        ).values(
            order=new_order
        )
        await self.session.execute(update_query)
        
        await self.session.commit()
        logger.info(f"Reordered song {song_id} from position {current_order} to {new_order} in playlist {playlist_id}")

    async def get_song_count(self, playlist_id: str) -> int:
        """Get the number of songs in a playlist.

        Args:
            playlist_id: Playlist ID

        Returns:
            int: Number of songs in the playlist
        """
        query = select(func.count()).where(PlaylistSong.playlist_id == playlist_id)
        result = await self.session.execute(query)
        return result.scalar_one() or 0