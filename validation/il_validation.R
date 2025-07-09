## Calibration Parameter Adjustment
setwd("E:/CR2/Repos/TNC-Demand-Model-Southeast/validation")

library(data.table)
library(tidyverse)
### Alex Data (this gets tracts in Chicago)
dropbox_md <- fread("../comparison/from_dropbox_md.csv")
geoid_dropbox <- unique(dropbox_md$ORIGIN)

### Get TNCSE output and filter for tracts in Chicago
tncse <- fread("../outputs/IL_neg_bin_pred_trips_baseline.csv")

tncse <- tncse %>%
  select(geoid_origin, nt_pickups, am_pickups, md_pickups, pm_pickups, ev_pickups) %>%
  distinct()

## Create comparison df
nt_observed <- 36972	           
am_observed <- 34143
md_observed <- 77707
pm_observed <- 48426	
ev_observed <- 46151

comparison_il <- data.frame("tod" = c("nt", "am", "md", "pm", "ev"),
  "observed" = c(nt_observed, am_observed, md_observed, pm_observed, ev_observed),
  "modeled" = c(sum(tncse$nt_pickups, na.rm = T),
                sum(tncse$am_pickups, na.rm = T), 
                sum(tncse$md_pickups, na.rm = T), 
                sum(tncse$pm_pickups, na.rm = T), 
                sum(tncse$ev_pickups, na.rm = T)))
comparison_il$pct_diff <- (comparison_il$modeled - comparison_il$observed) / comparison_il$observed



