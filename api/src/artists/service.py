from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from api.core.logging import get_logger
from api.src.artists.models import Artist
from api.src.artists.repository import ArtistRepository
from api.src.artists.schemas import ArtistCreate, ArtistUpdate

logger = get_logger(__name__)


class ArtistService:
    """Service for handling artist business logic."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = ArtistRepository(session)

    async def create_artist(self, artist_data: ArtistCreate) -> Artist:
        """Create a new artist."""
        return await self.repository.create(artist_data)

    async def get_artist(self, artist_id: str) -> Artist:
        """Get artist by ID."""
        return await self.repository.get_by_id(artist_id)

    async def get_artists(self, skip: int = 0, limit: int = 100) -> List[Artist]:
        """Get all artists with pagination."""
        return await self.repository.get_all(skip, limit)

    async def update_artist(self, artist_id: str, artist_data: ArtistUpdate) -> Artist:
        """Update artist by ID."""
        return await self.repository.update(artist_id, artist_data)

    async def delete_artist(self, artist_id: str) -> None:
        """Delete artist by ID."""
        await self.repository.delete(artist_id)