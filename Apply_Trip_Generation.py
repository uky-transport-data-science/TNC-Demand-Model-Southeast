import numpy as np
import pandas as pd

## 2019
def apply_trip_generation(merged_data):
    
    ## read in the file
    df = pd.read_csv(merged_data, index_col = 0) #TOD1

    ## apply linear models
    df['NT_LINEAR_PICKUPS'] = 0.1251485*df['FOOD_EMP'] + 260.4035*df['AIR_F'] + 0.0055992*df['LOW_INC_0'] + 0.1456829*df['HI_INC_0'] + 0.0206288*df['LOW_INC_1P'] 
    df['NT_LINEAR_PICKUPS_LOG'] =  np.where(df['NT_LINEAR_PICKUPS'] == 0, 0, np.log(df['NT_LINEAR_PICKUPS']))
    
    df['AM_LINEAR_PICKUPS'] = 0.0000952*df['OTHER_EMP'] + 0.0473473*df['FOOD_EMP'] + 0.015827*df['RETAIL_EMP'] + 130.2076*df['AIR_F'] + 53.18332*df['TOR_F'] + 0.3745288*df['HI_INC_0'] + 0.0174729*df['LOW_INC_0'] + 0.0176063*df['LOW_INC_1P'] + 0.0000136*df['HI_INC_1P'] 
    df['AM_LINEAR_PICKUPS_LOG'] =  np.where(df['AM_LINEAR_PICKUPS'] == 0, 0, np.log(df['AM_LINEAR_PICKUPS']))

    df['MD_LINEAR_PICKUPS'] = 0.1485942*df['FOOD_EMP'] + 0.0653171*df['RETAIL_EMP'] + 0.0075034*df['OTHER_EMP'] + 921.3699*df['AIR_F'] + 173.4502*df['TOR_F'] + 0.6336939*df['HI_INC_0'] + 0.0275177*df['LOW_INC_0'] + 0.0235304*df['LOW_INC_1P'] + 0.0000243*df['HI_INC_1P'] 
    df['MD_LINEAR_PICKUPS_LOG'] =  np.where(df['MD_LINEAR_PICKUPS'] == 0, 0, np.log(df['MD_LINEAR_PICKUPS']))

    df['PM_LINEAR_PICKUPS'] = 0.1094589*df['FOOD_EMP'] + 0.0385694*df['RETAIL_EMP'] + 0.0079508*df['OTHER_EMP'] + 213.2107*df['AIR_F'] + 102.1033*df['TOR_F'] + 0.4440004*df['HI_INC_0'] + 0.0060732*df['LOW_INC_0'] + 0.0072242*df['LOW_INC_1P'] + 0.0000164*df['HI_INC_1P'] 
    df['PM_LINEAR_PICKUPS_LOG'] = np.where(df['PM_LINEAR_PICKUPS'] == 0, 0, np.log(df['PM_LINEAR_PICKUPS']))

    df['EV_LINEAR_PICKUPS'] = 0.002725*df['OTHER_EMP'] + 0.1846295*df['FOOD_EMP'] + 476.2219*df['AIR_F'] + 0.350088*df['HI_INC_0'] + 0.00000446*df['HI_INC_1P'] + 0.0070386*df['LOW_INC_0'] + 0.0076753*df['LOW_INC_1P']
    df['EV_LINEAR_PICKUPS_LOG'] =  np.where(df['EV_LINEAR_PICKUPS'] == 0, 0, np.log(df['EV_LINEAR_PICKUPS']))


    ## apply negative binomial models 
    ## placeholder for airpport data (1)
    ## placeholder for tourist data (0)
    ## placeholder for logsum (0)
    df['NT_PRED_AVG_WD_PICKUPS'] = np.exp(-1.699553*df['AIR_F'] + 0.5047479*df['TOR_F'] + 0.3486627*df['NT_LINEAR_PICKUPS_LOG'] + 1.082214*df['LOGSUM'] - 0.0173114*df['MEDIAN_AGE'] + 0.0170123*df['P_BACH_25P'] + 0.000000716*df['TOTAL_EMP_DEN'] - 5.691818)

    df['AM_PRED_AVG_WD_PICKUPS'] = np.exp(-0.7743786*df['AIR_F'] + 0.4779832*df['TOR_F'] + 0.4050372*df['AM_LINEAR_PICKUPS_LOG'] + 0.6230226*df['LOGSUM'] - 0.0262*df['MEDIAN_AGE'] + 0.0143772*df['P_BACH_25P']+ 0.000000498*df['TOTAL_EMP_DEN'] - 1.946639)

    df['MD_PRED_AVG_WD_PICKUPS'] = np.exp(-0.6405087*df['AIR_F'] + 0.7809523*df['TOR_F'] + 0.3927277*df['MD_LINEAR_PICKUPS_LOG'] + 0.6977969*df['LOGSUM'] - 0.0208753*df['MEDIAN_AGE'] + 0.0123951*df['P_BACH_25P']+ 0.00000161*df['TOTAL_EMP_DEN'] - 2.551229)

    df['PM_PRED_AVG_WD_PICKUPS'] = np.exp(-0.4855696*df['AIR_F'] + 0.890186*df['TOR_F'] + 0.4090155*df['PM_LINEAR_PICKUPS_LOG'] + 0.8352944*df['LOGSUM'] - 0.0216488*df['MEDIAN_AGE'] + 0.0149257*df['P_BACH_25P']+ 0.00000217*df['TOTAL_EMP_DEN'] - 4.089885)

    df['EV_PRED_AVG_WD_PICKUPS'] = np.exp(0.0188928*df['AIR_F'] + 0.830838*df['TOR_F'] + 0.3445732*df['EV_LINEAR_PICKUPS_LOG'] + 0.9817033*df['LOGSUM'] - 0.0215845*df['MEDIAN_AGE'] + 0.0199614*df['P_BACH_25P']+ 0.00000224*df['TOTAL_EMP_DEN'] - 5.265743)
    
    return df

    