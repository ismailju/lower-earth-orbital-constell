from os import path
from ILP_LAS import ILP_LAS
from inputs import inputs
from shadow_example import shadow_example
from validation import validation

def set_start_time_str():
    start_time_str = "2026-02-24 07:32:37"
    return start_time_str

def get_parameters1(dims):
    p, n, m, o = dims['p'], dims['n'], dims['m'], dims['o']
    H, S, A, B = list(range(p)), list(range(m)), list(range(n)), list(range(o))
    return p, n, m, o, H, S, A, B

def set_physical_parameters2(S,B):
    mem = {j: 3 for j in S}
    up = {j: 2 for j in S}
    down = {k: 2 for k in B}
    C = {j: 45 for j in S}
    beta = {j: 80 for j in S}
    theta = {j: 3 for j in S}
    return mem, up, down, C, beta, theta
    
def set_discharge_rate_parameters3():
    c_solar = 0.4
    d_idle = 0.3
    e_col = 0.25
    f_com = 0.25
    g_proc = 0.4
    return c_solar, d_idle, e_col, f_com, g_proc

def set_processing_time_pt():
    pt_proc_time = 1
    return pt_proc_time

######## ----------------------------------------------------------- ########
######## ----------------------------------------------------------- ######## 
        ####   MAIN FUNCTION CALLS EVERY OTHERS STEP BY STEP ####
def helper(fileId,batch_size):
    print("--- INITIALIZING SCRIPT (CBC/Gurobi) ---")
    base_dir = path.dirname(path.abspath(__file__))
#############################################################################
    #### Call input() ####
    main_input_csv = path.join(base_dir, 'data', f'data_{fileId}', 'input_data.csv')
    col,com,dims = inputs(main_input_csv,batch_size)

#############################################################################
    #### Call shadow_example() ####
    input_csv = path.join(base_dir, 'data', f'data_{fileId}', 'example_data.csv')
    shadow_out_csv = path.join(base_dir, 'data', f'data_{fileId}', 'example_data_with_shadow_light.csv')
    tle_repaired_csv = path.join(base_dir, 'data', f'data_{fileId}', 'repaired_data.csv')

    start_time_str = set_start_time_str()
    s_mapped= shadow_example(dims,start_time_str,input_csv,tle_repaired_csv,shadow_out_csv,batch_size)
    print(f"\n[Shadow Mapping] Mapped {len(s_mapped)} shadow entries for optimization.")

############################################################################# 
    # print(f"Col: {col}")
    # print(f"Com: {com}")
    # print (f" -> Shadow Mapping Complete.")
    # print(s_mapped)

    #### --- STEP 4: PARAMETERS --- ####
    p, n, m, o, H, S, A, B = get_parameters1(dims)
    # print(f"\n[Setup] Problem: {p} Steps, {m} Sats, {n} Areas, {o} Stations")
    mem, up, down, C, beta, theta = set_physical_parameters2(S,B)

    c_solar, d_idle, e_col, f_com, g_proc = set_discharge_rate_parameters3()
    pt_proc_time = set_processing_time_pt()

#############################################################################
    #### --- STEP 5: SOLVE --- ####
    print(f"\n[Step 5] Launching Optimization...")

    ########################---------------------#########################

    from ILP_LAS2 import ILP_LAS2
    status, obj_val,result = ILP_LAS2(
        H, S, A, B,
        C, mem, up, down,
        col, com,
        theta,
        p, pt_proc_time,
        c_solar, d_idle, e_col, f_com, g_proc,
        s_mapped,
        beta
    )

    ########################---------------------#########################
    ########################---------------------#########################

    # from validate.getData import parse_shadow_ranges
    # shadow_list = parse_shadow_ranges(shadow_out_csv)
    # from ILP_LAS3 import ILP_LAS3
    # status, obj_val,result = ILP_LAS3(
    #     H, S, A, B,
    #     C, mem, up, down,
    #     col, com,
    #     theta,
    #     p, pt_proc_time,
    #     c_solar, d_idle, e_col, f_com, g_proc,
    #     s_mapped,
    #     beta,
    #     s_mapped,
    #     shadow_list
    # )
    ########################---------------------#########################

    ##########################################################
#############################################################################
    #### Validation ####
    print(f"\n {len(H)} | Horizon: {H} \n {len(S)} | Satellites: {S} \n {len(A)} | Areas: {A} \n {len(B)} | Stations: {B}\n\n")
    total_accuracy, total_validated_collection, total_expected_collection = validation(result,shadow_out_csv,H,C,beta,d_idle,c_solar,e_col,f_com,g_proc)
    # print("--- Generated Dictionary Lists for Validating ---")
    # for i in range(5):
    #     print(f"\nSatellite {i}:")
    #     print(f"  Col: {cols[i]}")
    #     print(f"  Com: {coms[i]}")
    #     print(f"  Proc: {procs[i]}")
    
