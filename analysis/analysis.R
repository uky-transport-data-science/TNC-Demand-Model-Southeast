## Output Analysis

# Set Working Directory ---------------------------------------------------
setwd("E:/CR2/Repos/TNC-Demand-Model-Southeast/analysis")

# Load Packages -----------------------------------------------------------
packages_vector <- c("tidyverse", "sf", "tigris", "collapse", "data.table", "janitor", "openxlsx")
need_to_install <- packages_vector[!(packages_vector %in% installed.packages()[,"Package"])]
if (length(need_to_install)) install.packages(need_to_install)
lapply(packages_vector, library, character.only = TRUE)
options(scipen = 999)


# Read in Data ------------------------------------------------------------
trips_load <- fread("../outputs/KY_trips_final_long_baseline.csv")
ruca_load <- read.xlsx("https://ers.usda.gov/sites/default/files/_laserfiche/DataFiles/53241/ruca2010revised.xlsx")

colnames(ruca_load) <- ruca_load[1, ]
ruca <- ruca_load %>%
  filter(!row_number() %in% c(1)) %>%
  select(4, 5)
colnames(ruca) <- c("geoid_origin", "ruca_code")
ruca$geoid_origin <- as.numeric(ruca$geoid_origin)
ruca$ruca_code <- as.numeric(ruca$ruca_code)
ruca$rural <- ifelse(ruca$ruca_code < 7 | ruca$ruca_code >= 10, "Non-Rural",
                     "Rural")

# Summary Stats -----------------------------------------------------------
## Total Trips ------------------------------------------------------------
sum(trips_load$trips, na.rm = T)

## Private/Shared ---------------------------------------------------------
trips_priv_shared <- trips_load %>%
  group_by(shared) %>%
  summarize(trips = sum(trips, na.rm = T))
print(trips_priv_shared)

## Matched/Unmatched ------------------------------------------------------
trips_matched <- trips_load %>%
  group_by(trip_type) %>%
  summarize(trips = sum(trips, na.rm = T))
print(trips_matched)

## Trips by Time of Day ---------------------------------------------------
trips_by_tod <- trips_load %>%
  group_by(time_of_day) %>%
  summarize(trips = sum(trips, na.rm = T))
print(trips_by_tod)

## Trips by Rural/Non-Rural -----------------------------------------------
trips_by_origin <- trips_load %>%
  group_by(geoid_origin) %>%
  summarize(trips = sum(trips, na.rm = T))

trips_by_origin <- merge(x = trips_by_origin, y = ruca, by = "geoid_origin", all.x = TRUE)
trips_rural <- trips_by_origin %>%
  group_by(rural) %>%
  summarize(trips = sum(trips, na.rm = T)) %>%
  filter(!row_number() %in% c(3))
print(trips_rural)


# Top Rural Tracts --------------------------------------------------------
trips_by_origin_rural <- trips_by_origin %>%
  filter(rural == "Rural") %>%
  arrange(desc(trips))
print(head(trips_by_origin_rural, 5))

# Top Non-Rural Tracts --------------------------------------------------------
trips_by_origin_non_rural <- trips_by_origin %>%
  filter(rural == "Non-Rural") %>%
  arrange(desc(trips))
print(head(trips_by_origin_non_rural, 5))


