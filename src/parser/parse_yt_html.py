from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import csv
import re

INPUT_PATH_HTML = "tests/cr_in_title.html"
OUTPUT_PATH_CSV = "output/history.csv"

FIELD_VIDEOID = "videoid"
FIELD_TITLE = "title"
FIELD_CHANNELID = "channelid"
FIELD_CHANNELNAME = "channelname"
FIELD_WATCHEDTIMESTAMP = "watched"
OUTPUT_FIELDS = [FIELD_VIDEOID, FIELD_TITLE,
                 FIELD_CHANNELID, FIELD_CHANNELNAME, FIELD_WATCHEDTIMESTAMP]


def timestamp_to_utc(yt_timestamp):
    # convert youtube timestamp to ISO timestamp for UTC

    # account for quirks in YT output format
    yt_timestamp = yt_timestamp.replace("Sept", "Sep")

    # set input format
    input_format = "%d %b %Y, %H:%M:%S GMT%z"

    # parse date and time
    dt_object = datetime.strptime(yt_timestamp, input_format)

    # offset to UTC
    dt_utc = dt_object - dt_object.utcoffset()

    # format as ISO timestamp
    output_format = "%Y-%m-%dT%H:%M:%SZ"
    utc_iso_timestamp = dt_utc.strftime(output_format)

    return utc_iso_timestamp

def sanitize_text(video_title):
    # sanitize text such as video title for CSV

    # clean up newlines and extra whitespace
    video_title = video_title.strip().replace("\n", "").replace("\r", "")

    # reduce duplicated spaces
    video_title = re.sub(r'\s+', ' ', video_title)

    return video_title

# open input HTML file to be parsed
with open(INPUT_PATH_HTML, 'r', encoding='utf-8') as input_file:
    raw_html = input_file.read()

# parse the file to get div for each watched video
soup = BeautifulSoup(raw_html, 'html.parser')
videos = soup.find_all('div', class_='outer-cell')

# open output CSV file
with open(OUTPUT_PATH_CSV, encoding='utf-8', mode='w', newline='') as output_file:

    writer = csv.DictWriter(output_file, fieldnames=OUTPUT_FIELDS)
    writer.writeheader()

    # iterate through videos in watch history
    for video in videos:

        # get the main content cell containing video info
        video_info = video.find('div', class_='content-cell')

        # get the links in this video's div
        links = video_info.findAll('a')
        if len(links) == 0:
            # no links found, must be deleted video
            continue

        if len(links) == 1:
            # video link exists, but channel was terminated
            continue

        video_title = sanitize_text(links[0].text)
        video_url = links[0]['href']
        channel_name = sanitize_text(links[1].text)
        channel_link = links[1]['href']

        # the date watched is raw text after the last br tag in the div
        # convert to text and replace newlines with comma, then get last argument
        video_info_text = video_info.get_text(separator='|')
        if '|' in video_info_text:
            watched_timestamp_yt = video_info_text.split(
                '|')[-1].lstrip().rstrip()
            watched_timestamp_iso = timestamp_to_utc(watched_timestamp_yt)
        else:
            watched_timestamp_iso = '0000-00-00T00:00:00'

        history_entry = {}
        history_entry[FIELD_CHANNELID] = channel_link.split('/')[-1]
        history_entry[FIELD_CHANNELNAME] = channel_name
        history_entry[FIELD_WATCHEDTIMESTAMP] = watched_timestamp_iso
        history_entry[FIELD_TITLE] = video_title
        history_entry[FIELD_VIDEOID] = video_url.split('=')[-1]

        writer.writerow(history_entry)

        print(f'Title: {video_title}\tDate: {watched_timestamp_iso}')
