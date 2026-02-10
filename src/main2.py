from os import path
from ILP_LAS import ILP_LAS
from inputs import inputs
from shadow_example import shadow_example
from validation import validation

def set_start_time_str():
    start_time_str = "2026-01-05 11:38:53"
    return start_time_str

def get_parameters1(dims):
    p, n, m, o = dims['p'], dims['n'], dims['m'], dims['o']
    H, S, A, B = list(range(p)), list(range(m)), list(range(n)), list(range(o))
    return p, n, m, o, H, S, A, B

def set_physical_parameters2(S,B):
    mem = {j: 3 for j in S}
    up = {j: 2 for j in S}
    down = {k: 2 for k in B}
    C = {j: 80 for j in S}
    beta = {j: 100 for j in S}
    theta = {j: 3 for j in S}
    return mem, up, down, C, beta, theta
    
def set_discharge_rate_parameters3():
    c_solar = 0.4
    d_idle = 0.3
    e_col = 0.25
    f_com = 0.4
    g_proc = 0.25
    return c_solar, d_idle, e_col, f_com, g_proc

def set_processing_time_pt():
    pt_proc_time = 1
    return pt_proc_time

######## ----------------------------------------------------------- ########
######## ----------------------------------------------------------- ######## 
        ####   MAIN FUNCTION CALLS EVERY OTHERS STEP BY STEP ####
def helper(fileId):
    print("--- INITIALIZING SCRIPT (CBC/Gurobi) ---")
    base_dir = path.dirname(path.abspath(__file__))
#############################################################################
    #### Call input() ####
    main_input_csv = path.join(base_dir, 'data', f'data_{fileId}', 'input_data.csv')
    col,com,dims = inputs(main_input_csv)

#############################################################################
    #### Call shadow_example() ####
    input_csv = path.join(base_dir, 'data', f'data_{fileId}', 'example_data.csv')
    shadow_out_csv = path.join(base_dir, 'data', f'data_{fileId}', 'example_data_with_shadow_light.csv')
    tle_repaired_csv = path.join(base_dir, 'data', f'data_{fileId}', 'repaired_data.csv')

    start_time_str = set_start_time_str()
    s_mapped= shadow_example(dims,start_time_str,input_csv,tle_repaired_csv,shadow_out_csv)

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
    
    status, obj_val,result = ILP_LAS(
        H, S, A, B,
        C, mem, up, down,
        col, com,
        theta,
        p, pt_proc_time,
        c_solar, d_idle, e_col, f_com, g_proc,
        s_mapped,
        beta
    )
    ##########################################################
#############################################################################
    #### Validation ####
    validation(result,shadow_out_csv)
    # print("--- Generated Dictionary Lists for Validating ---")
    # for i in range(5):
    #     print(f"\nSatellite {i}:")
    #     print(f"  Col: {cols[i]}")
    #     print(f"  Com: {coms[i]}")
    #     print(f"  Proc: {procs[i]}")

################################################################
    #########################################################

    
    # --- RESULTS ---
    # PuLP Status Code 1 = Optimal
    if status == 1:
        print(f"\n--- OPTIMAL SOLUTION FOUND (Obj: {obj_val}) ---")
    else:
        print(f"\n[Result] Optimization Failed/Infeasible. Status Code: {status}")

def main():
    # for fileId in range (2):
    #     helper(fileId)
    helper(1)

if __name__ == "__main__":
    main()