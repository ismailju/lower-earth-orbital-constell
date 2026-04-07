import json
import graph_plot.graph1 as graph1     # Original graph for satellites
import graph_plot.graph2 as graph2   # Graph for regions
import graph_plot.graph3 as graph3   # Graph for stations

def plot_from_json_for_satellites(json_filepath):
    # 1. Open the file and load the dictionary back into Python
    with open(json_filepath, 'r') as file:
        imported_data = json.load(file)

    # 2. Extract the dynamic data lists
    results = imported_data["results"]
    acc1 = results["accuracies_algo1"]
    acc2 = results["accuracies_algo2"]
    sats = results["sats_list"]           # <--- Extracting sats list
    validated = results["validated_collections"]
    expected = results["expected_collections"]


    # 3. Extract the static metadata
    meta = imported_data["metadata"]
    stations = meta["no_of_stations"]
    horizon = meta["time_horizon"]
    regions = meta["no_of_regions"]       # <--- Extracting fixed regions

    # 4. Pass the extracted data straight into your satellite plotting function
    print(f"Plotting satellite data from {json_filepath}...")
    graph1.graph(
        total_accuracies1=acc1, 
        total_accuracies2=acc2, 
        no_of_sats=sats,                  # <--- Passing sats to X-axis
        no_of_stations=stations, 
        time_horizon=horizon, 
        no_of_regions=regions             # <--- Passing fixed regions to the text box
    )
def plot_from_json_for_satellites_by_collections(json_filepath):
    # 1. Open the file and load the dictionary back into Python
    with open(json_filepath, 'r') as file:
        imported_data = json.load(file)

    # 2. Extract the dynamic data lists
    results = imported_data["results"]
    acc1 = results["accuracies_algo1"]
    acc2 = results["accuracies_algo2"]
    sats = results["sats_list"]           # <--- Extracting sats list
    validated = results["validated_collections"]
    expected = results["expected_collections"]


    # 3. Extract the static metadata
    meta = imported_data["metadata"]
    stations = meta["no_of_stations"]
    horizon = meta["time_horizon"]
    regions = meta["no_of_regions"]       # <--- Extracting fixed regions

    # 4. Pass the extracted data straight into your satellite plotting function
    graph1.graph_for_collections(
        total_validated_collections=validated,
        total_expected_collections=expected,
        no_of_sats=sats,                  # <--- Passing sats to X-axis
        no_of_stations=stations, 
        time_horizon=horizon, 
        no_of_regions=regions             # <--- Passing fixed regions to the text box
    )


def plot_from_json_for_regions(json_filepath):
    # 1. Open the file and load the dictionary back into Python
    with open(json_filepath, 'r') as file:
        imported_data = json.load(file)

    # 2. Extract the data lists
    results = imported_data["results"]
    acc1 = results["accuracies_algo1"]
    acc2 = results["accuracies_algo2"]
    regions = results["regions_list"]
    validated = results["validated_collections"]
    expected = results["expected_collections"]

    # 3. Extract the metadata
    meta = imported_data["metadata"]
    stations = meta["no_of_stations"]
    horizon = meta["time_horizon"]
    sats = meta["satsOnly"]

    # 4. Pass the extracted data straight into your plotting function
    print(f"Plotting data from {json_filepath}...")
    graph2.graph(
        total_accuracies1=acc1, 
        total_accuracies2=acc2, 
        regionsOnlyList=regions,  # Make sure graph1.graph is expecting regions here!
        no_of_stations=stations, 
        time_horizon=horizon, 
        satsOnly=sats
    )

def plot_from_json_for_regions_by_collections(json_filepath):
    # 1. Open the file and load the dictionary back into Python
    with open(json_filepath, 'r') as file:
        imported_data = json.load(file)

    # 2. Extract the data lists
    results = imported_data["results"]
    acc1 = results["accuracies_algo1"]
    acc2 = results["accuracies_algo2"]
    regions = results["regions_list"]
    validated = results["validated_collections"]
    expected = results["expected_collections"]

    # 3. Extract the metadata
    meta = imported_data["metadata"]
    stations = meta["no_of_stations"]
    horizon = meta["time_horizon"]
    sats = meta["satsOnly"]

    # 4. Pass the extracted data straight into your plotting function
    print(f"Plotting data from {json_filepath}...")
    graph2.graph_for_collections(
        total_validated_collections=validated,
        total_expected_collections=expected,
        regionsOnlyList=regions,  # Make sure graph1.graph is expecting regions here!
        no_of_stations=stations, 
        time_horizon=horizon, 
        satsOnly=sats
    )

def plot_from_json_for_stations(json_filepath):
    # 1. Open the file and load the dictionary back into Python
    with open(json_filepath, 'r') as file:
        imported_data = json.load(file)

    # 2. Extract the data lists
    results = imported_data["results"]
    acc1 = results["accuracies_algo1"]
    acc2 = results["accuracies_algo2"]
    stations = results["stations_list"]
    validated = results["validated_collections"]
    expected = results["expected_collections"]

    # 3. Extract the metadata
    meta = imported_data["metadata"]
    horizon = meta["time_horizon"]
    sats = meta["satsOnly"]
    regions = meta["regionsOnly"]  # <--- Extracting fixed regions for the text box

    # 4. Pass the extracted data straight into your plotting function
    print(f"Plotting data from {json_filepath}...")
    graph3.graph(
        total_accuracies1=acc1, 
        total_accuracies2=acc2, 
        stationsOnlyList=stations,  # Make sure graph1.graph is expecting stations here!
        regionsOnly=regions,
        time_horizon=horizon, 
        satsOnly=sats,
    )

def plot_from_json_for_stations_by_collections(json_filepath):
    # 1. Open the file and load the dictionary back into Python
    with open(json_filepath, 'r') as file:
        imported_data = json.load(file)

    # 2. Extract the data lists
    results = imported_data["results"]
    acc1 = results["accuracies_algo1"]
    acc2 = results["accuracies_algo2"]
    stations = results["stations_list"]
    validated = results["validated_collections"]
    expected = results["expected_collections"]

    # 3. Extract the metadata
    meta = imported_data["metadata"]
    horizon = meta["time_horizon"]
    sats = meta["satsOnly"]
    regions = meta["regionsOnly"]  # <--- Extracting fixed regions for the text box

    # 4. Pass the extracted data straight into your plotting function
    print(f"Plotting data from {json_filepath}...")
    graph3.graph_for_collections(
        total_validated_collections=validated, 
        total_expected_collections=expected,
        stationsOnlyList=stations,  # Make sure graph1.graph is expecting stations here!
        regionsOnly=regions,
        time_horizon=horizon, 
        satsOnly=sats,
    )

if __name__ == "__main__":
    # Call 1.1
    plot_from_json_for_satellites('experiment_satellites_vs_accuracy.json')

    # Call 1.2
    # plot_from_json_for_satellites_by_collections('experiment_satellites_vs_accuracy.json')

    # # Call 2.1
    # plot_from_json_for_regions('experiment_regions_vs_accuracy.json')

    # # Call 2.2
    # plot_from_json_for_regions_by_collections('experiment_regions_vs_accuracy.json')

    # # Call 3.1
    # plot_from_json_for_stations('experiment_stations_vs_accuracy.json')

    # # Call 3.2
    # plot_from_json_for_stations_by_collections('experiment_stations_vs_accuracy.json')