################################################################
    #########################################################
    '''
    print(dims)
    '''
    # --- RESULTS ---
    # PuLP Status Code 1 = Optimal
    if status == 1:
        print(f"\n--- OPTIMAL SOLUTION FOUND (Obj: {obj_val}) ---")
    else:
        print(f"\n[Result] Optimization Failed/Infeasible. Status Code: {status}")
    
    return total_accuracy,len(S),len(A),len(B),total_validated_collection,total_expected_collection

def main():
    batch_size = 7

    accuracies1 = []
    validated_collections = []
    accuracies2 = []
    expected_collections = []
    no_of_sats = []
    no_of_regions = []
    no_of_stations = []
    for fileId in range (0,1):
        individual_accuracy,no_of_sat,no_of_region,no_of_station,t_val_coll,t_exp_coll = helper(fileId,batch_size)
        accuracies1.append(100)
        validated_collections.append(t_val_coll)
        accuracies2.append(individual_accuracy)
        expected_collections.append(t_exp_coll)
        no_of_sats.append(no_of_sat)
        no_of_regions.append(no_of_region)
        no_of_stations.append(no_of_station)

        
        # 1.3 Stations Package everything into a clean Python dictionary
        export_data = {
            "metadata": {
                "regionsOnly": 118,
                "time_horizon": 63,
                "satsOnly": 5  # Or however many satellites this specific run used
            },
            "results": {
                "accuracies_algo1": accuracies1,
                "accuracies_algo2": accuracies2,
                "stations_list": no_of_stations,
                "validated_collections": validated_collections,
                "expected_collections": expected_collections
            }
        }
        # 2.3 Save it to a JSON file
        import json
        filename = 'experiment_stations_vs_accuracy.json'
        with open(filename, 'w') as file:
            # indent=4 formats the file beautifully so you can read it like a text file
            json.dump(export_data, file, indent=4)       
        print(f"Data successfully saved to {filename}")



    # # 1.1 Satellites Package the data (Regions is now static, Sats are dynamic)
    # export_data = {
    #     "metadata": {
    #         "no_of_stations": 6,
    #         "time_horizon": 63,
    #         "no_of_regions": 18  # Fixed for this specific experiment
    #     },
    #     "results": {
    #         "accuracies_algo1": accuracies1,
    #         "accuracies_algo2": accuracies2,
    #         "sats_list": no_of_sats,
    #         "validated_collections": validated_collections,
    #         "expected_collections": expected_collections
    #     }
    # }

    # # 1.2 Regions Package everything into a clean Python dictionary
    # export_data = {
    #     "metadata": {
    #         "no_of_stations": 6,
    #         "time_horizon": 63,
    #         "satsOnly": 5  # Or however many satellites this specific run used
    #     },
    #     "results": {
    #         "accuracies_algo1": accuracies1,
    #         "accuracies_algo2": accuracies2,
    #         "regions_list": no_of_regions,
    #         "validated_collections": validated_collections,
    #         "expected_collections": expected_collections
    #     }
    # }

    # 1.3 Stations Package everything into a clean Python dictionary
    export_data = {
        "metadata": {
            "regionsOnly": 118,
            "time_horizon": 63,
            "satsOnly": 5  # Or however many satellites this specific run used
        },
        "results": {
            "accuracies_algo1": accuracies1,
            "accuracies_algo2": accuracies2,
            "stations_list": no_of_stations,
            "validated_collections": validated_collections,
            "expected_collections": expected_collections
        }
    }

    # # 2.1 Save it to a JSON file
    # import json
    # filename = 'experiment_satellites_vs_accuracy.json'
    # with open(filename, 'w') as file:
    #     json.dump(export_data, file, indent=4)         
    # print(f"Satellite Data successfully saved to {filename}")

    # # 2.2 Save it to a JSON file
    # import json
    # filename = 'experiment_regions_vs_accuracy.json'
    # with open(filename, 'w') as file:
    #     # indent=4 formats the file beautifully so you can read it like a text file
    #     json.dump(export_data, file, indent=4)       
    # print(f"Data successfully saved to {filename}")

    # 2.3 Save it to a JSON file
    import json
    filename = 'experiment_stations_vs_accuracy.json'
    with open(filename, 'w') as file:
        # indent=4 formats the file beautifully so you can read it like a text file
        json.dump(export_data, file, indent=4)       
    print(f"Data successfully saved to {filename}")

    # # Call graphing function
    # # import graph_plot.graph as graph
    # import graph_plot.graph1 as graph1
    # # graph.graph(accuracies1, accuracies2, no_of_sats, no_of_stations=6, time_horizon=63, no_of_regions=18)
    # graph1.graph(accuracies1, accuracies2, no_of_regions, no_of_stations=6, time_horizon=63, satsOnly=5)
    
    # fId = 8
    # individual_accuracy = helper(fId,batch_size)
    # print(f"\n Individual Accuracy for fileId {fId}: {individual_accuracy:.2f}%")


if __name__ == "__main__":
    main()