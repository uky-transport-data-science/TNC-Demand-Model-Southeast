#### Mode Choice Part 2
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
mode_choice_utility_logsums = __import__('06_mode_choice_utility_logsums')

# Activate Census Key
c = Census("4049ee84e96e784c0042da45d81f95514d53b7fd")

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

def get_household_density(study_state = "KY"):
    print("Getting household density per Census tract (S1901)...")
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
        url = 'https://www2.census.gov/geo/tiger/TIGER2020/TRACT/tl_2020_' + i + '_tract.zip'
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

def mode_choice_p2():
    # Read in Data
    print("Reading in negative binomial trip data..")
    trips = pd.read_csv('../outputs/neg_bin_pred_trips.csv')
    
    print("Reading in travel time data..")
    traveltime = pd.read_csv('../outputs/fares_and_times.csv')
    traveltime = traveltime[['geoid_origin', 'geoid_dest', 'private_travel_time', 'private_fares', 'shared_travel_time', 'shared_fares']]

    print("Reading in median income data...")
    median_inc = mode_choice_utility_logsums.get_median_income()

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
    ## These are the airports in Kentucky.
    airport_census_tracts = [21067004207, 21015980100, 21111980100] 
    # Order: LEX, CVG, SDF
    trips.loc[:, 'airport'] = np.where(trips['geoid_origin'].isin(airport_census_tracts), 1, np.where(trips['geoid_dest'].isin(airport_census_tracts), 1, 0))

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
    origin_hh_density, dest_hh_density = get_household_density(study_state = "KY")
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
    print("Creating wide dataframe and writing out to CSV...")
    trips_wide.to_csv("../outputs/trips_final_wide.csv", index = False)

    # Create long dataframe
    print("Creating long dataframe and writing out to CSV...")
    ## Private Trips
    private_trips = matched_trips[["geoid_origin", "geoid_dest", "private_nt_trips", "private_am_trips", "private_md_trips", "private_pm_trips", "private_ev_trips", "private_travel_time", "private_fares"]]
    private_trips.columns = private_trips.columns.str.replace('private_', '') 
    private_trips = pd.melt(private_trips, id_vars=['geoid_origin', 'geoid_dest'], value_vars=['nt_trips', 'am_trips', 'md_trips', 'pm_trips', 'ev_trips'], var_name = 'time_of_day', value_name = 'trips')
    private_trips['time_of_day'] = private_trips['time_of_day'].str[:2]
    private_trips['trip_type'] = 'private'

    ## Matched Trips
    only_matched_trips = matched_trips[["geoid_origin", "geoid_dest", "matched_nt_trips", "matched_am_trips", "matched_md_trips", "matched_pm_trips", "matched_ev_trips"]]
    only_matched_trips.columns = only_matched_trips.columns.str.replace('matched_', '')
    only_matched_trips = pd.melt(only_matched_trips, id_vars=['geoid_origin', 'geoid_dest'], value_vars=['nt_trips', 'am_trips', 'md_trips', 'pm_trips', 'ev_trips'], var_name = 'time_of_day', value_name = 'trips')
    only_matched_trips['time_of_day'] = only_matched_trips['time_of_day'].str[:2]
    only_matched_trips['trip_type'] = 'matched'

    ## Unmatched Trips
    unmatched_trips = matched_trips[['geoid_origin', 'geoid_dest', "unmatched_nt_trips", "unmatched_am_trips", "unmatched_md_trips", "unmatched_pm_trips", "unmatched_ev_trips"]]
    unmatched_trips.columns = unmatched_trips.columns.str.replace ('unmatched_', '') 
    unmatched_trips = pd.melt(unmatched_trips, id_vars=['geoid_origin', 'geoid_dest'], value_vars=['nt_trips', 'am_trips', 'md_trips', 'pm_trips', 'ev_trips'], var_name = 'time_of_day', value_name = 'trips')
    unmatched_trips['time_of_day'] = unmatched_trips['time_of_day'].str[:2]
    unmatched_trips['trip_type'] = 'unmatched'

    trips_long = pd.concat([private_trips, only_matched_trips, unmatched_trips], ignore_index = True)
    trips_long.to_csv("../outputs/trips_final_long.csv", index = False)

    print("All finished!")


