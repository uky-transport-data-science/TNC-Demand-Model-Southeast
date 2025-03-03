#### Trip Distribution (Destination Choice)
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
acs_lehd = __import__('01_acs_lehd')
import json

## Read JSON file
with open('../model_config.json') as f:
    model_config = json.load(f)

## Pass Parameters
study_state = model_config["study_state"]
scenario_name = model_config["scenario_name"]
fare_adjust = model_config["fare_adjust"]
census_key = model_config["census_key"]
ctpp_key = model_config["ctpp_key"]

# Get linear predicted dropoffs by TOD
print("Getting linear predicted dropoffs by TOD...")
dropoffs = acs_lehd.get_acs_lehd(study_state)
dropoffs['nt_pred_dropoffs'] = 545*dropoffs['airport'] + 0.07*dropoffs['food_emp'] + 0.00*dropoffs['other_emp'] + 0.28*dropoffs['hi_inc_0'] +  0.02*dropoffs['low_inc_0'] + 0.02*dropoffs['low_inc_1p'] + 0.00000454*dropoffs['hi_inc_1p']
dropoffs['am_pred_dropoffs'] = 616*dropoffs['airport'] + 0.04*dropoffs['food_emp'] + 0.02*dropoffs['retail_emp'] + 0.001*dropoffs['other_emp'] + 0.29*dropoffs['hi_inc_0'] + 0.0000102*dropoffs['hi_inc_1p']
dropoffs['md_pred_dropoffs'] = 1501*dropoffs['airport'] + 77*dropoffs['tourist'] + 0.20*dropoffs['food_emp'] + 0.08*dropoffs['retail_emp'] + 0.01*dropoffs['other_emp'] + 0.51*dropoffs['hi_inc_0'] + 0.01*dropoffs['low_inc_0'] + 0.01*dropoffs['low_inc_1p'] + 0.0000313*dropoffs['hi_inc_1p']
dropoffs['pm_pred_dropoffs'] = 308*dropoffs['airport'] + 56*dropoffs['tourist'] * 0.17*dropoffs['food_emp'] + 0.001*dropoffs['retail_emp'] + 0.00*dropoffs['other_emp'] + 0.4*dropoffs['hi_inc_0'] + 0.02*dropoffs['low_inc_0'] + 0.01*dropoffs['low_inc_1p'] + 0.00000658*dropoffs['hi_inc_1p']
dropoffs['ev_pred_dropoffs'] = 0.12*dropoffs['food_emp'] + 62*dropoffs['tourist'] + 0.47*dropoffs['hi_inc_0'] + 0.02*dropoffs['low_inc_0'] + 0.02*dropoffs['low_inc_1p'] + 0.00000694*dropoffs['hi_inc_1p']

dropoffs = dropoffs.rename(columns={"geoid": "geoid_dest"})
# Read in utitlity/probability/logsum data
print("Reading in utility/probability/logsum data...")
logsum = pd.read_csv('../outputs/' + study_state + '_mode_choice_utility_logsums_' + scenario_name + '.csv')
logsum = logsum[['geoid_origin', 'geoid_dest', 'travel_distance', 'mode_logsum_airport', 'mode_logsum_no_airport']]
logsum.head()

