#### Create Census Tract Centroids
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
import os
import io
import requests
import fiona
import geopandas as gpd
from shapely import wkt
import itertools
import json

## Read JSON file
with open('../model_config.json') as f:
    model_config = json.load(f)

## Pass Parameters
study_state = model_config["study_state"]
scenario_name = model_config["scenario_name"]
fare_adjust = model_config["fare_adjust"]

# FIPS Codes for States
AL = '01'
FL = '12'
GA = '13'
IL = '17'
KY = '21'
MA = '25'
MS = '28'
NC = '37'
SC = '45'
TN = '47'

states_list = [AL, FL, GA, IL, KY, MA, MS, NC, SC, TN]
states_string = ','.join(states_list)

fips_dict =  {'AL':'01',
              'FL':'12',
              'GA':'13',
              'IL':'17',
              'KY':'21',
              'MA':'25',
              'MS':'28',
              'NC':'37',
              'SC':'45',
              'TN':'47'}

fips_df = pd.DataFrame(fips_dict.items(), columns=['state_abb', 'fips_code'])

# If centroids have been created, move on!
if os.path.exists(os.getcwd() + "/" + study_state + "_centroid_points.csv"):
       print("The centroids for " + study_state + " exist. Moving on...")
else:
    # Load Data
    print("Getting geography data from TIGER line files...")
    centroid_load = []
    for i in states_list:
        url = 'https://www2.census.gov/geo/tiger/TIGER2019/TRACT/tl_2019_' + i + '_tract.zip'
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
    ## Filter by State 
    centroid = centroid[centroid['state_abb'].isin([study_state])]
    ## Convert geoid from object to int64
    centroid['geoid'] = centroid['geoid'].astype(np.int64)
    ## Only Cook County for Illinois 
    if study_state == "IL":
        centroid['fips_county'] = centroid['geoid'].astype(str).str[:5]
        centroid = centroid[(centroid['fips_county'] == '17031')]
        centroid = centroid.drop(columns=['fips_county'])
    else:
         pass

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
    if study_state == "MA":
        centroid_combos["temp_origin"] = centroid_combos["geoid_origin"].apply(lambda x: str(x)[:5])
        centroid_combos["temp_dest"] = centroid_combos["geoid_dest"].apply(lambda x: str(x)[:5])
        values_to_exclude = ['25007', '25019']
        centroid_combos = centroid_combos[~centroid_combos[['temp_origin', 'temp_dest']].isin(values_to_exclude).any(axis=1)]
        centroid_combos.drop(['temp_origin', 'temp_dest'], axis=1, inplace=True)
    else:
         pass
    centroid_combos.to_csv(os.getcwd() + "/" + study_state + "_centroid_points.csv", index = False)
    print("All finished, centroids output via CSV. Move on to creating graphs and creating travel times...")
 