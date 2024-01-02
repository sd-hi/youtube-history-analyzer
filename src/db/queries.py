# generally useful queries
import pandas as pd

from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import Engine, func, text
from typing import List, Tuple

from src.db.objects import WatchHistory, Video

WEEKDAY_NAMES = ['Sunday', 'Monday', 'Tuesday',
                 'Wednesday', 'Thursday', 'Friday', 'Saturday']


def dbdate_str_to_datetime(isodate_string) -> datetime:
    iso_format = "%Y-%m-%d %H:%M:%S.%f%z"
    return datetime.strptime(isodate_string, iso_format)


def get_watchhistory_timestamp_range(db_engine: Engine) -> Tuple[datetime, datetime]:
    """
    Get date range for held history data
    """
    with Session(db_engine) as session:

        result = session.query(
            func.min(WatchHistory.timestamp).label('start_timestamp'),
            func.max(WatchHistory.timestamp).label('end_timestamp')
        ).first()

        start_datetime = dbdate_str_to_datetime(result.start_timestamp)
        end_datetime = dbdate_str_to_datetime(result.end_timestamp)

    return (start_datetime, end_datetime)


def get_watchhistory_count_per_month(db_engine: Engine) -> pd.DataFrame:
    """
    Get view counts for each month
    """

    with db_engine.connect() as conn:

        # get counts against each year-month combo (2021-04,1234)
        query = f"""
            SELECT
                strftime('%Y-%m', timestamp) AS year_month,
                COUNT(*) AS watch_count
            FROM
                watch_history
            GROUP BY
                year_month
            ORDER BY
                year_month
        """

        # get results from DB
        result = conn.execute(text(query)).fetchall()

        # transform results into pandas dataframe
        df = pd.DataFrame(result, columns=['year_month', 'watch_count'])

        return df


def get_watchhistory_count_per_weekday(db_engine: Engine) -> pd.DataFrame:
    """
    Get view counts for each weekday
    """

    with db_engine.connect() as conn:

        # get counts against each year-month combo (2021-04,1234)
        query = f"""
            SELECT
                strftime('%w', timestamp) AS weekday,
                COUNT(*) AS watch_count
            FROM
                watch_history
            GROUP BY
                weekday
            ORDER BY
                weekday
        """

        # get results from DB
        result = conn.execute(text(query)).fetchall()

        # transform results into pandas dataframe
        df = pd.DataFrame(result, columns=['weekday', 'watch_count'])

        # cast weekday column to integer an map to relevant day name
        df['weekday'] = df['weekday'].astype(int)
        df['weekday'] = df['weekday'].map(lambda dayno: WEEKDAY_NAMES[dayno])

        return df


def get_watchhistory_count_per_channel(db_engine: Engine) -> pd.DataFrame:
    """
    Get view counts for each channel
    """

    with db_engine.connect() as conn:

        query = f"""
            SELECT
                channels.name AS channel_name,
                COUNT(*) AS watch_count
            FROM
                watch_history
            INNER JOIN
                videos ON watch_history.videoid=videos.id
            INNER JOIN
                channels ON videos.channelid=channels.id
            GROUP BY
                channels.name
            ORDER BY
                watch_count DESC
            LIMIT 30
        """

        # get results from DB
        result = conn.execute(text(query)).fetchall()

        # transform results into pandas dataframe
        df = pd.DataFrame(result, columns=['channel_name', 'watch_count'])

        return df


def get_watchhistory_count_per_dayhour(db_engine: Engine) -> pd.DataFrame:
    """
    Get view counts for each hour in the day
    """

    with db_engine.connect() as conn:

        # get counts against each year-month combo (2021-04,1234)
        query = f"""
            SELECT
                strftime('%H', datetime(timestamp, 'localtime')) AS hour,
                COUNT(*) AS watch_count
            FROM
                watch_history
            GROUP BY
                hour
            ORDER BY
                hour
        """

        # get results from DB
        result = conn.execute(text(query)).fetchall()

        # transform results into pandas dataframe
        df = pd.DataFrame(result, columns=['hour', 'watch_count'])

        # convert to 12 hour clock for axis label
        df['hour'] = df['hour'].map(lambda hourno: datetime.strptime(
            str(hourno), "%H").strftime("%I %p"))

        return df


def get_watchhistory_for_month(db_engine: Engine, year, month, distinct_video_ids = True) -> List[WatchHistory]:
    """
    Get video IDs watched in given month
    """

    with Session(db_engine) as session:

        # get videos watched in the given month
        query = session.query(WatchHistory).filter(
            func.extract('year', WatchHistory.timestamp) == year,
            func.extract('month', WatchHistory.timestamp) == month
        )

        # only return each video ID once
        if distinct_video_ids:
            query.distinct(WatchHistory.videoid)
        
        result = query.all()
    
    return result