### Merge utility and dropoffs data together
print("Merge utility and dropoffs data together...")
df = pd.merge(logsum, dropoffs, on = "geoid_dest")
df['tourist'] = 0
# airport_list = [21067004207, # Lexington, KY
#                     21015980100, # Northern Kentucky, KY (Cincinnati, OH's airport is in Kentucky)
#                     21111980100, # Louisville, KY
#                     1073000400, # Birmingham, AL
#                     1101005901, # Montgomery, AL
#                     1089011200, # Huntsville, AL
#                     1097006403, # Mobile, AL
#                     12127092500, # Daytona Beach, FL
#                     12011080200, # Ft. Lauderdale, FL
#                     12071980000, # Fort Myers, FL
#                     12091021200, # Fort Walton Beach, FL
#                     12001001902, # Gainesville, FL
#                     12031010301, # Jacksonville, FL
#                     12087972000, # Key West, FL
#                     12009064700, # Melbourne, FL
#                     12086980500, # Miami, FL
#                     12095016802, # Orlando, FL
#                     12005000201, # Panama City Beach, FL
#                     12033001101, # Pensacola, FL
#                     12015010501, # Punta Gorda, FL
#                     12117021000, # Orlando-Sanford, FL
#                     12115001000, # Sarasota, FL
#                     12103024509, # St. Petersburg-Clearwater, FL
#                     12073002701, # Tallahasee, FL
#                     12057980600, # Tampa, FL
#                     12099980500] # West Palm Beach, FL
# df['airport'] = np.where(df.geoid_dest.isin([airport_list]), 1, 0)
airport_coeffs = pd.read_csv("airports_coeff.csv")
airport_coeffs = airport_coeffs[["geoid", "coeff"]]
airport_coeffs = airport_coeffs.rename(columns={'coeff': 'airport'})
airport_coeffs = airport_coeffs.rename(columns={'geoid': 'geoid_dest'})
df = df.drop('airport', axis=1)
df = pd.merge(df, airport_coeffs, on='geoid_dest', how='left')
df['airport'].fillna(0, inplace=True)
# acs_lehd['airport'] = np.where(acs_lehd.geoid.isin(airport_list), 1, 0)
df['internal'] = np.where(df['geoid_origin'] == df['geoid_dest'], 1, 0)

### Destination Choice Utility
print("Calculating destination choice utility by TOD...")
df['nt_utility'] = 1*np.log(df['nt_pred_dropoffs']) - 0.07*df['internal'] + 0.49*df['tourist'] - 2.81*df['airport'] + 0*df['mode_logsum_airport'] + 1*df['mode_logsum_no_airport']
df['am_utility'] = 1*np.log(df['am_pred_dropoffs']) - 0.8*df['internal'] + 0.47*df['tourist'] - 2.18*df['airport'] + 0.15*df['mode_logsum_airport'] + 0.85*df['mode_logsum_no_airport']
df['md_utility'] = 1*np.log(df['md_pred_dropoffs']) - 1.22*df['internal'] + 0.48*df['tourist'] - 2.84*df['airport'] + 0.08*df['mode_logsum_airport'] + 0.96*df['mode_logsum_no_airport']
df['pm_utility'] = 1*np.log(df['pm_pred_dropoffs']) - 1.20*df['internal'] + 0.23*df['tourist'] - 1.95*df['airport'] + 0.12*df['mode_logsum_airport'] + 0.72*df['mode_logsum_no_airport']
df['ev_utility'] = 1*np.log(df['ev_pred_dropoffs']) - 1.06*df['internal'] + 0.3*df['tourist'] - 2.18*df['airport'] + 0.16*df['mode_logsum_airport'] + 0.91*df['mode_logsum_no_airport']


### Exponentiated utility by TOD
print("Calculating exponentiated utility by TOD...")
time_of_day = ['nt', 'am', 'md', 'pm', 'ev']
for time in time_of_day:
    df[time + '_exp_utility'] = df[time + '_utility'].apply(np.exp)

### Sums of utilities by TOD and logsums
print("Get sums of utilities by TOD and logsums")
df["exp_utility_sum"] =  df["nt_exp_utility"] + df["am_exp_utility"] + df["md_exp_utility"] + df["pm_exp_utility"] + df["ev_exp_utility"]
df["dest_choice_logsum"] = np.log(df["exp_utility_sum"])

### Get probabilities
print("Calculating probabilities...")
for time in time_of_day:
    df[time + "_prob"] = df[time + "_exp_utility"] / df["exp_utility_sum"]       
df["prob_sum"] =  df["nt_prob"] + df["am_prob"] + df["md_prob"] + df["pm_prob"] + df["ev_prob"]

### Write to CSV
print("Writing to CSV...")
dest_choice = df[['geoid_origin', 'geoid_dest', 'dest_choice_logsum', 'nt_prob', 'am_prob', 'md_prob', 'pm_prob', 'ev_prob', 'airport', 'tourist', 'median_age', 'pct_bach_25p', 'total_emp_den']]
dest_choice.to_csv('../outputs/' + study_state + '_dest_choice_prob_logsum_' + scenario_name + '.csv', index = False)

