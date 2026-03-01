from app.db.base import Base
from app.db.engine import engine

# import models so SQLAlchemy knows them
from app.models import user  # noqa
from app.models import article  # noqa


def init_db():
    Base.metadata.create_all(bind=engine)