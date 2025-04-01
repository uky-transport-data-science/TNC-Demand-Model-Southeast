#### Negative Binomial Trip Generation and Trip Distribution
# Set working directory
import os
os.getcwd()

# Import Libraries
import warnings
warnings.simplefilter(action='ignore')
import numpy as np
import pandas as pd
pd.options.display.float_format = '{:.2f}'.format
import census
from census import Census
import io
import requests
import fiona
import geopandas as gpd
import json

## Read JSON file
with open('../model_config.json') as f:
    model_config = json.load(f)

## Pass Parameters
study_state = model_config["study_state"]
scenario_name = model_config["scenario_name"]
fare_adjust = model_config["fare_adjust"]
use_scaling_factor = model_config["scaling_factor"]

# Read in Data
print("Reading in linear pickup and destination choice data...")
pickups = pd.read_csv('../outputs/' + study_state + '_linear_pickups_' + scenario_name + '.csv')
dest_choice_logsums = pd.read_csv('../outputs/' + study_state + '_dest_choice_logsum_' + scenario_name + '.csv')
dest_choice_prob = pd.read_csv('../outputs/' + study_state + '_dest_choice_prob_' + scenario_name + '.csv')

# Merge data by geoid_origin
print("Merging data by origin...")
df = dest_choice_logsums.merge(pickups, on = "geoid_origin")
df.columns = df.columns.str.replace('_x', '')

# Apply negative binomial model to get pickups
print("Applying negative binomial model to get pickups...")
df['nt_pickups'] = np.exp(-1.699553*df['airport'] + 0.5047479*df['tourist'] + 0.3486627*df['nt_linear_pickups_log'] + 1.082214*df['nt_dc_logsum'] - 0.0173114*df['median_age'] + 0.0170123*df['pct_bach_25p'] + 0.000000716*df['total_emp_den'] + 0.2991526 - 5.691818) # +0.1
df['am_pickups'] = np.exp(-0.7743786*df['airport'] + 0.4779832*df['tourist'] + 0.4050372*df['am_linear_pickups_log'] + 0.6230226*df['am_dc_logsum'] - 0.0262*df['median_age'] + 0.0143772*df['pct_bach_25p']+ 0.000000498*df['total_emp_den'] + 0.3775664 - 1.946639) # +0.18
df['md_pickups'] = np.exp(-0.6405087*df['airport'] + 0.7809523*df['tourist'] + 0.3927277*df['md_linear_pickups_log'] + 0.6977969*df['md_dc_logsum'] - 0.0208753*df['median_age'] + 0.0123951*df['pct_bach_25p']+ 0.00000161*df['total_emp_den'] + 0.3918755 - 2.551229 - 0.3)
df['pm_pickups'] = np.exp(-0.4855696*df['airport'] + 0.890186*df['tourist'] + 0.4090155*df['pm_linear_pickups_log'] + 0.8352944*df['pm_dc_logsum'] - 0.0216488*df['median_age'] + 0.0149257*df['pct_bach_25p']+ 0.00000217*df['total_emp_den'] + 0.363544 - 4.089885 - 0.583894)
df['ev_pickups'] = np.exp(0.0188928*df['airport'] + 0.830838*df['tourist'] + 0.3445732*df['ev_linear_pickups_log'] + 0.9817033*df['ev_dc_logsum'] - 0.0215845*df['median_age'] + 0.0199614*df['pct_bach_25p']+ 0.00000224*df['total_emp_den'] + 0.4076045 - 5.265743) #+0.12

if use_scaling_factor == "True":
    print("Applying scalar factor...")
    scaling_factor = 0.7755538
    df['nt_pickups'] = scaling_factor*df['nt_pickups']
    df['am_pickups'] = scaling_factor*df['am_pickups']
    df['md_pickups'] = scaling_factor*df['md_pickups']
    df['pm_pickups'] = scaling_factor*df['pm_pickups']
    df['ev_pickups'] = scaling_factor*df['ev_pickups']
else:
    pass

# Apply probabilities
neg_bin_pred_trips = dest_choice_prob.merge(df, how = "left", on = "geoid_origin")
time_of_day = ["nt", "am", "md", "pm", "ev"]
for time in time_of_day:
    neg_bin_pred_trips[time + "_trips"] = neg_bin_pred_trips[time + "_pickups"] * neg_bin_pred_trips[time + "_prob"]

# Write to CSV
print("Writing to CSV...")
neg_bin_pred_trips_select = neg_bin_pred_trips[['geoid_origin', 'geoid_dest', 'nt_trips', 'am_trips', 'md_trips', 'pm_trips', 'ev_trips']]
neg_bin_pred_trips.to_csv('../outputs/' + study_state + '_neg_bin_pred_trips_' + scenario_name + '.csv', index = False)