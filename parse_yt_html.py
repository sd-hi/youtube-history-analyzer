from bs4 import BeautifulSoup
import csv

INPUT_PATH_HTML = "input/sample.html"
OUTPUT_PATH_CSV = "output/history.csv"

FIELD_VIDEOID = "videoid"
FIELD_TITLE = "title"
FIELD_CHANNELID = "channelid"
FIELD_CHANNELNAME = "channelname"
FIELD_DATEWATCHED = "datewatched"
OUTPUT_FIELDS = [FIELD_VIDEOID, FIELD_TITLE,
                 FIELD_CHANNELID, FIELD_CHANNELNAME, FIELD_DATEWATCHED]

# open input HTML file to be parsed
with open(INPUT_PATH_HTML, 'r', encoding='utf-8') as file:
    raw_html = file.read()

# parse the file to get div for each watched video
soup = BeautifulSoup(raw_html, 'html.parser')
videos = soup.find_all('div', class_='outer-cell')

# open output CSV file
with open(OUTPUT_PATH_CSV, mode='w', newline='') as file:
    writer = csv.DictWriter(file)

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

        title = links[0].text.strip()
        video_url = links[0]['href']
        channel_name = links[1].text.strip()
        channel_link = links[1]['href']

        # the date watched is raw text after the last br tag in the div
        # convert to text and replace newlines with comma, then get last argument
        video_info_raw = video_info.get_text(separator=',')
        print(video_info_raw)
        if ',' in video_info_raw:
            date_watched = video_info_raw.split(',')[-1].lstrip().rstrip()
        else:
            date_watched = ''

        entry = {}
        entry[""]
        print(f'Title: {title}')
        print(f'Video URL: {video_url}')
        print(f'Channel Name: {channel_name}')
        print(f'Channel Link: {channel_link}')
        print(f'Date watched: {date_watched}')
        print('\n')
