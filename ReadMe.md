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

In Python, create a virtual environment and make sure the following packages are installed: 