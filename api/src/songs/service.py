from sqlalchemy.ext.asyncio import AsyncSession

from api.core.logging import get_logger
from api.src.songs.models import Song
from api.src.songs.repository import SongRepository
from api.src.songs.schemas import SongCreate

logger = get_logger(__name__)


class SongService:
    """Service for handling song business logic."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = SongRepository(session)

    async def create_song(self, song_data: SongCreate) -> Song:
        """Create a new song."""
        return await self.repository.create(song_data)

    async def get_song(self, song_id: str) -> Song:
        """Get song by ID."""
        return await self.repository.get_by_id(song_id)
