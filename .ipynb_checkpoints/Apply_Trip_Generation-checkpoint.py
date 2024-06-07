import numpy as np
import pandas as pd

def apply_trip_generation(tod1_file, tod2_file, tod3_file, tod4_file, tod5_file, weekdays_csv):

	##read in the files
	df1 = pd.read_csv(tod1_file, index_col = 0)
	df2 = pd.read_csv(tod2_file, index_col = 0)
	df3 = pd.read_csv(tod3_file, index_col = 0)
	df4 = pd.read_csv(tod4_file, index_col = 0)
	df5 = pd.read_csv(tod5_file, index_col = 0)


	##apply linear models
	df1['LINEAR_PICKUPS'] = 0.1251485*df1['FOOD_EMP'] + 260.4035*1 + 0.0055992*df1['LOW_INC_0'] + 0.1456829*df1['HI_INC_0'] + 0.0206288*df1['LOW_INC_1P'] 
	df1['LINEAR_PICKUPS_LOG'] =  np.where(df1['LINEAR_PICKUPS'] == 0, 0, np.log(df1['LINEAR_PICKUPS']))

	df2['LINEAR_PICKUPS'] = 0.0000952*df2['OTHER_EMP'] + 0.0473473*df2['FOOD_EMP'] + 0.015827*df2['RETAIL_EMP'] + 130.2076*1 + 53.18332*0 + 0.3745288*df2['HI_INC_0'] + 0.0174729*df2['LOW_INC_0'] + 0.0176063*df2['LOW_INC_1P'] + 0.0000136*df2['HI_INC_1P'] 
	df2['LINEAR_PICKUPS_LOG'] =  np.where(df2['LINEAR_PICKUPS'] == 0, 0, np.log(df2['LINEAR_PICKUPS']))

	df3['LINEAR_PICKUPS'] = 0.1485942*df3['FOOD_EMP'] + 0.0653171*df3['RETAIL_EMP'] + 0.0075034*df3['OTHER_EMP'] + 921.3699*1 + 173.4502*0 + 0.6336939*df3['HI_INC_0'] + 0.0275177*df3['LOW_INC_0'] + 0.0235304*df3['LOW_INC_1P'] + 0.0000243*df3['HI_INC_1P'] 
	df3['LINEAR_PICKUPS_LOG'] =  np.where(df3['LINEAR_PICKUPS'] == 0, 0, np.log(df3['LINEAR_PICKUPS']))

	df4['LINEAR_PICKUPS'] = 0.1094589*df4['FOOD_EMP'] + 0.0385694*df4['RETAIL_EMP'] + 0.0079508*df4['OTHER_EMP'] + 213.2107*1 + 102.1033*0 + 0.4440004*df4['HI_INC_0'] + 0.0060732*df4['LOW_INC_0'] + 0.0072242*df4['LOW_INC_1P'] + 0.0000164*df4['HI_INC_1P'] 
	df4['LINEAR_PICKUPS_LOG'] = np.where(df4['LINEAR_PICKUPS'] == 0, 0, np.log(df4['LINEAR_PICKUPS']))

	df5['LINEAR_PICKUPS'] = 0.002725*df5['OTHER_EMP'] + 0.1846295*df5['FOOD_EMP'] + 476.2219*1 + 0.350088*df5['HI_INC_0'] + 0.00000446*df5['HI_INC_1P'] + 0.0070386*df5['LOW_INC_0'] + 0.0076753*df5['LOW_INC_1P']
	df5['LINEAR_PICKUPS_LOG'] =  np.where(df5['LINEAR_PICKUPS'] == 0, 0, np.log(df5['LINEAR_PICKUPS']))


	##apply negative binomial models 
    ## airport data got replaced with 1, tourist data got replaced with 0
    ## will replace logsum later, don't worry about it for now
	df1['PRED_AVG_WD_PICKUPS'] = np.exp(-1.699553*1 + 0.5047479*0 + 0.3486627*df1['LINEAR_PICKUPS_LOG'] + 1.082214*df1['LOGSUM'] - 0.0173114*df1['MEDIAN_AGE'] + 0.0170123*df1['P_BACH_25P'] + 0.000000716*df1['TOTAL_EMP_DEN'] - 0.1657967*df1['OCT_19'] - 5.691818)

	df2['PRED_AVG_WD_PICKUPS'] = np.exp(-0.7743786*1 + 0.4779832*0 + 0.4050372*df2['LINEAR_PICKUPS_LOG'] + 0.6230226*df2['LOGSUM'] - 0.0262*df2['MEDIAN_AGE'] + 0.0143772*df2['P_BACH_25P']+ 0.000000498*df1['TOTAL_EMP_DEN'] - 0.1265867*df2['OCT_19'] - 1.946639)

	df3['PRED_AVG_WD_PICKUPS'] = np.exp(-0.6405087*1 + 0.7809523*0 + 0.3927277*df3['LINEAR_PICKUPS_LOG'] + 0.6977969*df3['LOGSUM'] - 0.0208753*df3['MEDIAN_AGE'] + 0.0123951*df3['P_BACH_25P']+ 0.00000161*df1['TOTAL_EMP_DEN'] - 0.1605051*df3['OCT_19'] - 2.551229)

	df4['PRED_AVG_WD_PICKUPS'] = np.exp(-0.4855696*1 + 0.890186*0 + 0.4090155*df4['LINEAR_PICKUPS_LOG'] + 0.8352944*df4['LOGSUM'] - 0.0216488*df4['MEDIAN_AGE'] + 0.0149257*df4['P_BACH_25P']+ 0.00000217*df1['TOTAL_EMP_DEN'] - 0.0935998*df4['OCT_19'] - 4.089885)

	df5['PRED_AVG_WD_PICKUPS'] = np.exp(0.0188928*1 + 0.830838*0 + 0.3445732*df5['LINEAR_PICKUPS_LOG'] + 0.9817033*df5['LOGSUM'] - 0.0215845*df5['MEDIAN_AGE'] + 0.0199614*df4['P_BACH_25P']+ 0.00000224*df1['TOTAL_EMP_DEN'] - 0.148494*df5['OCT_19'] - 5.265743)

	#append all of the tod specific dataframes together
	pred_trips = df1.append(df2)
	pred_trips = df1.append(df3)
	pred_trips = df1.append(df4)
	pred_trips = df1.append(df5)

	#convert average weekday trips to monthly trip totals
	wd = pd.read_csv(weekdays_csv)
	pred_trips = pred_trips.merge(wd, on = ['MONTH','YEAR'])
	
	return pred_trips