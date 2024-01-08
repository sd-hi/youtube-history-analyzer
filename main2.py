from src.caching.populate import cache_videometas
from src.db.create import get_database_engine
from src.db.queries import get_watchhistory_count_per_channel, get_watchhistory_count_per_dayhour, get_watchhistory_count_per_month, get_watchhistory_count_per_weekday, get_watchhistory_for_month, get_watchhistory_timestamp_range
from src.ytapi.functions import ytapi_get_videos

# set up database
db_engine = get_database_engine()

# test code
watch_historys = get_watchhistory_for_month(db_engine, 2023, 12)
video_ids = [video.videoid for video in watch_historys]
cache_videometas(db_engine, video_ids)
