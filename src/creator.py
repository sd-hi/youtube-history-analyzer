import json
import os

from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass, Session

from db.objects import Base, Channel, Video, WatchHistory

count_deleted_videos = 0
count_music_listens = 0


def debug_dump_data(session):
    # print("dumping...")
    # results = session.query(Video).all()
    # for r in results:
    #     print(r)

    # results = session.query(WatchHistory).all()
    # for r in results:
    #     print(r)

    # results = session.query(Channel).all()
    # for r in results:
    #     print(r)

    print(f"Videos: {session.query(Video).count()
                     } (Deleted: {count_deleted_videos})")
    print(f"Channels: {session.query(Channel).count()}")
    print(f"WatchHistorys: {session.query(WatchHistory).count()}")
    print(f"Music plays: {count_music_listens}")


# the Engine is a factory that can create new database connections for us
engine = create_engine("sqlite:///:memory:")  # , echo=True)

# generate DB schema at once in our target SQLite database
Base.metadata.create_all(bind=engine)

# get path to wath history JSON
current_directory = os.getcwd()
input_path_json = os.path.join(current_directory, "input/watch-history.json")

# parse the JSON
with open(input_path_json, 'r', encoding='utf-8') as file:
    history_data = json.load(file)

    # instantiate a database session
    with Session(engine) as session:

        entries_written = 0

        # write the data for each watch and video to the database
        for history_entry in history_data:

            if "subtitles" not in history_entry:
                # the video has been deleted
                count_deleted_videos += 1
                continue

            if history_entry["header"] == "YouTube Music":
                # this is a YouTube Music listen
                count_music_listens += 1
                continue

            video_id = history_entry["titleUrl"].split('=')[-1]
            video_title = history_entry["title"].replace("Watched ", "")

            subtitles = history_entry["subtitles"][0]

            channel_id = history_entry["subtitles"][0]["url"].split('/')[-1]
            channel_name = history_entry["subtitles"][0]["name"]

            watch_time = datetime.fromisoformat(history_entry["time"])

            watch_history = WatchHistory(watch_time, video_id)
            video = Video(video_id, video_title, channel_id)
            channel = Channel(channel_id, channel_name)

            session.merge(watch_history)
            session.merge(video)
            session.merge(channel)

            entries_written += 1

            if entries_written % 1000 == 0:
                session.commit()
                print(f"committed {entries_written}")

        session.commit()

        # output data written
        debug_dump_data(session)
