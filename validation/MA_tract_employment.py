import os
os.chdir('/mnt/e/CR2/Repos/TNC-Demand-Model-Southeast/validation/')

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
import json

## Read JSON file
with open('../model_config.json') as f:
    model_config = json.load(f)

## Pass Parameters
study_state = "MA"
scenario_name = model_config["scenario_name"]
fare_adjust = model_config["fare_adjust"]

## Pass Parameters
study_state = model_config["study_state"]
scenario_name = model_config["scenario_name"]
fare_adjust = model_config["fare_adjust"]
census_key = model_config["census_key"]
ctpp_key = model_config["ctpp_key"]

# Activate Census Key
c = Census(census_key)

# FIPS Codes for States
AL = '01'
FL = '12'
GA = '13'
KY = '21'
MA = '25'
MS = '28'
NC = '37'
SC = '45'
TN = '47'

states_list = [AL, FL, GA, KY, MA, MS, NC, SC, TN]
states_string = ','.join(states_list)

fips_dict =  {'AL':'01',
              'FL':'12',
              'GA':'13',
              'KY':'21',
              'MA':'25',
              'MS':'28',
              'NC':'37',
              'SC':'45',
              'TN':'47'}

fips_df = pd.DataFrame(fips_dict.items(), columns=['state_abb', 'fips_code'])

states_abb = list(fips_dict.keys())
states_abb = [x.lower() for x in states_abb]

print("Getting workplace area characteristics...")
wac_load = []
for i in states_abb:
    if i == 'ms':
        url = 'https://lehd.ces.census.gov/data/lodes/LODES7/' + i + '/wac/' + i + '_wac_S000_JT00_2018.csv.gz'
        response = requests.get(url)    
        content = response.content
        df = pd.read_csv(io.BytesIO(content), sep=",", compression="gzip", index_col=0, quotechar='"')
        df['state_abb'] = 'MS'
        wac_load.append(df)
    else:
        url = 'https://lehd.ces.census.gov/data/lodes/LODES7/' + i + '/wac/' + i + '_wac_S000_JT00_2019.csv.gz'
        response = requests.get(url)    
        content = response.content
        df = pd.read_csv(io.BytesIO(content), sep=",", compression="gzip", index_col=0, quotechar='"')
        df['state_abb'] = i.upper()
        wac_load.append(df)
wac_load = pd.concat(wac_load)
wac_load = wac_load.reset_index()
## Rename column so it matches
wac_load = wac_load.rename(columns = {'w_geocode' : 'block'})
## Filter wac_load so it matches argument
wac_load = wac_load[wac_load['state_abb'].isin([study_state])]

## Get tracts from blocks
wac_load["geoid"] = wac_load["block"].astype(str).str[:-4].astype(np.int64)
print(len(wac_load["geoid"].unique()))

## Load Crosswalk Data
print("Getting crosswalk data and cleaning employment data...")
xwalk_load = []
for i in states_abb:
    url = 'https://lehd.ces.census.gov/data/lodes/LODES7/' + i + '/' + i + '_xwalk.csv.gz'
    response = requests.get(url)
    content = response.content
    df = pd.read_csv(io.BytesIO(content), sep=",", compression="gzip", index_col=0, quotechar='"', low_memory = False)
    xwalk_load.append(df)
xwalk_load = pd.concat(xwalk_load)
xwalk_load = xwalk_load.reset_index()
## Filter xwalk_load so it matches argument
xwalk_load = xwalk_load[xwalk_load['stusps'].isin([study_state])]
## Combine WAC and XWALK data
wac_geo = wac_load.merge(xwalk_load, how="left", left_on='block', right_on='tabblk2010')
wac_geo_grouped = wac_geo.groupby(by = 'trct', as_index = False).sum()

## Rename columns
wac_geo_grouped['emp2019'] = wac_geo_grouped['C000'] 
wac_geo_grouped = wac_geo_grouped.drop(columns=['geoid'])
wac_geo_grouped = wac_geo_grouped.rename(columns={"trct": "geoid"})
tract_employment = wac_geo_grouped[["geoid", "emp2019"]]

print("Getting median age by census tract (DP05)...")
dp05_load = pd.DataFrame(c.acs5dp.state_county_tract(fields = ('NAME', 'DP05_0001E'),
                                        state_fips = states_string,
                                        county_fips = "*",
                                        tract = "*",
                                        year = 2019))
dp05_load[['tract_name', 'county_name', 'state_name']] = dp05_load.NAME.str.split(',', expand=True)
### Clear front and rear whitespace
for i in ['tract_name', 'county_name', 'state_name']:
    dp05_load[i] = dp05_load[i].apply(lambda x: x.strip())
dp05_load.head()
### Drop name column
dp05_load = dp05_load.drop(columns=['NAME'])
### Rename DP05_0018E column
dp05_load = dp05_load.rename(columns={"DP05_0001E": "pop2019"})
dp05_load.head()
### Merge FIPS dataframe with dp05
dp05 = pd.merge(dp05_load, fips_df, left_on = 'state', right_on = 'fips_code')
### Drop 'state' column (since it's captured in fips_code)
dp05 = dp05.drop(columns=['state'])
### Create geoid column
dp05['geoid'] = dp05['fips_code'] + dp05['county'] + dp05['tract']
dp05['geoid'] = dp05['geoid'].astype('int64')
## Filter for state
dp05 = dp05[dp05['state_abb'].isin([study_state])]
tract_population = dp05[['geoid', 'pop2019']]

ma_pop_emp_2019 = pd.merge(tract_population, tract_employment, on='geoid', how='left')
ma_pop_emp_2019.fillna(0, inplace=True)
ma_pop_emp_2019.to_csv("./inputs/MA_tracts_pop_emp_2019.csv", index = False)