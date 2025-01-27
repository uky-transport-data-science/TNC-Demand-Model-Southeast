using CSV
using OSRM
using DataFrames
using Geodesy
using ArchGDAL
import GeoFormatTypes as GFT
using GeoDataFrames
using ThreadsX
using Downloads
using JSON
using PyCall

root = dirname(@__FILE__)
cd(abspath(joinpath(root, "..")))

config = JSON.parsefile("model_config.json")
study_state = config["study_state"]

od_filename = string(study_state, "_centroid_points.csv")
p = joinpath(root, od_filename)
od_table = CSV.read(p, DataFrame, types=Dict(1=>Float64, 2=>Float64, 3=>Float64, 4=>Float64, 5=>Float64, 6=>Float64,))

if study_state == "KY"
    if isfile(joinpath(root, "kentucky-latest.osrm.fileIndex"))
        println("Network file exists...")
        osrm_path = joinpath(root, "kentucky-latest.osrm")
        osrm = OSRMInstance(osrm_path, OSRM.Algorithm.MultiLevelDijkstra)
    else
        println("Downloading files and building network..")
        Downloads.download("https://download.geofabrik.de/north-america/us/kentucky-latest.osm.pbf", joinpath(root, "kentucky-latest.osm.pbf"))
        osm_path = joinpath(root, "kentucky-latest.osm.pbf")
        osrm_path = joinpath(root, "kentucky-latest.osrm")
        osrm = OSRMInstance(osrm_path, OSRM.Algorithm.MultiLevelDijkstra)
    end
elseif study_state == "AL"
    if isfile(joinpath(root, "alabama-latest.osrm.fileIndex"))
        println("Network file exists...")
        osrm_path = joinpath(root, "alabama-latest.osrm")
        osrm = OSRMInstance(osrm_path, OSRM.Algorithm.MultiLevelDijkstra)
    else
        println("Downloading files and building network..")
        Downloads.download("https://download.geofabrik.de/north-america/us/alabama-latest.osm.pbf", joinpath(root, "alabama-latest.osm.pbf"))
        osm_path = joinpath(root, "alabama-latest.osm.pbf")
        osrm_path = joinpath(root, "alabama-latest.osrm")
        osrm = OSRMInstance(osrm_path, OSRM.Algorithm.MultiLevelDijkstra)
    end
elseif study_state == "MA"
    if isfile(joinpath(root, "massachusetts-latest.osrm.fileIndex"))
        println("Network file exists...")
        osrm_path = joinpath(root, "massachusetts-latest.osrm")
        osrm = OSRMInstance(osrm_path, OSRM.Algorithm.MultiLevelDijkstra)
    else
        println("Downloading files and building network..")
        Downloads.download("https://download.geofabrik.de/north-america/us/massachusetts-latest.osm.pbf", joinpath(root, "massachusetts-latest.osm.pbf"))
        osm_path = joinpath(root, "massachusetts-latest.osm.pbf")
        OSRM.build(osm_path, OSRM.Profiles.Car, OSRM.Algorithm.MultiLevelDijkstra)
        osrm_path = joinpath(root, "massachusetts-latest.osrm")
        osrm = OSRMInstance(osrm_path, OSRM.Algorithm.MultiLevelDijkstra)
    end
elseif study_state == "MS"
    if isfile(joinpath(root, "mississippi-latest.osrm.fileIndex"))
        println("Network file exists...")
        osrm = OSRMInstance(osrm_path, OSRM.Algorithm.MultiLevelDijkstra)
    else
        println("Downloading files and building network..")
        Downloads.download("https://download.geofabrik.de/north-america/us/mississippi-latest.osm.pbf", joinpath(root, "mississippi-latest.osm.pbf"))
        osm_path = joinpath(root, "mississippi-latest.osm.pbf")
        osrm_path = joinpath(root, "mississippi-latest.osrm")
        osrm = OSRMInstance(osrm_path, OSRM.Algorithm.MultiLevelDijkstra)
    end
elseif study_state == "NC"
    if isfile(joinpath(root, "north-carolina-latest.osrm.fileIndex"))
        println("Network file exists...")
        osrm = OSRMInstance(osrm_path, OSRM.Algorithm.MultiLevelDijkstra)
    else
        println("Downloading files and building network..")
        Downloads.download("https://download.geofabrik.de/north-america/us/north-carolina-latest.osm.pbf", joinpath(root, "north-carolina-latest.osm.pbf"))
        osm_path = joinpath(root, "north-carolina-latest.osm.pbf")
        osrm_path = joinpath(root, "north-carolina-latest.osrm")
        osrm = OSRMInstance(osrm_path, OSRM.Algorithm.MultiLevelDijkstra)
    end
