# create database

from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass, Session

from src.db.objects import Base, Channel, Video, WatchHistory


def get_database_engine():
    """
    Create the database and return the engine
    """

    # the Engine is a factory that can create new database connections for us
    db_engine = create_engine("sqlite:///data")  # , echo=True)

    # generate DB schema at once in our target SQLite database
    Base.metadata.create_all(bind=db_engine)

    return db_engine
