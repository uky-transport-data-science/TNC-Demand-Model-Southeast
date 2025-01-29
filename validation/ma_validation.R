### TNC SE Validation
## Uses Massachusetts 2019 TNC Data to validate TNC SE model

# Set Working Directory ---------------------------------------------------
setwd("E:/CR2/Repos/TNC-Demand-Model-Southeast/validation")

# Load Packages -----------------------------------------------------------
packages_vector <- c("tidyverse", "sf", "tigris", "collapse", "data.table", "janitor")
need_to_install <- packages_vector[!(packages_vector %in% installed.packages()[,"Package"])]
if (length(need_to_install)) install.packages(need_to_install)
lapply(packages_vector, library, character.only = TRUE)
options(scipen = 999)

# Load in Data ------------------------------------------------------------
## Modeled Output
modeled_ma_read <- fread("./inputs/MA_trips_final_long_baseline.csv")

## Observed Output
observed_ma_read <- read.xlsx("./inputs/MA_observed_2019.xlsx", sheet = 1)

## Census Tracts to County (used for modeled)
county_fips_read <- read.csv(url("https://www2.census.gov/geo/docs/reference/codes/files/st25_ma_cou.txt"), colClasses=c("X001"="character"))

## Cities to County (used for observed)
city_county_read <- read.csv("./inputs/MA_city_county.csv")


# Cleaning Data -----------------------------------------------------------
## Clean County FIPS -----------------------------------------------------
county_fips_first_row <- colnames(county_fips_read)
county_fips <- rbind(county_fips_first_row, county_fips_read)
county_fips <- county_fips %>%
  select(2, 3, 4)
colnames(county_fips) <- c("state_no", "county_no", "county")

county_fips$state_no <- str_sub(county_fips$state_no, -2, -1)
county_fips$county_no <- str_sub(county_fips$county_no, -3, -1)
county_fips[1, 3] <- "Barnstable County"

county_fips$fips <- with(county_fips, paste0(state_no, county_no))
county_fips$fips <- as.numeric(county_fips$fips)
county_fips <- county_fips %>%
  select(4, 3)

## Clean City County Data --------------------------------------------------
city_county <- city_county_read %>%
  select(2, 5) %>%
  rename(city = City.Town, county = County)

city_county$city <- str_to_title(city_county$city)
city_county$county <- str_to_title(city_county$county)
city_county$county <- paste(city_county$county, "County", sep = " ")

## Clean Modeled Data ------------------------------------------------------
head(modeled_ma_read)
modeled_ma_origin <- modeled_ma_read %>%
  select(geoid_origin, trips) %>%
  group_by(geoid_origin) %>%
  summarize(origin_trips = sum(trips, na.rm = T)) 

modeled_ma_origin$fips <- as.numeric(substr(as.character(modeled_ma_origin$geoid_origin), 1, 5))
modeled_ma_origin <- modeled_ma_origin %>%
  left_join(county_fips, by = "fips") %>%
  select(county, origin_trips) %>%
  group_by(county) %>%
  summarize(origin_trips = sum(origin_trips))

modeled_ma_dest <- modeled_ma_read %>%
  select(geoid_dest, trips) %>%
  group_by(geoid_dest) %>%
  summarize(dest_trips = sum(trips, na.rm = T)) 

modeled_ma_dest$fips <- as.numeric(substr(as.character(modeled_ma_dest$geoid_dest), 1, 5))
modeled_ma_dest <- modeled_ma_dest %>%
  left_join(county_fips, by = "fips") %>%
  select(county, dest_trips)%>%
  group_by(county) %>%
  summarize(dest_trips = sum(dest_trips))

### Final Modeled Dataset
modeled_ma <- inner_join(modeled_ma_origin, modeled_ma_dest, by = "county") %>%
  rename(origin_trips_modeled = origin_trips,
         dest_trips_modeled = dest_trips)

## Clean Observed Data -------------------------------------------
observed_ma_city <- observed_ma_read %>%
  select(1, 3, 4) %>%
  rename(city = MUNICIPALITY,
         origin_trips_observed = ORIGIN_TRIPS,
         dest_trips_observed = DESTINATION_TRIPS)

