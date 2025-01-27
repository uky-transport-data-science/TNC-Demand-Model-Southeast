#### Calculate Fares for Private and Shared Trips
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

# Read in Data
#trips = priv_shared_ttd.calc_priv_shared_ttd()
trips = pd.read_csv('../outputs/' + study_state + '_priv_shared_ttd.csv')

# Calculate trip fares
## Fares are a function of time and distance
## Private Trip Fare = 1.9035 + (0.2892)(travel time in minutes) + (0.8822)(distance in miles)
print("Calculating private fares...")
trips.loc[:, 'private_fares'] = 1.9035 + (0.2892 * trips['private_travel_time']) + (0.8822 * trips['travel_distance'])
trips.loc[:, 'private_fares'] = trips.loc[:, 'private_fares'] * fare_adjust

## Shared Trip Fare = 2.6496 + (0.06)(travel time in minutes) + (0.7349)(distance in miles)
print("Calculating shared fares...")
trips.loc[:, 'shared_fares'] = 2.6496 + (0.06 * trips['shared_travel_time']) + (0.7349 * trips['travel_distance'])
trips.loc[:, 'shared_fares'] = trips.loc[:, 'shared_fares'] * fare_adjust

# Write out to CSV (optional)
print("Writing out to CSV...")
fares = trips
fares.to_csv('../outputs/' + study_state + '_fares_and_times_' + scenario_name + '.csv', index = False)
