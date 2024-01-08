# functions to cache data into local database

from datetime import datetime
from sqlalchemy.orm import Session

from src.db.objects import VideoMeta
from src.ytapi.functions import YT_API_MAX_VIDEOS, ytapi_get_videos


def cache_videometas(db_engine, videoids, max_chunk_size=YT_API_MAX_VIDEOS):
    """
    Cache video metadata not already present in database
    """

    print(f"Video IDs requested to cache: {
          len(videoids)} ({len(set(videoids))} unique)")

    with Session(db_engine) as session:

        # check which videos exist in the database already
        result = session.query(VideoMeta.id).filter(
            VideoMeta.id.in_(videoids)).all()
        videoids_existing = [tup[0] for tup in result]

        # determine which video IDs we need to cache into the database
        videoids_to_cache = list(
            set(videoids).difference(videoids_existing))

    print(f"Videos in cache already: {len(videoids_existing)}")
    print(f"Videos to to be cached: {len(videoids_to_cache)}")

    # work through the list of requested videos in chunks
    videometas_from_api = []

    elem_start = 0
    elem_end = 1
    while elem_end < len(videoids_to_cache) + 1:

        call_api_now = False

        current_chunk_size = elem_end - elem_start
        if current_chunk_size >= max_chunk_size:
            # maximum API request size reached
            call_api_now = True

        elif elem_end >= len(videoids_to_cache):
            # no more videos to request
            call_api_now = True

        if call_api_now:
            # get the chunk of videos from the API
            print(f"Requesting {current_chunk_size} videos from API")

            api_call_videometas = ytapi_get_videos(
                videoids_to_cache[elem_start:elem_end])

            print(f"Received {len(api_call_videometas)} videos from API")

            # add them to the collection of videos downloaded from the API in this instance
            videometas_from_api.extend(api_call_videometas)

            # move start pointer for next API call
            elem_start = elem_end

        # move to next video ID
        elem_end += 1

    # write data to our cache
    with Session(db_engine) as session:

        # flush the videos obtained from the API to database
        for videometa in videometas_from_api:
            session.merge(videometa)
        session.commit()

        # confirm which video IDs were returned by the API
        videoids_from_api = [videometa.id for videometa in videometas_from_api]

        # identify which of those the API never returned
        videoids_missing = set(
            videoids_to_cache).difference(videoids_from_api)

        print(f"Videos provided by API: {len(videoids_from_api)}")
        print(f"Videos missing from API: {len(videoids_missing)}")

        print("BREAKING OUT before writing to DB")
        exit()

        for videoid_missing in videoids_missing:
            # write a placeholder database entry for missing video
            videometa = VideoMeta(

                # caching info
                cachedate=datetime.utcnow(),
                videoexists=False,

                # metadata
                id=videoid_missing,
                commentcount=0,
                duration=0,
                likecount=0,
                viewcount=0,
            )
