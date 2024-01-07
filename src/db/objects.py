# database objects

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Integer, CHAR
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass, Session

from src.db.constants import *


class Base(DeclarativeBase, MappedAsDataclass):
    pass


class Channel(Base):
    __tablename__ = "channels"

    id: Mapped[str] = mapped_column(CHAR(YT_CHANNELID_LEN), primary_key=True)
    name: Mapped[str] = mapped_column(CHAR(YT_CHANNELNAME_LEN))

    def __repr__(self) -> str:
        return f"id={self.id!r}, name={self.name!r}"


class Video(Base):
    __tablename__ = "videos"

    id: Mapped[str] = mapped_column(CHAR(YT_VIDEOID_LEN), primary_key=True)

    title: Mapped[str] = mapped_column(CHAR(YT_VIDEOTITLE_LEN))
    channelid: Mapped[str] = mapped_column(
        CHAR(YT_CHANNELID_LEN), ForeignKey("channels.id"))

    def __repr__(self) -> str:
        return f"id={self.id!r}, title={self.title!r}"


class VideoMeta(Base):
    __tablename__ = "videometas"

    id: Mapped[str] = mapped_column(CHAR(YT_VIDEOID_LEN), primary_key=True)

    # caching columns
    videoexists: Mapped[Boolean] = mapped_column(Boolean) # video exists
    cachedate: Mapped[DateTime] = mapped_column(DateTime) # time this video was cached into DB

    # data columns
    commentcount: Mapped[Integer] = mapped_column(Integer)
    duration: Mapped[Integer] = mapped_column(Integer) # duration in seconds
    likecount: Mapped[Integer] = mapped_column(Integer)
    viewcount: Mapped[Integer] = mapped_column(Integer)

    def __repr__(self) -> str:
        return f"id={self.id!r}, viewcount={self.viewcount!r}, duration={self.duration!r}"


class WatchHistory(Base):
    __tablename__ = "watch_history"

    timestamp: Mapped[DateTime] = mapped_column(
        CHAR(ISO_TIMESTAMP_LEN), primary_key=True)

    videoid: Mapped[str] = mapped_column(
        CHAR(YT_VIDEOID_LEN), ForeignKey("videos.id"))

    def __repr__(self) -> str:
        return f"time={self.timestamp!r}, video={self.videoid!r}"
