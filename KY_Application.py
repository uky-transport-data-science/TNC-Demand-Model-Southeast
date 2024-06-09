import pandas as pd
import numpy as np

from Apply_Trip_Generation import apply_trip_generation

# STEP 1 CONSTANTS
merged_data = 'E:/CR2/Repos/TNC-Demand-Model-Southeast/Cleaned_Inputs/Intermediate/merged.csv'
weekdays_csv = 'E:/CR2/Repos/TNC-Demand-Model-Southeast/Cleaned_Inputs/Intermediate/weekdays.csv'

#STEP 1: TRIP GENERATION APPLICATION
print('Working on Trip Generation Step')
pred_trips = apply_trip_generation(merged_data, weekdays_csv)




