import json
import os

from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass, Session

from db.objects import Base, Channel, Video, WatchHistory

def debug_dump_data(session):
    print("dumping...")
    results = session.query(Video).all()
    for r in results:
        print(r)
    
    results = session.query(WatchHistory).all()
    for r in results:
        print(r)

    results = session.query(Channel).all()
    for r in results:
        print(r)

# the Engine is a factory that can create new database connections for us
engine = create_engine("sqlite:///:memory:") #, echo=True)

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

        for history_entry in history_data:

            # write each video and its associated data to the DB
            video_id = history_entry["titleUrl"].split('=')[-1]
            video_title = history_entry["title"].replace("Watched ", "")

            subtitles = history_entry["subtitles"][0]
            channel_id = history_entry["subtitles"][0]["url"].split('/')[-1]     
            channel_name = history_entry["subtitles"][0]["name"]

            watch_time = datetime.strptime(
                history_entry["time"], '%Y-%m-%dT%H:%M:%S.%fZ')

            watch_history = WatchHistory(watch_time, video_id)
            video = Video(video_id, video_title, channel_id, [watch_history])
            channel = Channel(channel_id, channel_name, [video])

            print("\n\n")
            print(watch_history)
            print(video)
            print(channel)
            
            session.merge(channel)

            session.commit()

            # TODO - remove debug test
            entries_written += 1
            if entries_written > 100:
                break

        # output data written
        debug_dump_data(session)
        

