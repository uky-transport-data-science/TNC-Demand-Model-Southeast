#### Mode Choice Part 2
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
import glob
import requests
import fiona
import geopandas as gpd
import json
mode_choice_utility_logsums = __import__('06_mode_choice_step1')

## Read JSON file
with open('../model_config.json') as f:
    model_config = json.load(f)

## Pass Parameters
study_state = model_config["study_state"]
scenario_name = model_config["scenario_name"]
fare_adjust = model_config["fare_adjust"]
census_key = model_config["census_key"]

# Activate Census Key
c = Census(census_key)

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

def get_household_density(study_state):
    print("Getting household density per Census tract (S1901)...")
    if study_state == "IL":
        s1901_load = pd.DataFrame(c.acs5st.state_county_tract(fields = ('NAME', 'S1901_C01_001E'),
                                        state_fips = "17",
                                        county_fips = "031",
                                        tract = "*",
                                        year = 2019))
    else:
        s1901_load = pd.DataFrame(c.acs5st.state_county_tract(fields = ('NAME', 'S1901_C01_001E'),
                                            state_fips = states_string,
                                            county_fips = "*",
                                            tract = "*",
                                            year = 2019))
    s1901_load["geoid"] = s1901_load["state"] + s1901_load["county"] + s1901_load["tract"]
    # Convert GEOID to float.
    s1901_load["geoid"] = s1901_load.geoid.astype(float)
    households = s1901_load[["geoid", "S1901_C01_001E"]]
    households = households.rename({'S1901_C01_001E': 'households'}, axis='columns')

    # Get tract area data
    print("Getting geography data from TIGER line files...")
    tract_load = []
    for i in states_list:
        url = 'https://www2.census.gov/geo/tiger/TIGER2019/TRACT/tl_2019_' + i + '_tract.zip'
        df = gpd.read_file(url)
        df = df[['GEOID', 'STATEFP', 'ALAND']]
        tract_load.append(df)

    tract_load = pd.concat(tract_load)
    tract_load = tract_load.reset_index()
    tract_load = fips_df.merge(tract_load, left_on = "fips_code", right_on = "STATEFP")
    tract_load = tract_load[tract_load["state_abb"] == study_state]
    tract = tract_load[["GEOID","ALAND"]]
    tract.columns = map(str.lower, tract.columns)
    tract["geoid"] = tract.geoid.astype(float)

    households = pd.merge(tract, households, how="left", on = "geoid")
    households.loc[:, "density"] = households.loc[:, "households"] / (households.loc[:, "aland"] / 4046.85)
    households = households[["geoid", "density"]]
    households['origin_hh_density'] = households['density']
    households['dest_hh_density'] = households['density']
    households = households.drop(["density"], axis = "columns")
    origin_hh_density = households[["geoid", "origin_hh_density"]]
    dest_hh_density = households[["geoid", "dest_hh_density"]]
    return origin_hh_density, dest_hh_density


# Read in Data
print("Reading in negative binomial trip data..")
trips = pd.read_csv('../outputs/' + study_state + '_neg_bin_pred_trips_' + scenario_name + '.csv')
trips.columns
#sdf_check = trips[trips['geoid_origin'] == 21111980100]
#sdf_check.to_csv("../outputs/sdf_check.csv", index = False)
print("Reading in travel time data..")
traveltime = pd.read_csv('../outputs/' + study_state + '_fares_and_times_' + scenario_name + '.csv')
traveltime = traveltime[['geoid_origin', 'geoid_dest', 'private_travel_time', 'private_fares', 'shared_travel_time', 'shared_fares']]

print("Reading in median income data...")
median_inc = mode_choice_utility_logsums.get_median_income(study_state)

# Merge trips and income data
print("Merging trips and income data...")
origin_median_inc = median_inc[["geoid_origin", "median_income_origin"]]
origin_median_inc['geoid_origin'] = origin_median_inc.geoid_origin.astype(float)

dest_median_inc = median_inc[["geoid_dest", "median_income_dest"]]
dest_median_inc['geoid_dest'] = dest_median_inc.geoid_dest.astype(float)

trips = trips.merge(origin_median_inc, on = "geoid_origin")
trips = trips.merge(dest_median_inc, on = "geoid_dest")

# Merge trips and travel time
print("Merging trips and travel time data...")
trips = pd.merge(trips, traveltime, how = "left", on = ["geoid_origin", "geoid_dest"])

