#### Calculate Private and Shared Travel Times
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

# Read data
travel_time_distance = pd.read_csv("../outputs/travel_time_distance.csv")
travel_time_distance = travel_time_distance[travel_time_distance['geoid_origin'] != travel_time_distance['geoid_dest']]
# Private travel time is same as travel time
travel_time_distance[["private_travel_time"]] = travel_time_distance[["travel_time"]]

# Shared travel time is travel time + 4 min
travel_time_distance[["shared_travel_time"]] = travel_time_distance[["travel_time"]] + 4

# Write out private and shared travel times
priv_shared_ttd = travel_time_distance[["geoid_origin", "geoid_dest", "travel_time", "travel_distance", "private_travel_time", "shared_travel_time"]]
priv_shared_ttd.to_csv("../outputs/priv_shared_ttd.csv", index = False)