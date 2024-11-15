# TNC Demand Model Southeast Documentation

## Overview

This model is an application of the TNC Demand Model estimated using Chicago data (Mucci and Erhardt 2023) on Census tracts in the Southeastern United States. The final output is a data frame that contains the number of trips from each Census tract by time of day, whether they're private or shared (and if shared, whether they're matched or unmatched), and the associated travel time (in minutes) and fares (in US Dollars). 

## Setup
The requirements for running this model are the following:
- Python (v3.9+)
- R (v4.0+)
- Julia
- Windows Subsystem for Linux (WSL, installation instructions: https://learn.microsoft.com/en-us/windows/wsl/install)
- Census API Key (retrieve key from here: https://api.census.gov/data/key_signup.html)

## How to run the model
1. Update `model_config.json`.
2. Because you're running this from WSL, enter this command to fix the line-break issues: `sed -i 's/\r//g' run_tncse.sh1`
   
