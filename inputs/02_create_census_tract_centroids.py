#### Create Census Tract Centroids
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
from shapely import wkt
import itertools

# Set working directory
os.chdir('/mnt/e/CR2/Repos/TNC-Demand-Model-Southeast/inputs/')

# FIPS Codes for States
AL = '01'
FL = '12'
GA = '13'
KY = '21'
MS = '28'
NC = '37'
SC = '45'
TN = '47'

states_list = [AL, FL, GA, KY, MS, NC, SC, TN]
states_string = ','.join(states_list)

fips_dict =  {'AL':'01',
              'FL':'12',
              'GA':'13',
              'KY':'21',
              'MS':'28',
              'NC':'37',
              'SC':'45',
              'TN':'47'}

fips_df = pd.DataFrame(fips_dict.items(), columns=['state_abb', 'fips_code'])

def create_centroids(study_state = "KY"):
    # Load Data
    print("Getting geography data from TIGER line files...")
    centroid_load = []
    for i in states_list:
        url = 'https://www2.census.gov/geo/tiger/TIGER2020/TRACT/tl_2020_' + i + '_tract.zip'
        df = gpd.read_file(url)
        df = df[['GEOID', 'STATEFP', 'geometry']]
        centroid_load.append(df)

    centroid_load = pd.concat(centroid_load)
    centroid_load = centroid_load.reset_index()

    # Clean Data
    print("Cleaning data...")
    centroid_load = centroid_load.drop(columns=["index"])
    centroid_load.columns = map(str.lower, centroid_load.columns)
    ## Merge with FIPS df
    centroid = pd.merge(centroid_load, fips_df, left_on = 'statefp', right_on = 'fips_code')
    ## Filter by State (MAKE ARGUMENT)
    centroid = centroid[centroid['state_abb'].isin(["KY"])]
    ## Convert geoid from object to int64
    centroid['geoid'] = centroid['geoid'].astype(np.int64)

    # Get Centroids
    print("Creating centroids...")
    centroid["centroid"] = centroid["geometry"].centroid
    centroid['centroid'] = centroid.centroid.apply(lambda x: wkt.dumps(x))
    centroid = centroid.join(centroid['centroid'].str.extract(r'(?P<x>-?\d+\.\d+) (?P<y>-?\d+\.\d+)'))
    ## Convert x and y to floats
    centroid[["x", "y"]] = centroid[["x", "y"]].astype(float)
    ## Keep relevant columns
    centroid = centroid.drop(columns = ["statefp", "geometry", "fips_code", "centroid"])
    origins = centroid[['geoid', 'x', 'y']].values.tolist()
    destinations = centroid[['geoid', 'x', 'y']].values.tolist()
    combinations = list(itertools.product(origins, destinations))
    combos_list = []
    for i in range(0, len(combinations)-1):
        combos_list.append(list(itertools.chain(*combinations[i])))
    centroid_combos = pd.DataFrame(combos_list, columns=['geoid_origin', 'origin_x', 'origin_y', 'geoid_dest', 'dest_x', 'dest_y'])
    centroid_combos.to_csv(os.getcwd() + "/centroid_points.csv", index = False)
    print("All finished, centroids output via CSV. Move on to creating graphs and creating travel times...")

