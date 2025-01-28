#!/usr/bin/env sh
cd /mnt/e/CR2/Repos/TNC-Demand-Model-Southeast/inputs
python3 "01_acs_lehd.py"
python3 "02_create_census_tract_centroids.py"
julia "03_travel_time_distance.jl"
python3 "04_priv_shared_ttd.py"
python3 "05_priv_shared_fares.py"
python3 "06_mode_choice_step1.py"
python3 "07_linear_trip_gen_tod_pickups.py"
python3 "08_trip_dist_dest_choice.py"
python3 "09_neg_bin_trip_gen_dist.py"
python3 "10_mode_choice_step2.py"

