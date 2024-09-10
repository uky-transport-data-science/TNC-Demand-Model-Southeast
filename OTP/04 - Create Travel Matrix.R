### Creating a Travel Time and Distance Matrix for each OD Pair
## Requires: R 4.4.1
## Author: Neeco Beltran

# Set Working Directory ---------------------------------------------------
wd <- "E:/CR2/ReposTNC-Demand-Model-Southeast/OTP"
setwd(wd)

# Load Packages ----------------------------------------------------------
packages_vector <- c("tidyverse", "rjson", "opentripplanner", "tmap")
need_to_install <- packages_vector[!(packages_vector %in% installed.packages()[,"Package"])]
if (length(need_to_install)) install.packages(need_to_install)
lapply(packages_vector, library, character.only = TRUE)
options(scipen = 999)


# Build OTP Graph Object --------------------------------------------------
# path_otp <- paste0(getwd(), "/", "otp-1.4.0-shaded.jar")
# path_data <- wd
# graph <- otp_build_graph(otp = path_otp, dir = path_data, router = "kentucky", memory = 10240) 

# OTP Connection ----------------------------------------------------------
otpcon <- otp_connect(hostname =  "localhost",
                      router = "default",
                      port = 8080)


# Centroids ---------------------------------------------------------------
## Read CSV of Centroids
centroids <- read.csv("./centroid_points.csv")[, -1]

## Create dataframe and matrix of origins
origin <- centroids[rep(seq(1, nrow(centroids)), times = nrow(centroids)),]
origin_mat <- as.matrix(origin[, c(1, 2)])

## Create dataframe and matrix of destinations
destination <- centroids[rep(seq(1, nrow(centroids)), each  = nrow(centroids)),]
destination_mat <- as.matrix(destination[, c(1, 2)])


# Travel Times ------------------------------------------------------------
## Creates Travel Time Dataframe
# route <- otp_plan(otpcon, 
#  fromPlace = c(-84.50254, 38.05170), 
#  toPlace = c(-84.54088, 38.03660))

routes <- otp_plan(otpcon = otpcon,
                   fromPlace = origin_mat,
                   toPlace = destination_mat,
                   fromID = as.character(origin$GEOID),
                   toID = as.character(destination$GEOID),
                   get_geometry = FALSE,
                   distance_balance = TRUE,
                   ncores = 6)

## Clean Travel Time Dataframe
travel_time_df <- routes[, c("fromPlace","toPlace","duration", "leg_distance")]
travel_time_df$travel_time_min <- travel_time_df$duration/60
travel_time_df$distance_km <- travel_time_df$leg_distance/1000
travel_time_df$distance_miles <- travel_time_df$leg_distance/1609.34
travel_time_df <- travel_time_df[c(1:3, 5:7)]
colnames(travel_time_df) <- c("origin", "destination", "travel_time_sec", "travel_time_min", "distance_km", "distance_miles")

within_tract <- data.frame("origin" = unique(origin$GEOID),
                           "destination" = unique(origin$GEOID), ## Since it's within the same tract
                           "travel_time_sec" = 0,
                           "travel_time_min" = 0,
                           "distance_km" = 0,
                           "distance_miles" = 0)

travel_time_df <- rbind(travel_time_df, within_tract)

od_df <- travel_time_df[, c("origin", "destination", "travel_time_min")]
od_matrix <- tidyr::pivot_wider(od_df, 
                                    names_from = "destination", 
                                    values_from = "travel_time_min")
# Write to CSV ------------------------------------------------------------
write.csv(travel_time_df, "./Car Travel Times/traveltime.csv", row.names = FALSE)

