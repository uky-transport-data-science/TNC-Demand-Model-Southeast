#### Calculate Fares for Private and Shared Trips
# Set working directory (make dynamic later)
import os
os.chdir('/mnt/e/CR2/Repos/TNC-Demand-Model-Southeast/inputs/')

# Import Libraries
import numpy as np
import pandas as pd
import census
from census import Census
import io
import requests
import fiona
import geopandas as gpd
priv_shared_ttd = __import__('04_priv_shared_ttd')

def priv_shared_fares():
    # Read in Data
    #trips = priv_shared_ttd.calc_priv_shared_ttd()
    trips = pd.read_csv('../outputs/priv_shared_ttd.csv')

    # Calculate trip fares
    ## Fares are a function of time and distance
    ## Private Trip Fare = 1.9035 + (0.2892)(travel time in minutes) + (0.8822)(distance in miles)
    print("Calculating private fares...")
    trips.loc[:, 'private_fares'] = 1.9035 + (0.2892 * trips['private_travel_time']) + (0.8822 * trips['travel_distance'])

    ## Shared Trip Fare = 2.6496 + (0.06)(travel time in minutes) + (0.7349)(distance in miles)
    print("Calculating shared fares...")
    trips.loc[:, 'shared_fares'] = 2.6496 + (0.06 * trips['shared_travel_time']) + (0.7349 * trips['travel_distance'])

    # Write out to CSV (optional)
    print("Writing out to CSV...")
    fares = trips
    fares.to_csv('../outputs/fares_and_times.csv', index = False)
    return fares