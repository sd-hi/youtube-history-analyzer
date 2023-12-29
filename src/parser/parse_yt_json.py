import json
import os

# get path to wath history JSON
current_directory = os.getcwd()
input_path_json = os.path.join(current_directory, "input/watch-history.json")

# parse the JSON
with open(input_path_json, 'r', encoding='utf-8') as file:
    watch_history = json.load(file)

print(watch_history[0])