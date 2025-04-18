from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class PlaylistBase(BaseModel):
    """Base playlist schema."""

    name: str
    cover_image_url: Optional[str] = None


class PlaylistCreate(PlaylistBase):
    """Playlist creation schema."""

    id: Optional[str] = None  # If not provided, will be generated
    user_id: Optional[str] = None  # Will be set from current user


class PlaylistUpdate(BaseModel):
    """Playlist update schema."""

    name: Optional[str] = None
    cover_image_url: Optional[str] = None


class PlaylistResponse(PlaylistBase):
    """Playlist response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    song_count: int = 0


class PlaylistDetail(PlaylistResponse):
    """Playlist detail response schema with songs."""

    songs: List[Dict[str, Any]] = Field(default_factory=list)


class AddSongRequest(BaseModel):
    """Request schema for adding a song to a playlist."""

    song_id: str
    order: Optional[int] = None  # If not provided, append to end


class RemoveSongRequest(BaseModel):
    """Request schema for removing a song from a playlist."""

    song_id: str


class ReorderSongRequest(BaseModel):
    """Request schema for reordering a song in a playlist."""

    song_id: str
    new_order: int
