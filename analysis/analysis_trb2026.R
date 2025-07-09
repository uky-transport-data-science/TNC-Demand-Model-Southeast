### Analysis for TRB Paper 2026
# Parameters --------------------------------------------------------------
study_state <- "KY"
scenario_name <- "quarter_fare"

# Set Working Directory ---------------------------------------------------
setwd("E:/CR2/Repos/TNC-Demand-Model-Southeast/analysis")

# Load Packages -----------------------------------------------------------
packages_vector <- c("tidyverse", "sf", "tigris", "collapse", "data.table", "janitor", "openxlsx")
need_to_install <- packages_vector[!(packages_vector %in% installed.packages()[,"Package"])]
if (length(need_to_install)) install.packages(need_to_install)
lapply(packages_vector, library, character.only = TRUE)
options(scipen = 999)

# Read in Data ------------------------------------------------------------
trips_load <- fread(paste0("../outputs/", study_state, "_trips_final_long_", scenario_name, ".csv"))
ruca_load <- read.xlsx("https://ers.usda.gov/sites/default/files/_laserfiche/DataFiles/53241/ruca2010revised.xlsx")
pop_load <- read.csv("./KY_pop_by_tract.csv")
tract_df <- tracts(state = study_state, year = 2019)

# Cleaning Data -----------------------------------------------------------
## Clean Trips Data -------------------------------------------------------
trips_load$time_of_day <- toupper(trips_load$time_of_day)
trips_load$trip_type <- gsub("^(\\w)(\\w+)", "\\U\\1\\L\\2", 
                             trips_load$trip_type, perl = TRUE)
trips_load$shared <- gsub("^(\\w)(\\w+)", "\\U\\1\\L\\2", 
                          trips_load$shared, perl = TRUE)
trips_load$time_of_day <- factor(trips_load$time_of_day, levels=c("NT", "AM", "MD", "PM", "EV"))
trips_load$trip_type <- factor(trips_load$trip_type, levels=c("Private", "Matched", "Unmatched"))

## Clean RUCA Data -------------------------------------------------------
colnames(ruca_load) <- ruca_load[1, ]
ruca <- ruca_load %>%
  filter(!row_number() %in% c(1)) %>%
  select(4, 5)
colnames(ruca) <- c("geoid", "ruca_code")
ruca$geoid <- as.numeric(ruca$geoid)
ruca$ruca_code <- as.numeric(ruca$ruca_code)
ruca$rural <- ifelse(ruca$ruca_code %in% c(7, 8, 9, 10), "Rural",
                     "Non-Rural")


# Clean Tracts Dataframe --------------------------------------------------
tract_df$INTPTLAT <- as.numeric(tract_df$INTPTLAT)
tract_df$INTPTLON <- as.numeric(tract_df$INTPTLON)
tract_df <- tract_df %>%
  select(GEOID, geometry) %>%
  rename(geoid_origin = GEOID)

# Merging RUCA and Trips --------------------------------------------------
trips_ruca <- trips_load %>%
  left_join(ruca, by = c("geoid_origin" = "geoid")) %>%
  left_join(ruca, by = c("geoid_dest" = "geoid"))

trips_ruca <- trips_ruca %>%
  rename(rural_origin = rural.x,
         rural_dest = rural.y) %>%
  select(-ruca_code.x, -ruca_code.y)

# Total Trips -------------------------------------------------------------
sum(trips_load$trips, na.rm = T)
print(paste0("Total trips: ", round(sum(trips_load$trips, na.rm = T))))

# Trips by Tract Type ------------------------------------------------
trips_by_tract_type <- trips_ruca %>%
  group_by(rural_origin) %>%
  summarize(trips = sum(trips, na.rm = T))
print(trips_by_tract_type)

# Trips by Tract Type and Trip Type ---------------------------------------
trips_by_tract_trip_type <- trips_ruca %>%
  group_by(rural_origin, trip_type) %>%
  summarize(trips = sum(trips, na.rm = T))
print(trips_by_tract_trip_type)
write.csv(trips_by_tract_trip_type, paste0("./outputs/trb2026/", study_state, "_trips_by_tract_trip_type_", scenario_name, ".csv"), row.names = F)

# Average Fare ------------------------------------------------------------
## Average fare weighted by number of trips for trips <= 60 min
average_fare <- trips_ruca %>%
  filter(travel_time < 60) %>%
  group_by(shared) %>%
  summarize(average_fare = weighted.mean(fares, dplyr::coalesce(trips, 0), na.rm = T))
print(average_fare)
write.csv(average_fare, paste0("./outputs/trb2026/", study_state, "_average_fare_", scenario_name, ".csv"), row.names = F)

# Revenue by Tract Type ----------------------------------------------------
revenue_by_tract_type <- trips_ruca %>%
  mutate(revenue = trips*fares) %>%
  group_by(rural_origin) %>%
  summarize(revenue = sum(revenue, na.rm = T))
print(revenue_by_tract_type)
print(sum(revenue_by_tract_type$revenue))
write.csv(revenue_by_tract_type, paste0("./outputs/trb2026/", study_state, "_revenue_by_tract_type_", scenario_name, ".csv"), row.names = F)

# Clean Data and Write out for ArcGIS Mapping -----------------------------
head(trips_ruca)
trips_by_origin <- trips_ruca %>%
  group_by(geoid_origin, rural_origin) %>%
  summarize(trips = sum(trips, na.rm = TRUE)) %>%
  left_join(pop_load, by = c("geoid_origin"="geoid")) %>%
  mutate(trips_per_pop = trips / population,
         geoid_origin = as.character(geoid_origin))

trips_by_origin_shp <- tract_df %>%
  left_join(trips_by_origin)
  
print(trips_by_origin_shp)
write_sf(trips_by_origin_shp, paste0("./outputs/trb2026/", study_state, "_trips_by_origin_", scenario_name, ".shp"), row.names = F)
