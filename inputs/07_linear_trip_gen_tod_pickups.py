#### Linear Trip Generation (Pickups by Time of Day)
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


# Get linear predicted pickups by TOD
print("Get linear predicted pickups by TOD...")
pickups = acs_lehd.get_acs_lehd(study_state)
### Adjusting airport pickups by e^(coefficient for airport in negative binomial for pickups, lines 40-44 in 09).
## Update 2/17: updating coefficients to account for rounding. https://github.com/alex-mucci/TNC-Demand-Model-Application/blob/main/Apply_Trip_Generation.py
pickups['nt_pred_pickups'] = 260.4035*pickups['airport'] +  0.1251485*pickups['food_emp'] + 0.1456829*pickups['hi_inc_0'] +  0.0055992*pickups['low_inc_0'] + 0.0206288*pickups['low_inc_1p']
pickups['am_pred_pickups'] = 130.2076*pickups['airport'] + 53.18332*pickups['tourist'] +0.0473473*pickups['food_emp'] + 0.015827*pickups['retail_emp'] + 0.0000952*pickups['other_emp'] + 0.37*pickups['hi_inc_0'] +  0.0174729*pickups['low_inc_0'] + 0.0176063*pickups['low_inc_1p'] + 0.0000136*pickups['hi_inc_1p']
pickups['md_pred_pickups'] = 921.3699*pickups['airport'] + 173.4502*pickups['tourist'] + 0.1485942*pickups['food_emp'] + 0.0653171*pickups['retail_emp'] + 0.0075034*pickups['other_emp'] + 0.6336939*pickups['hi_inc_0'] +  0.0275177*pickups['low_inc_0'] + 0.0235304*pickups['low_inc_1p'] + 0.0000243*pickups['hi_inc_1p']
pickups['pm_pred_pickups'] = 213.2107*pickups['airport'] + 102.1033*pickups['tourist'] + 0.1094589*pickups['food_emp'] + 0.0385694*pickups['retail_emp'] + 0.0079508*pickups['other_emp'] + 0.44*pickups['hi_inc_0'] + 0.0060732*pickups['low_inc_0'] + 0.0072242*pickups['low_inc_1p'] + 0.0000164*pickups['hi_inc_1p']
pickups['ev_pred_pickups'] = 476.2219*pickups['airport'] + 0.1846295*pickups['food_emp'] + 0.00273*pickups['other_emp'] + 0.35*pickups['hi_inc_0'] +  0.0070386*pickups['low_inc_0'] + 0.0076753*pickups['low_inc_1p'] + 0.00000446*pickups['hi_inc_1p']

# Sum pickups by TOD to get total pickups
pickups['pred_pickups'] =  pickups[['am_pred_pickups', 'nt_pred_pickups', 'md_pred_pickups', 'pm_pred_pickups', 'ev_pred_pickups']].sum(axis=1)

# Rename geoid to geoid_origin
pickups.rename(columns={'geoid' : 'geoid_origin'}, inplace=True)

# Get log pickups
print("Get log pickups...")
for i in ['nt_pred_pickups', 'am_pred_pickups', 'md_pred_pickups', 'pm_pred_pickups', 'ev_pred_pickups', 'pred_pickups']:
    pickups[i + "_log"] = np.where(pickups[i] == 0, 0, np.log(pickups[i]))


# Write to CSV
print("Writing to CSV...")
pickups = pickups[['geoid_origin', 'am_pred_pickups', 'nt_pred_pickups', 'md_pred_pickups', 'pm_pred_pickups', 'ev_pred_pickups', 'pred_pickups',  'nt_pred_pickups_log', 'am_pred_pickups_log', 'md_pred_pickups_log','pm_pred_pickups_log', 'ev_pred_pickups_log', 'pred_pickups_log']]
pickups.to_csv("../outputs/" + study_state + "_linear_pickups_" + scenario_name + ".csv", index = False)


