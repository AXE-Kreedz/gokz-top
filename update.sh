#!/bin/bash

# Read the JSON file and extract the Steam IDs
steamids=$(jq -r '.[]' jsons/players_steamids.json)

# Iterate over the Steam IDs
for steamid in $steamids
do
  # Call your Python script with the Steam ID as an argument
  python update_player_records.py $steamid
done