from typing import Optional
from pydantic import BaseModel, ConfigDict


class ArtistBase(BaseModel):
    """Base artist schema."""
    name: str
    bio: Optional[str] = None
    image_url: Optional[str] = None


class ArtistCreate(ArtistBase):
    """Artist creation schema."""
    id: str


class ArtistUpdate(ArtistBase):
    """Artist update schema."""
    name: Optional[str] = None


class ArtistResponse(ArtistBase):
    """Artist response schema."""
    model_config = ConfigDict(from_attributes=True)
    id: str