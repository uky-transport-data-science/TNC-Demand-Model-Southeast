#### Trip Distribution (Destination Choice)
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
mode_choice_utility_logsums = __import__('06_mode_choice_utility_logsums')

# Set working directory (make dynamic later)
os.chdir('/mnt/e/CR2/Repos/TNC-Demand-Model-Southeast/inputs/')

def trip_dist_dest_choice():
    # Get linear predicted dropoffs by TOD
    print("Getting linear predicted dropoffs by TOD...")
    dropoffs = acs_lehd.get_acs_lehd()
    dropoffs['nt_pred_dropoffs'] = 545*dropoffs['airport'] + 0.07*dropoffs['food_emp'] + 0.00*dropoffs['other_emp'] + 0.28*dropoffs['hi_inc_0'] +  0.02*dropoffs['low_inc_0'] + 0.02*dropoffs['low_inc_1p'] + 0.00000454*dropoffs['hi_inc_1p']
    dropoffs['am_pred_dropoffs'] = 616*dropoffs['airport'] + 0.04*dropoffs['food_emp'] + 0.02*dropoffs['retail_emp'] + 0.001*dropoffs['other_emp'] + 0.29*dropoffs['hi_inc_0'] + 0.0000102*dropoffs['hi_inc_1p']
    dropoffs['md_pred_dropoffs'] = 1501*dropoffs['airport'] + 0.20*dropoffs['food_emp'] + 0.08*dropoffs['retail_emp'] + 0.01*dropoffs['other_emp'] + 0.51*dropoffs['hi_inc_0'] + 0.01*dropoffs['low_inc_0'] + 0.01*dropoffs['low_inc_1p'] + 0.0000313*dropoffs['hi_inc_1p']
    dropoffs['pm_pred_dropoffs'] = 308*dropoffs['airport'] + 0.17*dropoffs['food_emp'] + 0.001*dropoffs['retail_emp'] + 0.00*dropoffs['other_emp'] + 0.4*dropoffs['hi_inc_0'] + 0.02*dropoffs['low_inc_0'] + 0.01*dropoffs['low_inc_1p'] + 0.00000658*dropoffs['hi_inc_1p']
    dropoffs['ev_pred_dropoffs'] = 0.12*dropoffs['food_emp'] + 0.47*dropoffs['hi_inc_0'] + 0.02*dropoffs['low_inc_0'] + 0.02*dropoffs['low_inc_1p'] + 0.00000694*dropoffs['hi_inc_1p']
    
    dropoffs = dropoffs.rename(columns={"geoid": "geoid_dest"})

    # Read in utitlity/probability/logsum data
    logsum = mode_choice_utility_logsums.mode_choice_utility_logsums()
    logsum = logsum[['origin', 'destination', 'distance_miles', 'mode_logsum_airport', 'mode_logsum_no_airport']]
    logsum.head()



    
