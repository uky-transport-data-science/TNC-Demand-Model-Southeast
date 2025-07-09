# TNC Demand Model Southeast Documentation

## Overview

This model is an application of the TNC Demand Model estimated using Chicago data (Mucci and Erhardt 2023) on Census tracts in the Southeastern United States. The final output is a data frame that contains the number of trips from each Census tract by time of day, whether they're private or shared (and if shared, whether they're matched or unmatched), and the associated travel time (in minutes) and fares (in US Dollars). 

## Setup
The requirements for running this model are the following:
- Python (v3.9+)
- Julia
- Windows Subsystem for Linux (WSL, installation instructions: https://learn.microsoft.com/en-us/windows/wsl/install)
- Census API Key (retrieve key from here: https://api.census.gov/data/key_signup.html)
- Census Transportation Planning Product (CTPP) API Key (instructions on retrieving key: https://ctppdata.transportation.org/CTPP_DataPortal_UserGuide_051624.pdf)

In Python, create a virtual environment and make sure the following packages are installed: `os`,
`warnings`, `numpy`, `pandas`, `census`, `io`, `requests`, `fiona`, `geopandas`, and `json`.

In Julia, install the `OSRM` package (instructions: https://github.com/mattwigway/OSRM.jl)

In a terminal, change your directory to where you put the model. Type in `wsl` to navigage to the Windows Subsystem for Linux interface.

## Running the Model
1. Open `model_config.json`. Edit the study state (postal abbreviation), fare adjustment (this multiplies the fare by whatever you put here. For example, if you're studying a quarter-fare, change this parameter to 0.25), the scenario name, your Census API key (in quotes), and your CTPP API key (in quotes).
2. Open `run_tncse.sh`. Edit the second line to change directories to the **inputs** folder.
3. In the terminal, activate your virtual environment.
4. Type in `bash run_tncse.sh` and hit enter. The first time you run for a state, it's going to take 3-4 hours to do the routing. But once you run another scenario for the same state, it should take about 15-20 minutes for the model to run.

## Other Things to be Aware Of
1. TIGER Line files that are being pulled in the code may run into permissions issues. To remedy this, download the TIGER Line file from https://www2.census.gov/geo/tiger/TIGER2019/TRACT/ for each state you wish to run (states are given in the link by their FIPS code). Make sure to change the `tiger_location` parameter in the model_config.json file parameter to `local` as well.