elseif study_state == "FL"
    if isfile(joinpath(root, "florida-latest.osrm.fileIndex"))
        println("Network file exists...")
        osrm = OSRMInstance(osrm_path, OSRM.Algorithm.MultiLevelDijkstra)
    else
        println("Downloading files and building network..")
        Downloads.download("https://download.geofabrik.de/north-america/us/florida-latest.osm.pbf", joinpath(root, "florida-latest.osm.pbf"))
        osm_path = joinpath(root, "florida-latest.osm.pbf")
        osrm_path = joinpath(root, "florida-latest.osrm")
        osrm = OSRMInstance(osrm_path, OSRM.Algorithm.MultiLevelDijkstra)
    end
elseif study_state == "GA"
    if isfile(joinpath(root, "georgia-latest.osrm.fileIndex"))
        println("Network file exists...")
        osrm = OSRMInstance(osrm_path, OSRM.Algorithm.MultiLevelDijkstra)
    else
        println("Downloading files and building network..")
        Downloads.download("https://download.geofabrik.de/north-america/us/georgia-latest.osm.pbf", joinpath(root, "georgia-latest.osm.pbf"))
        osm_path = joinpath(root, "georgia-latest.osm.pbf")
        osrm_path = joinpath(root, "georgia-latest.osrm")
        osrm = OSRMInstance(osrm_path, OSRM.Algorithm.MultiLevelDijkstra)
    end
elseif study_state == "SC"
    if isfile(joinpath(root, "south-carolina-latest.osrm.fileIndex"))
        println("Network file exists...")
        osrm = OSRMInstance(osrm_path, OSRM.Algorithm.MultiLevelDijkstra)
    else
        println("Downloading files and building network..")
        Downloads.download("https://download.geofabrik.de/north-america/us/south-carolina-latest.osm.pbf", joinpath(root, "south-carolina-latest.osm.pbf"))
        osm_path = joinpath(root, "south-carolina-latest.osm.pbf")
        osrm_path = joinpath(root, "south-carolina-latest.osrm")
        osrm = OSRMInstance(osrm_path, OSRM.Algorithm.MultiLevelDijkstra)
    end
elseif study_state == "TN"
    if isfile(joinpath(root, "tennessee-latest.osrm.fileIndex"))
        println("Network file exists...")
        osrm = OSRMInstance(osrm_path, OSRM.Algorithm.MultiLevelDijkstra)
    else
        println("Downloading files and building network..")
        Downloads.download("https://download.geofabrik.de/north-america/us/tennessee-latest.osm.pbf", joinpath(root, "tennessee-latest.osm.pbf"))
        osm_path = joinpath(root, "tennessee-latest.osm.pbf")
        osrm_path = joinpath(root, "tennessee-latest.osrm")
        osrm = OSRMInstance(osrm_path, OSRM.Algorithm.MultiLevelDijkstra)
    end
end

### Need for speed
study_file = string(study_state, "_travel_time_distance.csv")
if isfile(joinpath("./outputs/", study_file))
    println("Since travel times and distances exist for this state, moving on...")
else
    println("Routing travel time and distance, this will take a long time...")
    travel_distance = Array{Float64}(undef, nrow(od_table))
    travel_time = Array{Float64}(undef, nrow(od_table))
    #od_table = od_table[1:538022, :]
    #od_table_chunk2 = od_table[538023:1076044, :]
    #od_table_chunk3 = od_table[1076045:1614066, :]
    #od_table_chunk4 = od_table[1614066:2152088, :]
    for i in 1:nrow(od_table)
            travel_distance[i] = OSRM.distance_matrix(osrm, 
            [LatLon(od_table.origin_y[i], od_table.origin_x[i])],
            [LatLon(od_table.dest_y[i],  od_table.dest_x[i])]).distance_meters[1, 1]
            travel_time[i]= OSRM.distance_matrix(osrm, 
            [LatLon(od_table.origin_y[i], od_table.origin_x[i])],
            [LatLon(od_table.dest_y[i],  od_table.dest_x[i])]).duration_seconds[1, 1]
    end
    od_table[!, :travel_distance] = travel_distance / 1609.34
    od_table[!, :travel_time] = travel_time / 60
    CSV.write(joinpath("./outputs/", study_file), od_table)
end