observed_ma_city$city <- str_to_title(observed_ma_city$city)

observed_ma_origin <- observed_ma_city %>% 
  left_join(city_county, by = "city") %>%
  select(county, origin_trips_observed) %>% 
  group_by(county) %>%
  summarize(origin_trips_observed = sum(origin_trips_observed))
  
observed_ma_dest <- observed_ma_city %>% 
  left_join(city_county, by = "city") %>%
  select(county, dest_trips_observed) %>% 
  group_by(county) %>%
  summarize(dest_trips_observed = sum(dest_trips_observed))

### Final Observed Dataset
observed_ma <- inner_join(observed_ma_origin, observed_ma_dest, by = "county")

## Final Merge -------------------------------------------------------
validation_ma <- inner_join(modeled_ma, observed_ma, by = "county")

### Annualize Modeled Data
validation_ma$origin_trips_modeled <- validation_ma$origin_trips_modeled*252
validation_ma$dest_trips_modeled <- validation_ma$dest_trips_modeled*252

rm(list=setdiff(ls(), c("validation_ma", "observed_ma", "modeled_ma")))


# Validation Plots --------------------------------------------------------
ggplot(validation_ma, aes(x=origin_trips_observed, y=origin_trips_modeled, label = county)) + 
  geom_point() + geom_abline(intercept = 0, slope = 1, color = "navy", linetype = "dashed") +
  xlab("Observed Trips") + ylab("Modeled Trips") +
  ggtitle("Validation Plot for County Origins")

ggplot(validation_ma, aes(x=dest_trips_observed, y=dest_trips_modeled, label = county)) + 
  geom_point() + geom_abline(intercept = 0, slope = 1, color = "navy", linetype = "dashed") +
  xlab("Observed Trips") + ylab("Modeled Trips") +
  ggtitle("Validation Plot for County Destinations")


# Differences -------------------------------------------------------------
validation_ma$origin_pct_diff <- (validation_ma$origin_trips_modeled - validation_ma$origin_trips_observed) / validation_ma$origin_trips_modeled
validation_ma$dest_pct_diff <- (validation_ma$dest_trips_modeled - validation_ma$dest_trips_observed) / validation_ma$dest_trips_modeled


# Model Fit ---------------------------------------------------------------
origin_fit <- lm(origin_trips_modeled ~ origin_trips_observed, validation_ma)
summary(origin_fit)$r.squared

dest_fit <- lm(dest_trips_modeled ~ dest_trips_observed, validation_ma)
summary(dest_fit)$r.squared


# Ratio of Observed to Modeled --------------------------------------------
sum(validation_ma$origin_trips_observed) / sum(validation_ma$origin_trips_modeled)



# Model Output Origin Map -------------------------------------------------
ma <- tracts(state = "MA", year = 2019)
ma$INTPTLAT <- as.numeric(ma$INTPTLAT)
ma$INTPTLON <- as.numeric(ma$INTPTLON)
ma$GEOID <- as.numeric(ma$GEOID)

modeled_ma_read <- fread("./inputs/MA_trips_final_long_baseline.csv")
modeled_ma_origin <- modeled_ma_read %>%
  select(geoid_origin, trips) %>%
  group_by(geoid_origin) %>%
  summarize(origin_trips = sum(trips, na.rm = T)) 

ma_map_data <- left_join(ma, modeled_ma_origin, by = c("GEOID" = "geoid_origin")) %>%
  select(GEOID, origin_trips, geometry)
ma_map_data$origin_trips[is.na(ma_map_data$origin_trips)] <- 0

ma_map_data$trip_range <- 
  case_when(ma_map_data$origin_trips <= 20 ~ "Less than 20 trips",
            ma_map_data$origin_trips > 20 & ma_map_data$origin_trips <= 50 ~ "20 to 50 trips",
            ma_map_data$origin_trips > 50 & ma_map_data$origin_trips <= 100 ~ "50 to 100 trips",
            ma_map_data$origin_trips > 100 & ma_map_data$origin_trips <= 200 ~ "100 to 200 trips",
            ma_map_data$origin_trips > 200 & ma_map_data$origin_trips <= 500 ~ "200 to 500 trips",
            ma_map_data$origin_trips > 500 & ma_map_data$origin_trips <= 1000 ~ "500 to 1000 trips",
            ma_map_data$origin_trips > 1000 & ma_map_data$origin_trips <= 5000 ~ "1000 to 5000 trips",
            ma_map_data$origin_trips > 5000 ~ "More than 5000 trips"
  )

