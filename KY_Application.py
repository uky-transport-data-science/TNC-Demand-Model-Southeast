import pandas as pd
import numpy as np

from Apply_Trip_Generation import apply_trip_generation

# STEP 1 CONSTANTS
merged_data = 'E:/CR2/Repos/TNC-Demand-Model-Southeast/Cleaned_Inputs/Intermediate/merged_fayette_data.csv'

#STEP 1: TRIP GENERATION APPLICATION
print('Working on Trip Generation Step')
pred_trips = apply_trip_generation(merged_data)
pred_trips.to_csv('E:/CR2/Repos/TNC-Demand-Model-Southeast/Cleaned_Inputs/Intermediate/pred_trips.csv')



