# integration with v3 YouTube API

import json
import os
import requests

from datetime import datetime
from dotenv import load_dotenv
from isodate import parse_duration
from typing import List

from src.db.objects import VideoMeta

YT_API_BASE_URL = 'https://www.googleapis.com/youtube/v3'  # URL for YouTube API
YT_API_MAX_VIDEOS = 50  # maximum video IDs to request in single call


def extract_json_tag_value(data, *keys, default="0"):
    # try extracting JSON value based on path of keys
    try:
        for key in keys:
            data = data[key]
        return data
    except (KeyError, TypeError):
        # failed to find key, return default value
        print(f"returning {default}")
        return default


def iso_duration_to_seconds(duration_string):
    # try to convert given ISO duration to seconds
    try:
        duration_seconds = parse_duration(duration_string).total_seconds()
    except:
        duration_seconds = 0

    return duration_seconds


def ytapi_apitoken():
    """
    Return API token for current session
    """
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    return api_key


def ytapi_get_videos(video_ids) -> List[VideoMeta]:
    """
    Get data for given set of video IDs
    """
    videometas = []

    url = YT_API_BASE_URL + '/videos'
    headers = {
        'X-goog-api-key': f'{ytapi_apitoken()}',
        'Accept': 'application/json'
    }
    parameters = {
        'part': 'snippet,contentDetails,statistics',
        'id': {",".join(video_ids)}
    }

    print(f"Getting {len(video_ids)} videos: {",".join(video_ids)}")

    response = requests.get(url, params=parameters, headers=headers)

    if response.status_code == 200:
        response_json = response.json()

        for item in response_json.get("items", []):

            videometa = VideoMeta(

                # caching info
                cachedate=datetime.utcnow(),
                videoexists=True,

                # metadata
                id=item["id"],
                commentcount=int(extract_json_tag_value(
                    item, "statistics", "commentCount")),
                duration=iso_duration_to_seconds(extract_json_tag_value(
                    item, "contentDetails", "duration")),
                likecount=int(extract_json_tag_value(
                    item, "statistics", "likeCount")),
                viewcount=int(extract_json_tag_value(
                    item, "statistics", "viewCount")),
            )

            videometas.append(videometa)

    else:
        print(f"Error: {response.status_code}")
        print(response.text)

    return videometas
