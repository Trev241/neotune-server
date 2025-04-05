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
        # Check if song exists
        existing_song = await self.get_by_email(song_data.email)
        if existing_song:
            raise AlreadyExistsException("Email already registered")

        # Create song
        song = Song(
            email=song_data.email, hashed_password=get_password_hash(song_data.password)
        )
        self.session.add(song)
        await self.session.commit()
        await self.session.refresh(song)

        logger.info(f"Created song: {song.email}")
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

    async def get_by_email(self, email: str) -> Song | None:
        """Get song by email.

        Args:
            email: Song email

        Returns:
            Optional[Song]: Found song or None if not found
        """
        query = select(Song).where(Song.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
