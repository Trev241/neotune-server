from sqlalchemy import Column, String, Text

from api.core.database import Base


class Artist(Base):
    """Artist model."""

    __tablename__ = "artists"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    bio = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)