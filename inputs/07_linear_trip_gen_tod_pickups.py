#### Linear Trip Generation (Pickups by Time of Day)
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
acs_lehd = __import__('01_acs_lehd')

# Set working directory (make dynamic later)
os.chdir('/mnt/e/CR2/Repos/TNC-Demand-Model-Southeast/inputs/')

def linear_trip_gen_tod_pickups():
    # Get linear predicted pickups by TOD
    print("Get linear predicted pickups by TOD...")
    pickups = acs_lehd.get_acs_lehd()
    pickups['nt_pred_pickups'] = 260*pickups['airport'] + 0.13*pickups['food_emp'] + 0.01*pickups['hi_inc_0'] +  0.02*pickups['low_inc_0']
    pickups['am_pred_pickups'] = 130*pickups['airport'] + 0.05*pickups['food_emp'] + 0.02*pickups['retail_emp'] + 0.0000952*pickups['other_emp'] + 0.37*pickups['hi_inc_0'] +  0.02*pickups['low_inc_0'] + 0.02*pickups['low_inc_1p'] + 0.0000136*pickups['hi_inc_1p']
    pickups['md_pred_pickups'] = 921*pickups['airport'] + 0.15*pickups['food_emp'] + 0.07*pickups['retail_emp'] + 0.01*pickups['other_emp'] + 0.63*pickups['hi_inc_0'] +  0.03*pickups['low_inc_0'] + 0.02*pickups['low_inc_1p'] + 0.0000243*pickups['hi_inc_1p']
    pickups['pm_pred_pickups'] = 213*pickups['airport'] + 0.11*pickups['food_emp'] + 0.04*pickups['retail_emp'] + 0.01*pickups['other_emp'] + 0.44*pickups['hi_inc_0'] +  0.01*pickups['low_inc_0'] + 0.01*pickups['low_inc_1p'] + 0.0000164*pickups['hi_inc_1p']
    pickups['ev_pred_pickups'] = 476*pickups['airport'] + 0.18*pickups['food_emp'] + 0.00273*pickups['other_emp'] + 0.35*pickups['hi_inc_0'] +  0.01*pickups['low_inc_0'] + 0.01*pickups['low_inc_1p'] + 0.00000446*pickups['hi_inc_1p']

    # Sum pickups by TOD to get total pickups
    pickups['pred_pickups'] =  pickups[['am_pred_pickups', 'nt_pred_pickups', 'md_pred_pickups', 'pm_pred_pickups', 'ev_pred_pickups']].sum(axis=1)

    # Rename geoid to geoid_origin
    pickups.rename(columns={'geoid' : 'geoid_origin'}, inplace=True)

    # Get log pickups
    print("Get log pickups...")
    for i in ['nt_pred_pickups', 'am_pred_pickups', 'md_pred_pickups', 'pm_pred_pickups', 'ev_pred_pickups', 'pred_pickups']:
        pickups[i + "_log"] = np.where(pickups[i] == 0, 0, np.log(pickups[i]))
    
    return pickups

