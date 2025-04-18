from pydantic import BaseModel, ConfigDict, EmailStr


class SongBase(BaseModel):
    """Base song schema."""

    title: str
    song_code: int
    release: str
    year: int
    duration: int
    thumbnail_url: str
    artist_id: str


class SongCreate(SongBase):
    """Song creation schema."""

    id: str


class SongResponse(SongBase):
    """Song response schema."""

    model_config = ConfigDict(from_attributes=True)
    id: str