# Airport indicator
airport_coeffs = pd.read_csv("airports_coeff.csv")
airport_coeffs = airport_coeffs[["geoid", "coeff"]]
airport_coeffs = airport_coeffs.rename(columns={'coeff': 'airport_origin'})
airport_coeffs[["geoid_dest"]] = airport_coeffs[["geoid"]]
airport_coeffs[["airport_dest"]] = airport_coeffs[["airport_origin"]]
airport_coeffs = airport_coeffs.rename(columns={'geoid': 'geoid_origin'})
airport_coeffs_origin = airport_coeffs[["geoid_origin", "airport_origin"]]
airport_coeffs_dest = airport_coeffs[["geoid_dest", "airport_dest"]]
trips = pd.merge(trips, airport_coeffs_origin, on='geoid_origin', how='left')
trips = pd.merge(trips, airport_coeffs_dest, on='geoid_dest', how='left')
trips['airport_origin'].fillna(0, inplace=True)
trips['airport_dest'].fillna(0, inplace=True)
trips["airport"] = trips[['airport_origin', 'airport_dest']].max(axis=1)

# Use logit model to get probability
print("Applying logit model to get private/shared trips...")
shared_exp_utility =  np.exp(-0.85 - 0.08*trips['shared_travel_time'] - 0.14*trips['shared_fares'] - 0.06*trips['median_income_origin'] - 0.06*trips['median_income_dest'] - 2.88*trips['airport'])
private_exp_utility = np.exp(-0.85 - 0.08*trips['private_travel_time'] - 0.14*trips['private_fares'])
trips['shared_prob'] = shared_exp_utility / (shared_exp_utility + private_exp_utility)
trips['private_prob'] = 1 - trips[['shared_prob']]

# Get private and shared trips
priv_shared_trips = trips[['geoid_origin', 'geoid_dest', 'nt_trips', 'am_trips', 'md_trips', 'pm_trips', 'ev_trips', 'shared_prob', 'private_prob',"private_travel_time", "shared_travel_time", "private_fares", "shared_fares"]]
time_of_day = ["nt", "am", "md", "pm", "ev"]
mode_choices = ['private', 'shared']
for time in time_of_day:
    for mode in mode_choices:
        priv_shared_trips[mode + '_' + time + "_trips"] = priv_shared_trips[time + '_trips'] * priv_shared_trips[mode + '_prob']
print("Calculating private/shared trips by TOD...")

priv_shared_trips['shared_trips_total'] = priv_shared_trips['shared_nt_trips'] + priv_shared_trips['shared_nt_trips'] + priv_shared_trips['shared_am_trips'] + priv_shared_trips['shared_md_trips'] + priv_shared_trips['shared_pm_trips'] + priv_shared_trips['shared_ev_trips']

# Reading in data for matched/unmatched trips.
print("Merging household density data and creating matched/unmatched trips...")
origin_hh_density, dest_hh_density = get_household_density(study_state)
matched_trips = pd.merge(priv_shared_trips, origin_hh_density, left_on = ["geoid_origin"], right_on = ["geoid"])
matched_trips = pd.merge(matched_trips, dest_hh_density, left_on = ["geoid_dest"], right_on = ["geoid"])
# matched_trips = matched_trips.drop(["dest_hh_density_y"], axis = 1)
# matched_trips = matched_trips.rename({'dest_hh_density_x': 'dest_hh_density'}, axis='columns')
match_exp_u = np.exp(-1.45 + 0.148*matched_trips["shared_travel_time"] + 0.323*matched_trips["shared_trips_total"] + 0.012*matched_trips['origin_hh_density'] + 0.016*matched_trips["dest_hh_density"])
matched_trips["matched_prob"] = match_exp_u / (1 + match_exp_u)
matched_trips["unmatched_prob"] = 1 - matched_trips["matched_prob"]
time_of_day = ["nt", "am", "md", "pm", "ev"]
for time in time_of_day:
    matched_trips["matched_" + time + "_trips"] = matched_trips["shared_" + time + "_trips"] * matched_trips["matched_prob"]
    matched_trips["unmatched_" + time + "_trips"] = matched_trips["shared_" + time + "_trips"] * matched_trips["unmatched_prob"]
matched_trips = matched_trips.drop(["geoid_x", "geoid_y"], axis = "columns")
trips_wide = matched_trips
trips_wide.replace([np.inf, -np.inf], 0, inplace=True)
print("Creating wide dataframe and writing out to CSV...")
trips_wide.to_csv("../outputs/" + study_state + "_trips_final_wide_" + scenario_name + ".csv", index = False)

