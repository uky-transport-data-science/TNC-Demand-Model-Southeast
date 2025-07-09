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
pd.set_option('display.max_columns', None)
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
#dropoffs = acs_lehd.get_acs_lehd(study_state)
dropoffs =  pd.read_csv("../outputs/" + study_state + "_acs_lehd_" + scenario_name + ".csv")

# Get city of Chicago
dropoffs.head()
if study_state == 'IL':
   chicago_tracts = pd.read_csv("../comparison/from_dropbox_md.csv")
   chicago_tracts = chicago_tracts["ORIGIN"].unique()
   dropoffs = dropoffs[dropoffs['geoid'].isin(chicago_tracts)]
else:
    pass

for col in dropoffs.select_dtypes(include=['object']).columns:
    try:
        dropoffs[col] = pd.to_numeric(dropoffs[col], errors='coerce')
    except ValueError:
        print(f"Could not convert column '{col}' to float.")

dropoffs['nt_pred_dropoffs'] = 545*dropoffs['airport'] + 0.07*dropoffs['food_emp'] + 0.00*dropoffs['other_emp'] + 0.28*dropoffs['hi_inc_0'] +  0.02*dropoffs['low_inc_0'] + 0.02*dropoffs['low_inc_1p'] + 0.00000454*dropoffs['hi_inc_1p']
dropoffs['am_pred_dropoffs'] = 616*dropoffs['airport'] + 0.04*dropoffs['food_emp'] + 0.02*dropoffs['retail_emp'] + 0.001*dropoffs['other_emp'] + 0.29*dropoffs['hi_inc_0'] + 0.0000102*dropoffs['hi_inc_1p']
dropoffs['md_pred_dropoffs'] = 1501*dropoffs['airport'] + 77*dropoffs['tourist'] + 0.20*dropoffs['food_emp'] + 0.08*dropoffs['retail_emp'] + 0.01*dropoffs['other_emp'] + 0.51*dropoffs['hi_inc_0'] + 0.01*dropoffs['low_inc_0'] + 0.01*dropoffs['low_inc_1p'] + 0.0000313*dropoffs['hi_inc_1p']
dropoffs['pm_pred_dropoffs'] = 308*dropoffs['airport'] + 56*dropoffs['tourist'] * 0.17*dropoffs['food_emp'] + 0.001*dropoffs['retail_emp'] + 0.00*dropoffs['other_emp'] + 0.4*dropoffs['hi_inc_0'] + 0.02*dropoffs['low_inc_0'] + 0.01*dropoffs['low_inc_1p'] + 0.00000658*dropoffs['hi_inc_1p']
dropoffs['ev_pred_dropoffs'] = 0.12*dropoffs['food_emp'] + 62*dropoffs['tourist'] + 0.47*dropoffs['hi_inc_0'] + 0.02*dropoffs['low_inc_0'] + 0.02*dropoffs['low_inc_1p'] + 0.00000694*dropoffs['hi_inc_1p']

dropoffs = dropoffs.rename(columns={"geoid": "geoid_dest"})
# Read in utitlity/probability/logsum data
print("Reading in utility/probability/logsum data...")
logsum = pd.read_csv('../outputs/' + study_state + '_mode_choice_utility_logsums_' + scenario_name + '.csv')
# City of Chicago Only
if study_state == 'IL':
   chicago_tracts = pd.read_csv("../comparison/from_dropbox_md.csv")
   chicago_tracts = chicago_tracts["ORIGIN"].unique()
   logsum = logsum[logsum['geoid_origin'].isin(chicago_tracts) & logsum['geoid_dest'].isin(chicago_tracts)]
else:
    pass

logsum = logsum[['geoid_origin', 'geoid_dest', 'travel_distance', 'mode_logsum_airport', 'mode_logsum_no_airport']]
logsum.head()

### Merge utility and dropoffs data together
print("Merge utility and dropoffs data together...")
df = pd.merge(logsum, dropoffs, on = "geoid_dest")

### Add internal data
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
    
### Sum exp utils across all possible destinations, within each TOD, then take the log
## Get exp utilities
df_exp_utility = df[["geoid_origin", "nt_exp_utility", "am_exp_utility", "md_exp_utility", "pm_exp_utility", "ev_exp_utility"]]
df_exp_utility.head() 

df_sum_exp_utility = df_exp_utility.groupby(['geoid_origin']).sum()
df_sum_exp_utility.head()
## String to check for
string_to_check = 'exp_utility'

## Iterate through columns and add prefix if the string is found
for col in df_sum_exp_utility.columns:
    if string_to_check in col:
        df_sum_exp_utility.rename(columns={col: 'sum_' + col}, inplace=True)

for time in time_of_day:
    df_sum_exp_utility[time + '_dc_logsum'] = np.log(df_sum_exp_utility['sum_' + time + '_exp_utility'])

df_sum_exp_utility = df_sum_exp_utility.reset_index()
df_sum_exp_utility
# write out a dataframe with just the dc logsums and one row for each origin
print("Writing to CSV...")
df_dc_logsums = df_sum_exp_utility[['geoid_origin', 'nt_dc_logsum', 'am_dc_logsum', 'md_dc_logsum', 'pm_dc_logsum', 'ev_dc_logsum']]
df_dc_logsums.to_csv('../outputs/' + study_state + '_dest_choice_logsum_' + scenario_name + '.csv', index = False)

### Get probabilities
print("Calculating probabilities...")
## Merge the sum of exp utils back to the matrix (these are the row sums) via the origin
# Calcuclate prob as exp_util / rowsum
df = pd.merge(df, df_sum_exp_utility, on = "geoid_origin", how = "left")

for time in time_of_day:
    df[time + "_prob"] = df[time + "_exp_utility"] / df['sum_' + time + '_exp_utility']      

# df_prob = df[["geoid_origin", 'nt_prob', 'am_prob', 'md_prob', 'pm_prob', 'ev_prob']]
# check that they sum to 1
#df_prob.groupby(['geoid_origin']).sum()

### Write to CSV
print("Writing to CSV...")
dest_choice_prob = df[['geoid_origin', 'geoid_dest', 
                  'nt_prob', 'am_prob', 'md_prob', 'pm_prob', 'ev_prob', 
                  'airport', 'tourist', 'median_age', 'pct_bach_25p', 'total_emp_den']]
dest_choice_prob.to_csv('../outputs/' + study_state + '_dest_choice_prob_' + scenario_name + '.csv', index = False)

