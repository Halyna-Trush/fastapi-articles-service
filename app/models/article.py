from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)

    # article title
    title = Column(String, nullable=False)

    # main article content
    content = Column(Text, nullable=False)

    # owner reference
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # relationship to User model
    owner = relationship("User", backref="articles")

    