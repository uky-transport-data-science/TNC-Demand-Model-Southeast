#### Fayette County, KY TNC Trip Analysis

# Set Working Directory ---------------------------------------------------
setwd("E:/CR2/Repos/TNC-Demand-Model-Southeast/analysis")

# Load Packages ----------------------------------------------------------
packages_vector <- c("tidyverse", "sf")
need_to_install <- packages_vector[!(packages_vector %in% installed.packages()[,"Package"])]
if (length(need_to_install)) install.packages(need_to_install)
lapply(packages_vector, library, character.only = TRUE)
options(scipen = 999)


# Read in Data ------------------------------------------------------------
load_data <- read.csv("../outputs/fayette_trips_long.csv")
load_data$time_of_day <- factor(load_data$time_of_day, levels = c("NT", "AM", "MD", "PM", "EV"))
load_data$trip_type <- factor(load_data$trip_type, levels = c("matched", "unmatched", "private"))

travel_time_fare_data <- read.csv('../Cleaned_Inputs/Intermediate/pred_trips.csv')

ky <- st_read('../Raw_Inputs/Shapefile Centroids/tl_2020_21_tract.shp')
ky$INTPTLAT <- as.numeric(ky$INTPTLAT)
ky$INTPTLON <- as.numeric(ky$INTPTLON)
ky$GEOID <- as.numeric(ky$GEOID)

ky_map_data <- right_join(ky, load_data, by = c("GEOID" = "origin"))
ky_map_data <- ky_map_data %>%
  rename("origin" = "GEOID")
  
# Clean Travel Time Data --------------------------------------------------
travel_time_data <- travel_time_fare_data[, c(1, 2, 4:6)]
travel_fare_data <- travel_time_fare_data[, c(1, 2, 4, 7, 8)]


# Trip Length Distribution ------------------------------------------------
ggplot(travel_time_data, aes(x=distance_miles)) + geom_histogram(color="white", fill="darkblue") +
  ggtitle("Trip Length Distribution")
print(summary(travel_time_data$distance_miles))


# Travel Time Distribution ------------------------------------------------
ggplot(travel_time_data, aes(x=PRIVATE_TRAVEL_TIME)) + geom_histogram(color="white", fill="darkblue") +
  ggtitle("Private Travel Time Distribution")
print(summary(travel_time_data$PRIVATE_TRAVEL_TIME))

ggplot(travel_time_data, aes(x=SHARED_TRAVEL_TIME)) + geom_histogram(color="white", fill="darkblue") +
  ggtitle("Shared Travel Time Distribution")
print(summary(travel_time_data$SHARED_TRAVEL_TIME))


# Fare Distribution -------------------------------------------------------
ggplot(travel_fare_data, aes(x=PRIVATE_TRIP_FARES)) + geom_histogram(color="white", fill="darkblue") +
  ggtitle("Private Fare Distribution")
print(summary(travel_fare_data$PRIVATE_TRIP_FARES))

ggplot(travel_fare_data, aes(x=SHARED_TRIP_FARES)) + geom_histogram(color="white", fill="darkblue") +
  ggtitle("Shared Fare Distribution")
print(summary(travel_fare_data$SHARED_TRIP_FARES))


# Grouped Bar Charts ------------------------------------------------------
trips_by_tod <- load_data %>%
  group_by(trip_type, time_of_day) %>%
  summarize(trips = sum(trips))

ggplot(trips_by_tod, aes(x = time_of_day, y = trips, fill = trip_type, label = round(trips))) +
  geom_bar(stat = "identity") +
  geom_text(size = 3, position = position_stack(vjust = 0.5)) +
  ggtitle("Trips by Time of Day")

airport_trips <- load_data %>%
  filter(origin == 21067004207 | destination == 21067004207) %>%
  group_by(trip_type, time_of_day) %>%
  summarize(trips = sum(trips))

ggplot(airport_trips, aes(x = time_of_day, y = trips, fill = trip_type, label = round(trips))) +
  geom_bar(stat = "identity") +
  geom_text(size = 3, position = position_stack(vjust = 0.5)) +
  ggtitle("Airport Trips by Time of Day")
 
non_airport_trips <- load_data %>%
  filter(origin != 21067004207 & destination != 21067004207) %>%
  group_by(trip_type, time_of_day) %>%
  summarize(trips = sum(trips))

ggplot(non_airport_trips, aes(x = time_of_day, y = trips, fill = trip_type, label = round(trips))) +
  geom_bar(stat = "identity") +
  geom_text(size = 3, position = position_stack(vjust = 0.5)) +
  ggtitle("Non-Airport Trips by Time of Day")


# Choropleth Maps ---------------------------------------------------------
non_airport_od_trips <- ky_map_data %>%
  group_by(origin, geometry, INTPTLAT, INTPTLON,
           STATEFP, COUNTYFP, TRACTCE, NAME, NAMELSAD, MTFCC, 
           FUNCSTAT, ALAND, AWATER) %>%
  summarize(trips = sum(trips)) %>%
  filter(origin != 21067004207)

ggplot() + geom_sf(data = non_airport_od_trips, aes(fill = trips)) +
  scale_fill_gradient2(midpoint = 30) +
  ggtitle("Non-Airport Trips from Origin") +
  theme(axis.text.x=element_blank(),
        axis.text.y=element_blank(),
        axis.ticks=element_blank())

##### Zip Code data from California
