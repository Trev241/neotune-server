from sqlalchemy import Column, Integer, String, Float

from api.core.database import Base


class Song(Base):
    """Song model."""

    __tablename__ = "songs"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, unique=True, index=True, nullable=False)
    release = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    duration = Column(Float, nullable=False)
    thumbnail_url = Column(String)
    artist_id = Column(String)
