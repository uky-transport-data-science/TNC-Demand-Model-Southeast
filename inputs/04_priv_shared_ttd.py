#### Calculate Private and Shared Travel Times and Distances
# Set working directory
import os
os.getcwd()

# Import Libraries
import warnings
warnings.simplefilter(action='ignore')
import numpy as np
import pandas as pd
import census
from census import Census
import io
import requests
import fiona
import geopandas as gpd
import json

## Read JSON file
with open('../model_config.json') as f:
    model_config = json.load(f)

## Pass Parameters
study_state = model_config["study_state"]
scenario_name = model_config["scenario_name"]
fare_adjust = model_config["fare_adjust"]

print(study_state)
print(scenario_name)
print(fare_adjust)

# Read data
print("Reading travel time/distance data...")
travel_time_distance = pd.read_csv("../outputs/" + study_state + "_travel_time_distance.csv")

# Private travel time is same as travel time
print("Calculating private travel time...")
travel_time_distance[["private_travel_time"]] = travel_time_distance[["travel_time"]]

# Shared travel time is travel time + 4 min
print("Calculating shared travel time...")
travel_time_distance[["shared_travel_time"]] = travel_time_distance[["travel_time"]] + 4

# Write out private and shared travel times
priv_shared_ttd = travel_time_distance[["geoid_origin", "geoid_dest", "travel_time", "travel_distance", "private_travel_time", "shared_travel_time"]]
priv_shared_ttd.to_csv("../outputs/" + study_state + "_priv_shared_ttd.csv", index = False)