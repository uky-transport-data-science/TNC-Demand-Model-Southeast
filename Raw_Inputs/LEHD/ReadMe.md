RS 05.30.2024


These KY files come from the LEHD census website: https://lehd.ces.census.gov/data/. 

The WAC data provides information about the characteristics of jobs within a specific work area. The Geo xwalk data helps integrate the employment data from the WAC to different geographic contexts.


## To download the LEHD WAC xwalk data for your chosen state: ##

1. Go to https://lehd.ces.census.gov/data/ and scroll down to LODES. 

2. Choose your version, in our case we used "LODES8". (Version 8 of LODES was enumerated by 2020 census blocks. Previous versions of LODES were enumerated with 2010 census blocks (LODES7) or 2000 census blocks (LODES5))

3. Choose your state, in our case, "Kentucky".

4. Choose your type, in our case, "Workplace Area Characteristics (WAC)", then click on View Files.

5. Click on the "Geography crosswalk for (state)" link to download the xwalk data.



## To download the LEHD WAC data for your chosen state: ##

1. Same as steps 1-4 for LEHD WAC xwalk data.

2. Scroll in the box that opens after clicking View Files and find your year. In our use, the file was 
ky_wac_S000_JT00_2019.csv.gz (You will need to unzip, we used WinZip or 7-Zip).

Keep in mind, JT00 is the total number of jobs in each work area. 


## To download land area in square miles for each census tract for your chosen state: ##

1. Download QGIS on your computer

2. Go to TIGER/Line Shapefiles on the U.S. Census Bureau website. Scroll down to the bottom. Download the shapefile for your state. We used the 2020 tract for Kentucky. https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html

3. Start a new project on QGIS, and use the shapefile. Create a map.

4. Add a field, land_area, and use formula: $area * 3.861e-7 (area in square miles per census tract)

5. Export as CSV file.

