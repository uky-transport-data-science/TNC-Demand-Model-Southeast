#### Collect Census Data using Census API
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

# Set working directory
os.chdir('/mnt/e/CR2/Repos/TNC-Demand-Model-Southeast/inputs/')

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

# Main Function
def get_acs_lehd(study_state = "KY"):
    "This function returns ACS and LEHD Data for a given study state."
    "Output: dataframe"
    # Median Age by Census Tract
    ## Load Data
    print("Getting median age by census tract (DP05)...")
    dp05_load = pd.DataFrame(c.acs5dp.state_county_tract(fields = ('NAME', 'DP05_0018E'),
                                        state_fips = states_string,
                                        county_fips = "*",
                                        tract = "*",
                                        year = 2019))
    dp05_load.head()
    ## Clean Data
    ### Split name column
    dp05_load[['tract_name', 'county_name', 'state_name']] = dp05_load.NAME.str.split(',', expand=True)
    ### Clear front and rear whitespace
    for i in ['tract_name', 'county_name', 'state_name']:
        dp05_load[i] = dp05_load[i].apply(lambda x: x.strip())
    dp05_load.head()
    ### Drop name column
    dp05_load = dp05_load.drop(columns=['NAME'])
    ### Rename DP05_0018E column
    dp05_load = dp05_load.rename(columns={"DP05_0018E": "median_age"})
    dp05_load.head()
    ### Merge FIPS dataframe with dp05
    dp05 = pd.merge(dp05_load, fips_df, left_on = 'state', right_on = 'fips_code')
    ### Drop 'state' column (since it's captured in fips_code)
    dp05 = dp05.drop(columns=['state'])
    ### Create geoid column
    dp05['geoid'] = dp05['fips_code'] + dp05['county'] + dp05['tract']
    dp05['geoid'] = dp05['geoid'].astype('int64')
    ## Filter for state (MAKE ARGUMENT)
    dp05 = dp05[dp05['state_abb'].isin([study_state])]
    dp05 = dp05[['geoid', 'median_age']]
    dp05.head()



    # Educational Attainment by Census Tract (Pop. 25+ with Bachelor's Degree/Pop. 25+)
    ## Clean Data
    s1501_load = pd.DataFrame(c.acs5st.state_county_tract(fields = ('NAME', 'S1501_C01_006E', 'S1501_C01_012E'),
                                        state_fips = states_string,
                                        county_fips = "*",
                                        tract = "*",
                                        year = 2019))
    s1501_load.head()
    print("Getting educational attainment  by census tract (S1501)...")
    ### Split name column
    s1501_load[['tract_name', 'county_name', 'state_name']] = s1501_load.NAME.str.split(',', expand=True)
    ### Clear front and rear whitespace
    for i in ['tract_name', 'county_name', 'state_name']:
        s1501_load[i] = s1501_load[i].apply(lambda x: x.strip())
    s1501_load.head()
    ### Drop name column
    s1501_load = s1501_load.drop(columns=['NAME'])
    ### Rename columns
    s1501_load = s1501_load.rename(columns={"S1501_C01_006E": "pop_over_25",
                                        "S1501_C01_012E": "bach_over_25"})
    ### Get percentage of population over 25 with Bachelor's Degree (relative to 25+ pop.)
    s1501_load['pct_bach_25p'] = s1501_load['bach_over_25']/s1501_load['pop_over_25']
    s1501_load = s1501_load.drop(columns =['pop_over_25', 'bach_over_25'])
    ### Make geoid column (state + county + tract)
    s1501 = pd.merge(s1501_load, fips_df, left_on = 'state', right_on = 'fips_code')
    ### Drop 'state' column (since it's captured in fips_code)
    s1501 = s1501.drop(columns=['state'])
    ### Create geoid column
    s1501['geoid'] = s1501['fips_code'] + s1501['county'] + s1501['tract']
    s1501['geoid'] = s1501['geoid'].astype('int64')
    ## Filter for state (MAKE ARGUMENT)
    s1501 = s1501[s1501['state_abb'].isin([study_state])]
    s1501 = s1501[['geoid', 'pct_bach_25p']]
    s1501.head()


    # Get number of vehicles by household income
    print("Getting vehicles by household income...")
    ## Load data (MAKE ARGUMENT FOR STATE)
    veh_hh_inc_load = pd.read_csv(os.getcwd() + '/A112306/A112306_KY.csv')
    veh_hh_inc_load.head()
    ## Clean data
    ### Set first row as column names
    veh_hh_inc_load.columns = veh_hh_inc_load.iloc[0]
    ### Drop first row (since it's now column names)
    veh_hh_inc_load = veh_hh_inc_load.drop(veh_hh_inc_load.index[0])
    ### Remove the a112306_ substring from colnames
    veh_hh_inc_load.columns = [col.replace('a112306_', '') for col in veh_hh_inc_load.columns]
    veh_hh_inc_load.head()
    ### Split name column
    veh_hh_inc_load[['tract_name', 'county_name', 'state_name']] = veh_hh_inc_load.name.str.split(',', expand=True)
    ### Clear front and rear whitespace
    for i in ['tract_name', 'county_name', 'state_name']:
        veh_hh_inc_load[i] = veh_hh_inc_load[i].apply(lambda x: x.strip())
    veh_hh_inc_load.head()
    ### Drop name column
    veh_hh_inc_load = veh_hh_inc_load.drop(columns = ['name'])
    ### Keep relevant columns
    low_inc_0 = ['e11', 'e12', 'e13', 'e14', 'e15', 'e16']
    high_inc_0 = ['e17', 'e18']
    low_inc_1p = ['e20', 'e21', 'e22', 'e23', 'e24', 'e25', 
                'e29', 'e30', 'e31', 'e32', 'e33', 'e34',
                'e38', 'e39', 'e40', 'e41', 'e42', 'e43']
    high_inc_1p = ['e26', 'e27', 'e35', 'e36', 'e44', 'e45']
    ### Clean and convert income columns
    def clean_and_convert(columns):
        for col in columns:
            veh_hh_inc_load[col] = veh_hh_inc_load[col].astype(str).str.replace(',', '')
            veh_hh_inc_load[col] = pd.to_numeric(veh_hh_inc_load[col], errors='coerce')
    ### Apply function
    clean_and_convert(low_inc_0)
    clean_and_convert(high_inc_0)
    clean_and_convert(low_inc_1p)
    clean_and_convert(high_inc_1p)
    ### Sum across columns
    veh_hh_inc_load['low_inc_0'] = veh_hh_inc_load[low_inc_0].sum(axis=1)
    veh_hh_inc_load['hi_inc_0'] = veh_hh_inc_load[high_inc_0].sum(axis=1)
    veh_hh_inc_load['low_inc_1p'] = veh_hh_inc_load[low_inc_1p].sum(axis=1)
    veh_hh_inc_load['hi_inc_1p'] = veh_hh_inc_load[high_inc_1p].sum(axis=1)
    ### Keep relevant columns
    veh_hh_inc = veh_hh_inc_load[['geoid', 'low_inc_0', 'hi_inc_0', 'low_inc_1p', 'hi_inc_1p']]
    veh_hh_inc = veh_hh_inc.reset_index(drop=True)
    ### Remove C1100US string from geoid adn convert to numeric
    veh_hh_inc["geoid"] = veh_hh_inc["geoid"].str.replace("C1100US", "")
    veh_hh_inc[["geoid"]] = veh_hh_inc[["geoid"]].apply(pd.to_numeric)
    veh_hh_inc.head()

    # Combine median income, education, and vehicles by household income data
    acs = pd.merge(pd.merge(dp05, s1501 ,on = 'geoid'), veh_hh_inc, on = 'geoid')
    acs.head()

    # Workplace area characteristics (WAC) data
    ## Load data (MAKE PARAMETER SO THAT IT FILTERS FOR STATE)
    states_abb = list(fips_dict.keys())
    states_abb = [x.lower() for x in states_abb]
    
    print("Getting workplace area characteristics...")
    wac_load = []
    for i in states_abb:
        if i == 'ms':
            url = 'https://lehd.ces.census.gov/data/lodes/LODES8/' + i + '/wac/' + i + '_wac_S000_JT00_2018.csv.gz'
            response = requests.get(url)    
            content = response.content
            df = pd.read_csv(io.BytesIO(content), sep=",", compression="gzip", index_col=0, quotechar='"')
            df['state_abb'] = 'MS'
            wac_load.append(df)
        else:
            url = 'https://lehd.ces.census.gov/data/lodes/LODES8/' + i + '/wac/' + i + '_wac_S000_JT00_2019.csv.gz'
            response = requests.get(url)    
            content = response.content
            df = pd.read_csv(io.BytesIO(content), sep=",", compression="gzip", index_col=0, quotechar='"')
            df['state_abb'] = i.upper()
            wac_load.append(df)
    wac_load = pd.concat(wac_load)
    wac_load = wac_load.reset_index()
    ## Rename column so it matches
    wac_load = wac_load.rename(columns = {'w_geocode' : 'geoid'})
    ## Filter wac_load so it matches argument
    wac_load = wac_load[wac_load['state_abb'].isin([study_state])]

    ## Load Crosswalk Data
    print("Getting crosswalk data and cleaning employment data...")
    xwalk_load = []
    for i in states_abb:
        url = 'https://lehd.ces.census.gov/data/lodes/LODES8/' + i + '/' + i + '_xwalk.csv.gz'
        response = requests.get(url)
        content = response.content
        df = pd.read_csv(io.BytesIO(content), sep=",", compression="gzip", index_col=0, quotechar='"', low_memory = False)
        xwalk_load.append(df)
    xwalk_load = pd.concat(xwalk_load)
    xwalk_load = xwalk_load.reset_index()
    ## Filter xwalk_load so it matches argument
    xwalk_load = xwalk_load[xwalk_load['stusps'].isin([study_state])]
    ## Combine WAC and XWALK data
    wac_geo = wac_load.merge(xwalk_load, how="left", left_on='geoid', right_on='tabblk2020')
    wac_geo_grouped = wac_geo.groupby(by = 'trct', as_index = False).sum()
    ## Rename columns
    wac_geo_grouped['food_emp'] = wac_geo_grouped['CNS18'] 
    wac_geo_grouped['retail_emp'] = wac_geo_grouped['CNS07'] 
    wac_geo_grouped['other_emp'] = wac_geo_grouped['CNS01'] + wac_geo_grouped['CNS02'] + wac_geo_grouped['CNS03'] + wac_geo_grouped['CNS04'] + wac_geo_grouped['CNS05'] + wac_geo_grouped['CNS06'] + wac_geo_grouped['CNS08'] + wac_geo_grouped['CNS09'] + wac_geo_grouped['CNS10'] + wac_geo_grouped['CNS11'] + wac_geo_grouped['CNS12'] + wac_geo_grouped['CNS13'] + wac_geo_grouped['CNS14'] + wac_geo_grouped['CNS15'] + wac_geo_grouped['CNS16'] + wac_geo_grouped['CNS17'] + wac_geo_grouped['CNS19'] + wac_geo_grouped['CNS20']
    wac_geo_grouped = wac_geo_grouped.drop(columns=['geoid'])
    wac_geo_grouped = wac_geo_grouped.rename(columns={"trct": "geoid"})

    ## Load Land Area Data from TIGER Line Census Files
    print("Getting land area data from TIGER line files...")
    land_area_load = []
    for i in states_list:
        url = 'https://www2.census.gov/geo/tiger/TIGER2020/TRACT/tl_2020_' + i + '_tract.zip'
        df = gpd.read_file(url)[['GEOID', 'ALAND', 'STATEFP']]
        land_area_load.append(df)

    land_area_load = pd.concat(land_area_load)
    land_area_load = land_area_load.reset_index()
    ### Merge FIPS dataframe with dp05
    land_area  = pd.merge(land_area_load, fips_df, left_on = 'STATEFP', right_on = 'fips_code')
    ### Get land area in miles
    land_area['land_area'] = land_area['ALAND'] * (3.861 * (10**(-7)))
    ### Lowercase columns
    land_area.columns = map(str.lower, land_area.columns)
    ### Keep relevant columns
    land_area = land_area[['geoid', 'land_area', 'state_abb']]
    ### Convert geoid from object to int64
    land_area['geoid'] = land_area['geoid'].astype(np.int64)
    ### Filter by state from argument (MAKE ARGUMENT)
    land_area = land_area[land_area['state_abb'].isin([study_state])]
    land_area.head()

    # Combine WAC and Geography Files to Create LEHD Dataset
    wac = pd.merge(wac_geo_grouped, land_area, on='geoid', how='inner')
    wac['total_emp_den'] = (wac['food_emp'] + wac['retail_emp'] + wac['other_emp']) / wac['land_area']
    lehd = wac[['geoid', 'food_emp', 'retail_emp', 'other_emp', 'total_emp_den']]
    lehd.head()

    # Combine ACS data and LEHD data
    acs_lehd = pd.merge(acs, lehd, on = 'geoid', how='left')
    acs_lehd.shape

    # Flag for Tourist (TO DO find tourists)
    acs_lehd['tourist'] = 0

    # Flag for Airport (TO DO Find airports)
    airport_list = [21067004207, 21015980100, 21111980100]
    acs_lehd['airport'] = np.where(acs_lehd.geoid.isin([airport_list]), 1, 0)
    print("Cleaning acs_lehd combined dataframe...")
    return acs_lehd

