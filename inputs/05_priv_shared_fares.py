#### Calculate Fares for Private and Shared Trips
# Import Libraries
import numpy as np
import pandas as pd
import census
from census import Census
import os
import io
import requests
import fiona
import geopandas as gpd

# Set working directory (make dynamic later)
os.chdir('/mnt/e/CR2/Repos/TNC-Demand-Model-Southeast/inputs/')

# Read in Data
trips = pd.read_csv('../outputs/priv_shared_ttd.csv')

# Calculate trip fares
## Fares are a function of time and distance
## Private Trip Fare = 1.9035 + (0.2892)(travel time in minutes) + (0.8822)(distance in miles)
trips.loc[:, 'private_fares'] = 1.9035 + (0.2892 * trips['private_travel_time']) + (0.8822 * trips['travel_distance'])

## Shared Trip Fare = 2.6496 + (0.06)(travel time in minutes) + (0.7349)(distance in miles)
trips.loc[:, 'shared_fares'] = 2.6496 + (0.06 * trips['shared_travel_time']) + (0.7349 * trips['travel_distance'])

# 