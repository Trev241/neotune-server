from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, UniqueConstraint, Index
from sqlalchemy.sql import func

from api.core.database import Base


class Playlist(Base):
    """Playlist model."""

    __tablename__ = "playlists"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    cover_image_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Create an index on user_id to improve query performance
    __table_args__ = (
        Index('ix_playlists_user_id', user_id),
    )


class PlaylistSong(Base):
    """Junction table for playlist-song many-to-many relationship."""

    __tablename__ = "playlist_songs"

    playlist_id = Column(String, ForeignKey("playlists.id", ondelete="CASCADE"), primary_key=True)
    song_id = Column(String, ForeignKey("songs.id", ondelete="CASCADE"), primary_key=True)
    order = Column(Integer, nullable=False)
    added_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Ensure song order is unique within a playlist
    __table_args__ = (
        UniqueConstraint('playlist_id', 'order', name='unique_song_order'),
    )