from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.exceptions import AlreadyExistsException, NotFoundException
from api.core.logging import get_logger
from api.src.artists.models import Artist
from api.src.artists.schemas import ArtistCreate, ArtistUpdate

logger = get_logger(__name__)


class ArtistRepository:
    """Repository for handling artist database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, artist_data: ArtistCreate) -> Artist:
        """Create a new artist.

        Args:
            artist_data: Artist creation data

        Returns:
            Artist: Created artist

        Raises:
            AlreadyExistsException: If artist with same name already exists
        """
        # Check if artist exists
        existing_artist = await self.get_by_name(artist_data.name)
        if existing_artist:
            raise AlreadyExistsException("Artist with this name already exists")

        # Create artist
        artist = Artist(
            id=artist_data.id,
            name=artist_data.name,
            bio=artist_data.bio,
            image_url=artist_data.image_url
        )
        self.session.add(artist)
        await self.session.commit()
        await self.session.refresh(artist)

        logger.info(f"Created artist: {artist.name}")
        return artist

    async def get_by_id(self, artist_id: str) -> Artist:
        """Get artist by ID.

        Args:
            artist_id: Artist ID

        Returns:
            Artist: Found artist

        Raises:
            NotFoundException: If artist not found
        """
        query = select(Artist).where(Artist.id == artist_id)
        result = await self.session.execute(query)
        artist = result.scalar_one_or_none()

        if not artist:
            raise NotFoundException("Artist not found")

        return artist

    async def get_by_name(self, name: str) -> Optional[Artist]:
        """Get artist by name.

        Args:
            name: Artist name

        Returns:
            Optional[Artist]: Found artist or None if not found
        """
        query = select(Artist).where(Artist.name == name)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Artist]:
        """Get all artists with pagination.

        Args:
            skip: Number of artists to skip
            limit: Maximum number of artists to return

        Returns:
            List[Artist]: List of artists
        """
        query = select(Artist).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def update(self, artist_id: str, artist_data: ArtistUpdate) -> Artist:
        """Update artist by ID.

        Args:
            artist_id: Artist ID
            artist_data: Artist update data

        Returns:
            Artist: Updated artist

        Raises:
            NotFoundException: If artist not found
        """
        # Get artist
        artist = await self.get_by_id(artist_id)
        
        # Update fields if they are provided and not None
        if artist_data.name is not None:
            artist.name = artist_data.name
            
        if artist_data.bio is not None:
            artist.bio = artist_data.bio
            
        if artist_data.image_url is not None:
            artist.image_url = artist_data.image_url
            
        await self.session.commit()
        await self.session.refresh(artist)
        
        logger.info(f"Updated artist: {artist.name}")
        return artist

    async def delete(self, artist_id: str) -> None:
        """Delete artist by ID.

        Args:
            artist_id: Artist ID

        Raises:
            NotFoundException: If artist not found
        """
        # Get artist
        artist = await self.get_by_id(artist_id)
        
        # Delete artist
        await self.session.delete(artist)
        await self.session.commit()
        
        logger.info(f"Deleted artist: {artist.name}")