# Create long dataframe
print("Creating long dataframe and writing out to CSV...")
## Private Trips
private_trips = matched_trips[["geoid_origin", "geoid_dest", "private_nt_trips", "private_am_trips", "private_md_trips", "private_pm_trips", "private_ev_trips", "private_travel_time", "private_fares"]]
private_trips.columns = private_trips.columns.str.replace('private_', '') 
private_trips_od_ttf = private_trips[["geoid_origin", "geoid_dest", "travel_time", "fares"]]
private_trips = pd.melt(private_trips, id_vars=['geoid_origin', 'geoid_dest'], value_vars=['nt_trips', 'am_trips', 'md_trips', 'pm_trips', 'ev_trips'], var_name = 'time_of_day', value_name = 'trips')
private_trips['time_of_day'] = private_trips['time_of_day'].str[:2]
private_trips['trip_type'] = 'private'

### Join Travel Time and Fare Data (ttf)
private_trips = pd.merge(private_trips, private_trips_od_ttf, on=['geoid_origin', 'geoid_dest'], how='left')

## Matched Trips
only_matched_trips = matched_trips[["geoid_origin", "geoid_dest", "matched_nt_trips", "matched_am_trips", "matched_md_trips", "matched_pm_trips", "matched_ev_trips", "shared_travel_time", "shared_fares"]]
only_matched_trips.columns = only_matched_trips.columns.str.replace('matched_', '')
only_matched_trips.columns = only_matched_trips.columns.str.replace('shared_', '')
only_matched_trips_od_ttf = only_matched_trips[["geoid_origin", "geoid_dest", "travel_time", "fares"]]
only_matched_trips = pd.melt(only_matched_trips, id_vars=['geoid_origin', 'geoid_dest'], value_vars=['nt_trips', 'am_trips', 'md_trips', 'pm_trips', 'ev_trips'], var_name = 'time_of_day', value_name = 'trips')
only_matched_trips['time_of_day'] = only_matched_trips['time_of_day'].str[:2]
only_matched_trips['trip_type'] = 'matched'

### Join Travel Time and Fare Data (ttf)
only_matched_trips = pd.merge(only_matched_trips, only_matched_trips_od_ttf, on=['geoid_origin', 'geoid_dest'], how='left')

## Unmatched Trips
unmatched_trips = matched_trips[['geoid_origin', 'geoid_dest', "unmatched_nt_trips", "unmatched_am_trips", "unmatched_md_trips", "unmatched_pm_trips", "unmatched_ev_trips", "shared_travel_time", "shared_fares"]]
unmatched_trips.columns = unmatched_trips.columns.str.replace ('unmatched_', '') 
unmatched_trips.columns = unmatched_trips.columns.str.replace ('shared_', '') 
unmatched_trips_od_ttf = unmatched_trips[["geoid_origin", "geoid_dest", "travel_time", "fares"]]
unmatched_trips = pd.melt(unmatched_trips, id_vars=['geoid_origin', 'geoid_dest'], value_vars=['nt_trips', 'am_trips', 'md_trips', 'pm_trips', 'ev_trips'], var_name = 'time_of_day', value_name = 'trips')
unmatched_trips['time_of_day'] = unmatched_trips['time_of_day'].str[:2]
unmatched_trips['trip_type'] = 'unmatched'

### Join Travel Time and Fare Data (ttf)
unmatched_trips = pd.merge(unmatched_trips, unmatched_trips_od_ttf, on=['geoid_origin', 'geoid_dest'], how='left')

## Write out trips_long
trips_long = pd.concat([private_trips, only_matched_trips, unmatched_trips], ignore_index = True)
### Join with travel distance
travel_distance = pd.read_csv("../outputs/" + study_state + "_travel_time_distance.csv")
travel_distance = travel_distance[["geoid_origin", "geoid_dest",  "travel_distance"]]
trips_long = pd.merge(trips_long, travel_distance, on=['geoid_origin', 'geoid_dest'], how='left')
trips_long['shared'] = np.where(trips_long['trip_type'] == "private", "private", "shared")
trips_long.replace([np.inf, -np.inf], 0, inplace=True)
trips_long.to_csv("../outputs/" + study_state + "_trips_final_long_" + scenario_name + ".csv", index = False)

## Delete files
print("Deleting intermediate files...")
os.chdir('/mnt/e/CR2/Repos/TNC-Demand-Model-Southeast/outputs/')
patterns = ['*neg_bin*', '*dest_choice*', '*logsums*', '*linear*', '*matched_trips*']
files = [f for pattern in patterns for f in glob.glob(pattern)]
dir_path = os.getcwd()

# Iterate over the files and delete them
for file_name in files:
    file_path = os.path.join(dir_path, file_name)
    os.remove(file_path)

print("All finished!")


