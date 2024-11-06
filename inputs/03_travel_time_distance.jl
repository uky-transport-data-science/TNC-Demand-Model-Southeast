using CSV
using OSRM
using DataFrames
using Geodesy
using ArchGDAL
import GeoFormatTypes as GFT
using GeoDataFrames
using ThreadsX

#import Pkg; Pkg.add("DataFrames")

root = dirname(@__FILE__)
p = joinpath(root, "centroid_points.csv")
od_table = CSV.read(p, DataFrame, types=Dict(1=>Float64, 2=>Float64, 3=>Float64, 4=>Float64, 5=>Float64, 6=>Float64,))

#osm_path = joinpath(root, "kentucky-latest.osm.pbf")
#OSRM.build(osm_path, OSRM.Profiles.Car, OSRM.Algorithm.MultiLevelDijkstra)

osrm_path = joinpath(root, "kentucky-latest.osrm")
osrm = OSRMInstance(osrm_path, OSRM.Algorithm.MultiLevelDijkstra)


travel_distance = Array{Float64}(undef, nrow(od_table))
travel_time = Array{Float64}(undef, nrow(od_table))
for i in 1:nrow(od_table)
    travel_distance[i] = OSRM.distance_matrix(osrm, 
    [LatLon(od_table.origin_y[i], od_table.origin_x[i])],
    [LatLon(od_table.dest_y[i],  od_table.dest_x[i])]).distance_meters[1, 1]
    travel_time[i ]= OSRM.distance_matrix(osrm, 
    [LatLon(od_table.origin_y[i], od_table.origin_x[i])],
    [LatLon(od_table.dest_y[i],  od_table.dest_x[i])]).duration_seconds[1, 1]
end

od_table[!, :travel_distance] = travel_distance / 1609.34
od_table[!, :travel_time] = travel_time / 60

CSV.write("/mnt/e/CR2/Repos/TNC-Demand-Model-Southeast/outputs/travel_time_distance.csv", od_table)
