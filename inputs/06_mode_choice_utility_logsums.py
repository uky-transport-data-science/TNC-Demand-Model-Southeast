#### Calculate Mode Choice Utility and Logsums
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
priv_shared_fares = __import__('05_priv_shared_fares')

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

# Calculate utility for shared trips
## Recall: utility for shared trips is a function of travel time, travel cost, median income in the origin, 
## median income in the destination, and if it's going to or from the airport.
def get_median_income():
    "This function returns median income by Census tract."
    "Output: dataframe"
    # Median Income by Census Tract
    ## Load Data
    print("Getting median income by Census tract (B19013)...")
    b19013_load = pd.DataFrame(c.acs5.state_county_tract(fields = ('NAME', 'B19013_001E'), state_fips = states_string, county_fips = "*", tract = "*", year = 2019))
    ## Create geoid_origin and geoid_dest columns
    b19013_load.loc[:, "geoid_origin"] = b19013_load['state'] + b19013_load['county'] + b19013_load['tract']
    b19013_load.loc[:, "geoid_dest"] = b19013_load['state'] + b19013_load['county'] + b19013_load['tract']
    ## Get median income columns
    median_inc = b19013_load[["geoid_origin", "geoid_dest", "B19013_001E"]]
    median_inc.loc[:, "B19013_001E"] = median_inc["B19013_001E"]/10000 # convert to units of $10,000
    median_inc = median_inc.rename(columns={'B19013_001E': 'median_income_origin'})
    median_inc[["median_income_dest"]] = median_inc[["median_income_origin"]]
    return median_inc

def mode_choice_utility_logsums():
    # Read in data
    utility = pd.read_csv('../outputs/fares_and_times.csv')
    #utility = priv_shared_fares.priv_shared_fares()
    # Create indicator to see if an airport is in the origin or destination.
    ## These are the airports in Kentucky.
    airport_census_tracts = [21067004207, 21015980100, 21111980100] 
    # Order: LEX, CVG, SDF
    utility.loc[:, 'airport'] = np.where(utility['geoid_origin'].isin(airport_census_tracts), 1, np.where(utility['geoid_dest'].isin(airport_census_tracts), 1, 0))

    # Calculate utility for private trips
    ## Private utility is a function of travel time and costs.
    print("Calculating utility for private trips...")
    utility.loc[:, 'private_utility'] = (-0.110 * utility['private_travel_time']) + (-0.138 * utility['private_fares'])

    # Apply get_median_income function
    median_inc = get_median_income()
    origin_median_inc = median_inc[["geoid_origin", "median_income_origin"]]
    dest_median_inc = median_inc[["geoid_dest", "median_income_dest"]]

    ### Merge utility dataframe with income dataframe on origin Census tract
    print("Merging utility dataframe with income on origin...")
    utility = utility.merge(origin_median_inc.astype(float), how='left', on = ['geoid_origin'])

    ### Merge utility dataframe with income dataframe on destination Census tract
    print("Merging utility dataframe with income on destination...")
    utility = utility.merge(dest_median_inc.astype(float), how='left', on = ['geoid_dest'])

    # Calculate Utility for Shared Trips
    print("Calculating utility for shared trips...")
    utility.loc[:, 'shared_utility'] = (-0.573223) + (-0.110075 * utility['shared_travel_time']) + (-0.137794 * utility['shared_fares'])  + (-0.068228 * utility['median_income_origin'])  + (-0.049448 * utility['median_income_dest']) + (-2.716947 * utility['airport'])

    # Calculate Probability of Taking a Private/Shared Ride between an OD Pair
    ## P(Private) = e^(U(Private)) / sum(e^(U(Private))+e^(U(Shared))
    print("Calculating private/shared probabilities...")
    utility.loc[:, 'private_prob'] = (np.exp(utility['private_utility'])) / ((np.exp(utility['private_utility'])) + (np.exp(utility['shared_utility'])))
    utility.loc[:, 'shared_prob'] = 1 - utility['private_prob']

    # Calculate Mode Choice Logsums
    print("Calculating logsums...")
    utility['mode_logsum'] = np.log((np.exp(utility['shared_utility'])) + (np.exp(utility['private_utility'])))

    # Used in Destination Choice: Break out utilities by whether they are airport trips or not.
    print("Calculating airport logsums...")
    utility['mode_logsum_airport'] = utility['mode_logsum'] * utility['airport']
    utility['mode_logsum_no_airport'] = np.where(utility['airport'] == 0, utility['mode_logsum'], 0)

    ### Write to CSV
    print("Writing to CSV...")
    utility.to_csv('../outputs/mode_choice_utility_logsums.csv', index = False)
    return utility