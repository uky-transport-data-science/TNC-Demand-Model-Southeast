import numpy as np
import pandas as pd

## for 2019
def apply_trip_generation(merged_data, weekdays_csv):
    
    ## read in the file
    ON = pd.read_csv(merged_data, index_col = 0)
    AM = pd.read_csv(merged_data, index_col = 0)
    MD = pd.read_csv(merged_data, index_col = 0)
    PM = pd.read_csv(merged_data, index_col = 0)
    NT = pd.read_csv(merged_data, index_col = 0)


    ## apply linear models
    ON['LINEAR_PICKUPS'] = 0.1251485*ON['FOOD_EMP'] + 260.4035*1 + 0.0055992*ON['LOW_INC_0'] + 0.1456829*ON['HI_INC_0'] + 0.0206288*ON['LOW_INC_1P'] 
    ON['LINEAR_PICKUPS_LOG'] =  np.where(ON['LINEAR_PICKUPS'] == 0, 0, np.log(ON['LINEAR_PICKUPS']))

    AM['LINEAR_PICKUPS'] = 0.0000952*AM['OTHER_EMP'] + 0.0473473*AM['FOOD_EMP'] + 0.015827*AM['RETAIL_EMP'] + 130.2076*1 + 53.18332*0 + 0.3745288*AM['HI_INC_0'] + 0.0174729*AM['LOW_INC_0'] + 0.0176063*AM['LOW_INC_1P'] + 0.0000136*AM['HI_INC_1P'] 
    AM['LINEAR_PICKUPS_LOG'] =  np.where(AM['LINEAR_PICKUPS'] == 0, 0, np.log(AM['LINEAR_PICKUPS']))

    MD['LINEAR_PICKUPS'] = 0.1485942*MD['FOOD_EMP'] + 0.0653171*MD['RETAIL_EMP'] + 0.0075034*MD['OTHER_EMP'] + 921.3699*1 + 173.4502*0 + 0.6336939*MD['HI_INC_0'] + 0.0275177*MD['LOW_INC_0'] + 0.0235304*MD['LOW_INC_1P'] + 0.0000243*MD['HI_INC_1P'] 
    MD['LINEAR_PICKUPS_LOG'] =  np.where(MD['LINEAR_PICKUPS'] == 0, 0, np.log(MD['LINEAR_PICKUPS']))

    PM['LINEAR_PICKUPS'] = 0.1094589*PM['FOOD_EMP'] + 0.0385694*PM['RETAIL_EMP'] + 0.0079508*PM['OTHER_EMP'] + 213.2107*1 + 102.1033*0 + 0.4440004*PM['HI_INC_0'] + 0.0060732*PM['LOW_INC_0'] + 0.0072242*PM['LOW_INC_1P'] + 0.0000164*PM['HI_INC_1P'] 
    PM['LINEAR_PICKUPS_LOG'] = np.where(PM['LINEAR_PICKUPS'] == 0, 0, np.log(PM['LINEAR_PICKUPS']))

    NT['LINEAR_PICKUPS'] = 0.002725*NT['OTHER_EMP'] + 0.1846295*NT['FOOD_EMP'] + 476.2219*1 + 0.350088*NT['HI_INC_0'] + 0.00000446*NT['HI_INC_1P'] + 0.0070386*NT['LOW_INC_0'] + 0.0076753*NT['LOW_INC_1P']
    NT['LINEAR_PICKUPS_LOG'] =  np.where(NT['LINEAR_PICKUPS'] == 0, 0, np.log(NT['LINEAR_PICKUPS']))


    ## apply negative binomial models 
    ## placeholder for airpport data (1)
    ## placeholder for tourist data (0)
    ## placeholder for logsum (0)
    ON['PRED_AVG_WD_PICKUPS'] = np.exp(-1.699553*ON['AIR_F'] + 0.5047479*ON['TOR_F'] + 0.3486627*ON['LINEAR_PICKUPS_LOG'] + 1.082214*ON['LOGSUM'] - 0.0173114*ON['MEDIAN_AGE'] + 0.0170123*ON['P_BACH_25P'] + 0.000000716*ON['TOTAL_EMP_DEN'] - 0.1657967*ON['OCT_19'] - 5.691818)

    AM['PRED_AVG_WD_PICKUPS'] = np.exp(-0.7743786*AM['AIR_F'] + 0.4779832*AM['TOR_F'] + 0.4050372*AM['LINEAR_PICKUPS_LOG'] + 0.6230226*AM['LOGSUM'] - 0.0262*AM['MEDIAN_AGE'] + 0.0143772*AM['P_BACH_25P']+ 0.000000498*ON['TOTAL_EMP_DEN'] - 0.1265867*AM['OCT_19'] - 1.946639)

    MD['PRED_AVG_WD_PICKUPS'] = np.exp(-0.6405087*MD['AIR_F'] + 0.7809523*MD['TOR_F'] + 0.3927277*MD['LINEAR_PICKUPS_LOG'] + 0.6977969*MD['LOGSUM'] - 0.0208753*MD['MEDIAN_AGE'] + 0.0123951*MD['P_BACH_25P']+ 0.00000161*ON['TOTAL_EMP_DEN'] - 0.1605051*MD['OCT_19'] - 2.551229)

    PM['PRED_AVG_WD_PICKUPS'] = np.exp(-0.4855696*PM['AIR_F'] + 0.890186*PM['TOR_F'] + 0.4090155*PM['LINEAR_PICKUPS_LOG'] + 0.8352944*PM['LOGSUM'] - 0.0216488*PM['MEDIAN_AGE'] + 0.0149257*PM['P_BACH_25P']+ 0.00000217*ON['TOTAL_EMP_DEN'] - 0.0935998*PM['OCT_19'] - 4.089885)

    NT['PRED_AVG_WD_PICKUPS'] = np.exp(0.0188928*NT['AIR_F'] + 0.830838*NT['TOR_F'] + 0.3445732*NT['LINEAR_PICKUPS_LOG'] + 0.9817033*NT['LOGSUM'] - 0.0215845*NT['MEDIAN_AGE'] + 0.0199614*PM['P_BACH_25P']+ 0.00000224*ON['TOTAL_EMP_DEN'] - 0.148494*NT['OCT_19'] - 5.265743)

    # append all of the tod specific dataframes together
    pred_trips = ON.append(AM)
    pred_trips = ON.append(MD)
    pred_trips = ON.append(PM)
    pred_trips = ON.append(NT)

    # convert average weekday trips to monthly trip totals
    wd = pd.read_csv(weekdays_csv)
    pred_trips = pred_trips.merge(wd, on = ['MONTH','YEAR'])
    
    return pred_trips

apply_trip_generation(merged.csv, weekdays.csv)
print(pred_trips)
    