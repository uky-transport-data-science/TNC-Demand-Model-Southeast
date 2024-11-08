#### Negative Binomial Trip Generation and Trip Distribution
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

def neg_bin_trip_gen_dist(study_state, scenario_name):
    # Read in Data
    print("Reading in linear pickup and destination choice data...")
    pickups = pd.read_csv('../outputs/' + study_state + '_linear_pickups_' + scenario_name + '.csv')
    dest_choice = pd.read_csv('../outputs/' + study_state + '_dest_choice_prob_logsum_' + scenario_name + '.csv')
    # Merge data by geoid_origin
    print("Merging data by origin")
    df = dest_choice.merge(pickups, on = "geoid_origin")
    df = df[['geoid_origin', 'geoid_dest', 'dest_choice_logsum', 'nt_pred_pickups_log', 'am_pred_pickups_log', 'md_pred_pickups_log','pm_pred_pickups_log', 'ev_pred_pickups_log', 'pred_pickups_log', 'airport', 'tourist', 'median_age', 'pct_bach_25p', 'total_emp_den', 'nt_prob', 'am_prob', 'md_prob', 'pm_prob', 'ev_prob']]

    # Apply negative binomial model to get pickups
    print("Applying negative binomial model to get pickups...")
    df['nt_pickups'] = np.exp(-1.699553*df['airport'] + 0.5047479*df['tourist'] + 0.3486627*df['nt_pred_pickups_log'] + 1.082214*df['dest_choice_logsum'] - 0.0173114*df['median_age'] + 0.0170123*df['pct_bach_25p'] + 0.000000716*df['total_emp_den'] + 0.2991526 - 5.691818)
    df['am_pickups'] = np.exp(-0.7743786*df['airport'] + 0.4779832*df['tourist'] + 0.4050372*df['am_pred_pickups_log'] + 0.6230226*df['dest_choice_logsum'] - 0.0262*df['median_age'] + 0.0143772*df['pct_bach_25p']+ 0.000000498*df['total_emp_den'] + 0.3775664 - 1.946639)
    df['md_pickups'] = np.exp(-0.6405087*df['airport'] + 0.7809523*df['tourist'] + 0.3927277*df['md_pred_pickups_log'] + 0.6977969*df['dest_choice_logsum'] - 0.0208753*df['median_age'] + 0.0123951*df['pct_bach_25p']+ 0.00000161*df['total_emp_den'] + 0.3918755 - 2.551229)
    df['pm_pickups'] = np.exp(-0.4855696*df['airport'] + 0.890186*df['tourist'] + 0.4090155*df['pm_pred_pickups_log'] + 0.8352944*df['dest_choice_logsum'] - 0.0216488*df['median_age'] + 0.0149257*df['pct_bach_25p']+ 0.00000217*df['total_emp_den'] + 0.363544 - 4.089885)
    df['ev_pickups'] = np.exp(0.0188928*df['airport'] + 0.830838*df['tourist'] + 0.3445732*df['ev_pred_pickups_log'] + 0.9817033*df['dest_choice_logsum'] - 0.0215845*df['median_age'] + 0.0199614*df['pct_bach_25p']+ 0.00000224*df['total_emp_den'] + 0.4076045 - 5.265743)

    # Get TOD probabilities
    print("Get TOD probabilities...")
    time_of_day = ["nt", "am", "md", "pm", "ev"]
    for time in time_of_day:
        df[time + "_trips"] = df[time + "_pickups"] * df[time + "_prob"]
    
    # Write to CSV
    print("Writing to CSV...")
    neg_bin_pred_trips = df[['geoid_origin', 'geoid_dest', 'nt_trips', 'am_trips', 'md_trips', 'pm_trips', 'ev_trips']]
    neg_bin_pred_trips.to_csv('../outputs/' + study_state + '_neg_bin_pred_trips_' + scenario_name + '.csv', index = False)