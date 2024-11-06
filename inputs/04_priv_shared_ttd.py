#### Calculate Private and Shared Travel Times and Distances
# Set working directory (make dynamic later)
import os
os.chdir('/mnt/e/CR2/Repos/TNC-Demand-Model-Southeast/inputs/')

# Import Libraries
import numpy as np
import pandas as pd
import census
from census import Censuss
import io
import requests
import fiona
import geopandas as gpd

def calc_priv_shared_ttd():
    # Read data
    print("Reading travel time/distance data...")
    travel_time_distance = pd.read_csv("../outputs/travel_time_distance.csv")

    # Private travel time is same as travel time
    print("Calculating private travel time...")
    travel_time_distance[["private_travel_time"]] = travel_time_distance[["travel_time"]]

    # Shared travel time is travel time + 4 min
    print("Calculating shared travel time...")
    travel_time_distance[["shared_travel_time"]] = travel_time_distance[["travel_time"]] + 4

    # Write out private and shared travel times
    priv_shared_ttd = travel_time_distance[["geoid_origin", "geoid_dest", "travel_time", "travel_distance", "private_travel_time", "shared_travel_time"]]
    priv_shared_ttd.to_csv("../outputs/priv_shared_ttd.csv", index = False)
    return priv_shared_ttd