### TNC SE Validation
## Uses Massachusetts 2019 TNC Data to validate TNC SE model

# Set Working Directory ---------------------------------------------------
setwd("E:/CR2/Repos/TNC-Demand-Model-Southeast/validation")

# Load Packages -----------------------------------------------------------
packages_vector <- c("tidyverse", "sf", "tigris", "collapse", "data.table", "janitor", "tools", "openxlsx")
need_to_install <- packages_vector[!(packages_vector %in% installed.packages()[,"Package"])]
if (length(need_to_install)) install.packages(need_to_install)
lapply(packages_vector, library, character.only = TRUE)
options(scipen = 999)

# Load in Data ------------------------------------------------------------
## With Tourism
ma_with_tourism_read <- fread("../outputs/MA_trips_final_long_with_tourism.csv")
ma_with_tourism_read$tourism <- "with_tourism"

## No Tourism
ma_no_tourism_read <- fread("../outputs/MA_trips_final_long_no_tourism.csv")
ma_no_tourism_read$tourism <- "no_tourism"

### Combine
modeled_ma_read <- rbind(ma_with_tourism_read, ma_no_tourism_read)

## Observed Output
observed_ma_read <- read.xlsx("./inputs/MA_observed_2019.xlsx", sheet = 1)

## Census Tracts to County (used for modeled)
county_fips_read <- read.csv("./inputs/MA_xwalk_fips.csv")


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
county_fips[1, 2] <- "001"

county_fips[c(2:5), 2] <- paste0("00", county_fips[c(2:5), 2])
county_fips[c(6:14), 2] <- paste0("0", county_fips[c(6:14), 2])

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
city_county$city[city_county$city=="Manchester-By-The-Sea"]<- "Manchester"

## Clean Modeled Data ------------------------------------------------------
#head(modeled_ma_read)
#modeled_ma_read$trips[!is.finite(modeled_ma_read$trips)] <- 0
modeled_ma_origin <- modeled_ma_read %>%
  select(geoid_origin, tourism, trips) %>%
  group_by(geoid_origin, tourism) %>%
  summarize(origin_trips = round(sum(trips, na.rm = T)))

modeled_ma_origin$fips <- as.numeric(substr(as.character(modeled_ma_origin$geoid_origin), 1, 5))
modeled_ma_origin <- modeled_ma_origin %>%
  left_join(county_fips, by = "fips") %>%
  select(county, origin_trips, tourism) %>%
  group_by(county, tourism) %>%
  summarize(origin_trips = round(sum(origin_trips)))

## Make this wide
modeled_ma_origin <- spread(modeled_ma_origin, tourism, origin_trips)
colnames(modeled_ma_origin) <- c("county", "origin_modeled_no_tourism", "origin_modeled_with_tourism")

modeled_ma_dest <- modeled_ma_read %>%
  select(geoid_dest, tourism, trips) %>%
  group_by(geoid_dest, tourism) %>%
  summarize(dest_trips = round(sum(trips, na.rm = T)))

modeled_ma_dest$fips <- as.numeric(substr(as.character(modeled_ma_dest$geoid_dest), 1, 5))
modeled_ma_dest <- modeled_ma_dest %>%
  left_join(county_fips, by = "fips") %>%
  select(county, dest_trips, tourism)%>%
  group_by(county, tourism) %>%
  summarize(dest_trips = round(sum(dest_trips)))

## Make this wide
modeled_ma_dest <- spread(modeled_ma_dest, tourism, dest_trips)
colnames(modeled_ma_dest) <- c("county", "dest_modeled_no_tourism", "dest_modeled_with_tourism")

### Final Modeled Dataset
modeled_ma <- inner_join(modeled_ma_origin, modeled_ma_dest, by = "county") 

## Clean Observed Data -------------------------------------------
observed_ma_city <- observed_ma_read %>%
  select(1, 3, 4) %>%
  rename(city = MUNICIPALITY,
         origin_trips_observed = ORIGIN_TRIPS,
         dest_trips_observed = DESTINATION_TRIPS)

observed_ma_city$city <- str_to_title(observed_ma_city$city)
observed_ma_city$city <- sub("_", " ", observed_ma_city$city)
observed_ma_city$city <- toTitleCase(observed_ma_city$city)

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

### Make Annual Data Daily
validation_ma$origin_trips_observed <- round(validation_ma$origin_trips_observed/252)
validation_ma$dest_trips_observed <- round(validation_ma$dest_trips_observed/252)

### Remove county from the end
validation_ma$county <- str_replace(validation_ma$county, "County", "")
#rm(list=setdiff(ls(), c("validation_ma", "observed_ma", "modeled_ma")))
# validation_ma <- validation_ma %>%
#   filter(!county %in% c("Barnstable County", "Suffolk County", "Middlesex County"))

# Validation Plots --------------------------------------------------------
ggplot(validation_ma, aes(x=origin_trips_observed, y=origin_modeled_no_tourism, label = county)) + 
  geom_point() + geom_abline(intercept = 0, slope = 1, color = "navy", linetype = "dashed") +
  xlab("Observed Trips") + ylab("Modeled Trips") + xlim(0, 200000) + ylim(0, 125000) +
  ggtitle("Massachusetts Validation Plot for County Origins (No Tourism)") + geom_text(data=subset(validation_ma, origin_trips_observed > 10000),
                                                            aes(x=origin_trips_observed, y=origin_modeled_no_tourism,label=county),
                                                            size = 3, hjust = -0.1, vjust = 0.1)

ggplot(validation_ma, aes(x=origin_trips_observed, y=origin_modeled_with_tourism, label = county)) +
  geom_point() + geom_abline(intercept = 0, slope = 1, color = "navy", linetype = "dashed") +
  xlab("Observed Trips") + ylab("Modeled Trips") + xlim(0, 200000) + ylim(0, 125000) +
  ggtitle("Massachusetts Validation Plot for County Origins (With Tourism)") + geom_text(data=subset(validation_ma, origin_trips_observed > 10000),
                                  aes(x=origin_trips_observed, y=origin_modeled_with_tourism,label=county),
                                  size = 3, hjust = -0.1, vjust = 0.1)

# Validtaion (Origin) Table ----------------------------------------------------
origin_validation <- validation_ma %>% 
  select(starts_with("origin"))

write.csv(origin_validation, "./outputs/ma_validation.csv", row.names = F)


# Model Fit ---------------------------------------------------------------
origin_fit_no_tourism <- lm(origin_modeled_no_tourism ~ origin_trips_observed, validation_ma)
summary(origin_fit_no_tourism)$r.squared

origin_fit_with_tourism <- lm(origin_modeled_with_tourism ~ origin_trips_observed, validation_ma)
summary(origin_fit_with_tourism)$r.squared
