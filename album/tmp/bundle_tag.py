from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
)

from album.database import Base


class BundleTag(Base):
    __tablename__ = 'bundle_tag'

    id = Column(Integer, primary_key=True)
    bundle_id = Column(Integer)
    tag = Column(String(255))
    created_at = Column(DateTime)
