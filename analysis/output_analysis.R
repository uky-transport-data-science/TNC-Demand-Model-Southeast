#### TNC Trip Analysis


# Get full long file ------------------------------------------------------


# Set Working Directory ---------------------------------------------------
setwd("E:/CR2/Repos/TNC-Demand-Model-Southeast/analysis")

# Load Packages ----------------------------------------------------------
packages_vector <- c("tidyverse", "sf", "tigris", "collapse", "data.table")
need_to_install <- packages_vector[!(packages_vector %in% installed.packages()[,"Package"])]
if (length(need_to_install)) install.packages(need_to_install)
lapply(packages_vector, library, character.only = TRUE)
options(scipen = 999)



# Geography Data ----------------------------------------------------------
## Load in Geography Data
ky <- tracts(state = "KY", year = 2020)
ky$INTPTLAT <- as.numeric(ky$INTPTLAT)
ky$INTPTLON <- as.numeric(ky$INTPTLON)
ky$GEOID <- as.numeric(ky$GEOID)

ky_map_data <- left_join(ky, full_df, by = c("GEOID" = "geoid_origin"))
ky_map_data <- ky_map_data %>%
  rename("geoid_origin" = "GEOID")


# Number of Trips ---------------------------------------------------------
## Number of Total Trips
sum(full_df$trips, na.rm = T)

## Number of Trips by Private/Shared
full_df %>%
  group_by(shared) %>%
  summarize(trips = sum(trips, na.rm = TRUE))

## Number of Trips by Private/Shared/Unmatched
full_df %>%
  group_by(trip_type) %>%
  summarize(trips = sum(trips, na.rm = TRUE))

## Number of Trips by Time of Day
full_df %>%
  group_by(time_of_day) %>%
  summarize(trips = sum(trips, na.rm = TRUE))


# Summary Statistics ------------------------------------------------------
## Trips and Distances
distance <- full_df %>%
  group_by(geoid_origin, geoid_dest, travel_distance) %>%
  summarize(trips = sum(trips, na.rm = TRUE))

weighted.mean(distance$travel_distance, 
              dplyr::coalesce(distance$trips, 0), 
              na.rm = TRUE)

## Trips and Fares
fare_summary <- full_df %>%
  group_by(geoid_origin, geoid_dest, fare, shared) %>%
  summarize(trips = sum(trips, na.rm = TRUE))


weighted.mean(fare_summary$fare[fare_summary$shared == "Private"], 
              dplyr::coalesce(fare_summary$trips[fare_summary$shared == "Private"], 0), 
              na.rm = TRUE)

weighted.mean(fare_summary$fare[fare_summary$shared == "Shared"], 
              dplyr::coalesce(fare_summary$trips[fare_summary$shared == "Shared"], 0), 
              na.rm = TRUE)

fare_summary_under60 <- full_df %>%
  filter(travel_time < 60)  %>%
  group_by(geoid_origin, geoid_dest, fare, shared) %>%
  summarize(trips = sum(trips, na.rm = TRUE))

weighted.mean(fare_summary_under60$fare[fare_summary_under60$shared == "Private"], 
              dplyr::coalesce(fare_summary_under60$trips[fare_summary_under60$shared == "Private"], 0), 
              na.rm = TRUE)

weighted.mean(fare_summary_under60$fare[fare_summary_under60$shared == "Shared"], 
              dplyr::coalesce(fare_summary_under60$trips[fare_summary_under60$shared == "Shared"], 0), 
              na.rm = TRUE)

## Travel Time
tt_summary <- full_df %>%
  group_by(geoid_origin, geoid_dest, travel_time) %>%
  summarize(trips = sum(trips, na.rm = TRUE))

weighted.mean(tt_summary$travel_time, 
              dplyr::coalesce(tt_summary$trips, 0), 
              na.rm = TRUE)


# Trips by TOD ------------------------------------------------------------
trips_by_tod <- full_df %>%
  group_by(time_of_day, trip_type) %>%
  summarize(trips = sum(trips, na.rm = TRUE))

trips_by_tod$time_of_day <- factor(trips_by_tod$time_of_day, levels=c("NT", "AM", "MD", "PM", "EV"))

ggplot(trips_by_tod, aes(x = time_of_day, y = trips, fill = trip_type, label = round(trips))) +
  geom_bar(position = "dodge", stat = "identity") +
  geom_text(aes(label = round(trips, digits = 0)), position = position_dodge(width = .9), vjust = -0.3, size = 2.5) +
  ggtitle("Trips by Time of Day") +
  xlab("Time of Day") + ylab("Trips") + guides(fill=guide_legend(title="Trip Type"))

