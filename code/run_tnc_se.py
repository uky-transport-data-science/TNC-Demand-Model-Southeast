# Run TNC-SE Model
study_state = "KY"
scenario_name = "baseline"
fare_adjust = 1 # default baseline is 1 (i.e. multiply fare by itself)

# Set working directory
import os
import sys
os.chdir('/mnt/e/CR2/Repos/TNC-Demand-Model-Southeast/code/')
sys.path.append("../inputs/")

# Import Scripts
acs_lehd = __import__('01_acs_lehd')
priv_shared_ttd = __import__('04_priv_shared_ttd')
priv_shared_fares = __import__('05_priv_shared_fares')
mode_choice_step1 = __import__('06_mode_choice_step1')
linear_trip_gen = __import__('07_linear_trip_gen_tod_pickups')
trip_dist = __import__('08_trip_dist_dest_choice')
neg_bin_trip_gen_dist = __import__('09_neg_bin_trip_gen_dist')
mode_choice_step2 = __import__('10_mode_choice_step2')

os.chdir('/mnt/e/CR2/Repos/TNC-Demand-Model-Southeast/code/')

# Run Model
priv_shared_fares.priv_shared_fares(scenario_name = scenario_name, study_state = study_state, fare_adjust = fare_adjust)
mode_choice_step1.mode_choice_step1(scenario_name = scenario_name, study_state = study_state)
linear_trip_gen.linear_trip_gen_tod_pickups(scenario_name = scenario_name, study_state = study_state)
trip_dist.trip_dist_dest_choice(scenario_name = scenario_name, study_state = study_state)
neg_bin_trip_gen_dist.neg_bin_trip_gen_dist(scenario_name = scenario_name, study_state = study_state)
mode_choice_step2.mode_choice_step2(scenario_name = scenario_name, study_state = study_state)
