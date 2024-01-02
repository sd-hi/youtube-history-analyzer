# integration with v3 YouTube API

import json
import os
import requests

from dotenv import load_dotenv

YT_API_BASE_URL = 'https://www.googleapis.com/youtube/v3'


def ytapi_apitoken():
    """
    Return API token for current session
    """
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    print(f"API key: {api_key}")
    return api_key


def ytapi_get_videos(video_ids):
    """
    Get data for given set of video IDs
    """

    url = YT_API_BASE_URL + '/videos'
    headers = {
        'X-goog-api-key': f'{ytapi_apitoken()}',
        'Accept': 'application/json'
    }
    parameters = {
        'part': 'snippet,contentDetails,statistics',
        'id': {",".join(video_ids)}
    }

    response = requests.get(url, params=parameters, headers=headers)

    if response.status_code == 200:
        response_json = response.json()

        for item in response_json.get("items", []):
            print(item.get("etag"))

    else:
        print(f"Error: {response.status_code}")
        print(response.text)
