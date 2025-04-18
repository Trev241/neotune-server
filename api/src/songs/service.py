from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from api.core.logging import get_logger
from api.core.audio import AudioDownloader, Recommender
from api.src.songs.models import Song
from api.src.songs.repository import SongRepository
from api.src.songs.schemas import SongCreate
from api.src.artists.repository import ArtistRepository

logger = get_logger(__name__)


def stream_audio(file, chunk_size=8192):
    with open(file, "rb") as f:
        while chunk := f.read(chunk_size):
            yield chunk


class SongService:
    """Service for handling song business logic."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = SongRepository(session)
        self.artist_repository = ArtistRepository(session)
        self.audio_downloader = AudioDownloader()
        self.recommender = Recommender()

    async def create_song(self, song_data: SongCreate) -> Song:
        """Create a new song."""
        return await self.repository.create(song_data)

    async def get_song(self, song_id: str) -> Song:
        """Get song by ID."""
        return await self.repository.get_by_id(song_id)

    async def get_stream(self, song_id: str):
        """Get stream by ID"""
        song = await self.repository.get_by_id(song_id)
        artist = await self.artist_repository.get_by_id(song.artist_id)
        details = self.audio_downloader.download(song_id, song.title, artist.name)

        return {
            "stream": stream_audio(details["filepath"]),
            "ext": {details["filepath"].split(".")[-1]},
        }

    async def get_songs(self, skip: int = 0, limit: int = 100) -> List[Song]:
        """Get all songs with pagination."""
        return await self.repository.get_all(skip, limit)

    async def recommend_songs(self, song_id, top_k=5) -> List[Song]:
        song = await self.repository.get_by_id(song_id)
        song_codes, _ = self.recommender.find_similar_songs(song.song_code, top_k)

        similar_songs = []
        for song_code in song_codes:
            similar_song = await self.repository.get_by_song_code(song_code)
            similar_songs.append(similar_song)

        return similar_songs