ma_map_data$trip_range <- factor(ma_map_data$trip_range, 
                                         levels=c("Less than 20 trips", 
                                                  "20 to 50 trips", 
                                                  "50 to 100 trips",
                                                  "100 to 200 trips", 
                                                  "200 to 500 trips",
                                                  "500 to 1000 trips",
                                                  "1000 to 5000 trips",
                                                  "More than 5000 trips"))

ggplot(ma_map_data) +
  geom_sf(aes(fill = trip_range), 
          color = "black",
          linetype = 1,
          lwd = 0.001) +
  scale_fill_brewer(palette = "YlOrRd") + ggtitle("Massachusetts Modeled Trips by Origin (Daily)") +
  theme(axis.text.x=element_blank(),
        axis.text.y=element_blank(),
        axis.ticks=element_blank()) + 
  guides(fill=guide_legend(title="Number of Trips"))


# Observed Output Origin Map ----------------------------------------------
## Observed Output
observed_ma_read <- read.xlsx("./inputs/MA_observed_2019.xlsx", sheet = 1)
ma_city <- st_read("./inputs/townssurvey_shp/TOWNSSURVEY_POLYM.shp") %>%
  select(TOWN, geometry) %>%
  rename(city = TOWN)

observed_ma_origin <- observed_ma_read %>%
  select(MUNICIPALITY, ORIGIN_TRIPS) %>%
  rename(city = MUNICIPALITY, origin_trips = ORIGIN_TRIPS)

ma_city$city <- str_to_title(ma_city$city)
ma_city$city[ma_city$city=="Manchester-By-The-Sea"]<- "Manchester"

observed_ma_origin$city <- sub("_", " ", observed_ma_origin$city)
observed_ma_origin$city <- str_to_title(observed_ma_origin$city)

ma_map_data <- inner_join(ma_city, observed_ma_origin)
ma_map_data$origin_trips <- ma_map_data$origin_trips/252
ma_map_data$trip_range <- 
  case_when(ma_map_data$origin_trips <= 20 ~ "Less than 20 trips",
            ma_map_data$origin_trips > 20 & ma_map_data$origin_trips <= 50 ~ "20 to 50 trips",
            ma_map_data$origin_trips > 50 & ma_map_data$origin_trips <= 100 ~ "50 to 100 trips",
            ma_map_data$origin_trips > 100 & ma_map_data$origin_trips <= 200 ~ "100 to 200 trips",
            ma_map_data$origin_trips > 200 & ma_map_data$origin_trips <= 500 ~ "200 to 500 trips",
            ma_map_data$origin_trips > 500 & ma_map_data$origin_trips <= 1000 ~ "500 to 1000 trips",
            ma_map_data$origin_trips > 1000 & ma_map_data$origin_trips <= 5000 ~ "1000 to 5000 trips",
            ma_map_data$origin_trips > 5000 ~ "More than 5000 trips"
  )

ma_map_data$trip_range <- factor(ma_map_data$trip_range, 
                                 levels=c("Less than 20 trips", 
                                          "20 to 50 trips", 
                                          "50 to 100 trips",
                                          "100 to 200 trips", 
                                          "200 to 500 trips",
                                          "500 to 1000 trips",
                                          "1000 to 5000 trips",
                                          "More than 5000 trips"))


ggplot(ma_map_data) +
  geom_sf(aes(fill = trip_range), 
          color = "black",
          linetype = 1,
          lwd = 0.001) +
  scale_fill_brewer(palette = "YlOrRd") + ggtitle("Massachusetts Observed Trips by Origin (Daily)") +
  theme(axis.text.x=element_blank(),
        axis.text.y=element_blank(),
        axis.ticks=element_blank()) + 
  guides(fill=guide_legend(title="Number of Trips"))


# Trip Origins per Square Mile vs Density ---------------------------------


