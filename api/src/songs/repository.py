from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.exceptions import AlreadyExistsException, NotFoundException
from api.core.logging import get_logger
from api.core.security import get_password_hash
from api.src.songs.models import Song
from api.src.songs.schemas import SongCreate

logger = get_logger(__name__)


class SongRepository:
    """Repository for handling song database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, song_data: SongCreate) -> Song:
        """Create a new song.

        Args:
            song_data: Song creation data

        Returns:
            Song: Created song

        Raises:
            AlreadyExistsException: If song with same email already exists
        """

        # Create song
        song = Song(
            title=song_data.title,
            release=song_data.release,
            year=song_data.year,
            duration=song_data.duration,
            thumbnail_url=song_data.thumbnail_url,
            artist_id=song_data.artist_id,
            id=song_data.id,
            song_code=song_data.song_code,
        )

        self.session.add(song)
        await self.session.commit()
        await self.session.refresh(song)

        logger.info(f"Created song: {song.title}")
        return song

    async def get_by_id(self, song_id: str) -> Song:
        """Get song by ID.

        Args:
            song_id: Song ID

        Returns:
            Song: Found song

        Raises:
            NotFoundException: If song not found
        """
        query = select(Song).where(Song.id == song_id)
        result = await self.session.execute(query)
        song = result.scalar_one_or_none()

        if not song:
            raise NotFoundException("Song not found")

        return song

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Song]:
        """Get all songs with pagination.

        Args:
            skip: Number of songs to skip
            limit: Maximum number of songs to return

        Returns:
            List[Song]: List of songs
        """
        query = select(Song).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_song_code(self, song_code: int) -> Song:
        """Get song by song_code

        Args:
            song_code: Song code

        Returns:
            Song: Found song
        """

        query = select(Song).where(Song.song_code == song_code)
        result = await self.session.execute(query)
        song = result.scalar_one_or_none()

        if not song:
            raise NotFoundException("Song not found")

        return song

    async def get_by_title(
        self, title: str, skip: int = 0, limit: int = 100
    ) -> List[Song]:
        """Get song by similar title

        Args:
            title: Query

        Returns:
            List[Song]: Found songs
        """

        query = (
            select(Song).where(Song.title.ilike(f"%{title}%")).offset(skip).limit(limit)
        )

        result = await self.session.execute(query)
        return result.scalars().all()