# Map of Origins ----------------------------------------------------------
ky_map_data$trips[is.na(ky_map_data$trips)] <- 0
ky_map_data <- ky_map_data %>%
  rename(geoid_origin = GEOID)

origin_trips_map_df <- ky_map_data %>%
  select(geoid_origin, geometry, trips) %>%
  group_by(geoid_origin, geometry) %>%
  summarize(trips = sum(trips, na.rm = T))

origin_trips_map_df$trip_range <- 
  case_when(origin_trips_map_df$trips <= 20 ~ "Less than 20 trips",
            origin_trips_map_df$trips > 20 & origin_trips_map_df$trips <= 50 ~ "20 to 50 trips",
            origin_trips_map_df$trips > 50 & origin_trips_map_df$trips <= 100 ~ "50 to 100 trips",
            origin_trips_map_df$trips > 100 & origin_trips_map_df$trips <= 150 ~ "100 to 150 trips",
            origin_trips_map_df$trips > 150 & origin_trips_map_df$trips <= 200 ~ "150 to 200 trips",
            origin_trips_map_df$trips > 200 & origin_trips_map_df$trips <= 300 ~ "200 to 300 trips",
            origin_trips_map_df$trips > 300 & origin_trips_map_df$trips <= 400 ~ "300 to 400 trips",
            origin_trips_map_df$trips > 400 ~ "More than 400 trips"
            )

origin_trips_map_df$trip_range <- factor(origin_trips_map_df$trip_range, 
                                         levels=c("Less than 20 trips", 
                                                  "20 to 50 trips", 
                                                  "50 to 100 trips",
                                                  "100 to 150 trips", 
                                                  "150 to 200 trips",
                                                  "200 to 300 trips",
                                                  "300 to 400 trips",
                                                  "More than 400 trips"))


no_airport_origin <- origin_trips_map_df %>%
  filter(!geoid_origin %in% c(21067004207, 21015980100, 21111980100))

ggplot(origin_trips_map_df) +
  geom_sf(aes(fill = trip_range), 
          color = "black",
          linetype = 1,
          lwd = 0.001) +
  scale_fill_brewer(palette = "YlOrRd") + ggtitle("Number of Trips from Origin") +
  theme(axis.text.x=element_blank(),
        axis.text.y=element_blank(),
        axis.ticks=element_blank()) + 
  guides(fill=guide_legend(title="Number of Trips"))


# Urban/Rural -------------------------------------------------------------
## Read in Urban Areas from Census
link <- "https://www2.census.gov/geo/docs/reference/ua/2020_UA_BLOCKS.txt"
census_urban <- read.table(url(link), sep = "|")
## Clean Data
colnames(census_urban) <- census_urban[1, ]
census_urban <- census_urban[-1, ]
## Make columns (that need to be numeric) numeric
cols.num <- c("STATE","GEOID", "BLOCK")
census_urban[cols.num] <- sapply(census_urban[cols.num],as.numeric)

## Filter for relevant state
census_urban_ky <- census_urban %>%
  filter(STATE == 21)
### Make all column names lowercase
colnames(census_urban_ky) <- tolower(colnames(census_urban_ky))
census_urban_ky$geoid_origin <- as.numeric(gsub('.{4}$', '', as.character(census_urban_ky$GEOID)))
census_urban_ky <- census_urban_ky %>% 
  select(geoid_origin, state, county, tract, `2020_ua_name`)

origin_trips_map_df$urban <- ifelse(origin_trips_map_df$geoid_origin %in% census_urban_ky$geoid_origin, "urban", "rural")

sum(origin_trips_map_df$trips[origin_trips_map_df$urban == "urban"])
sum(origin_trips_map_df$trips[origin_trips_map_df$urban == "rural"])

# County Level ------------------------------------------------------------
origin_trips_map_df$county_fips <- as.numeric(substr(as.character(origin_trips_map_df$geoid_origin), 
                                          start = 1, stop = 5))

## Get County level data
link <- "https://www2.census.gov/geo/docs/reference/codes2020/cou/st21_ky_cou2020.txt"
counties <- read.table(url(link), sep = "|")
colnames(counties) <- counties[1, ]
counties <- counties[-1, ]
colnames(counties) <- tolower(colnames(counties))
counties$county_fips <- as.numeric(paste0(counties$statefp, counties$countyfp))
counties <- counties %>%
  select(countyname, county_fips)

origin_trips_df <- origin_trips_map_df %>%
  left_join(counties)

trips_by_county <- origin_trips_df %>%
  group_by(countyname) %>%
  summarize(trips = sum(trips))

rural <- origin_trips_df %>%
  filter(urban == "rural")
