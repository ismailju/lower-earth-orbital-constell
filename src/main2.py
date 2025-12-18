# from os import path
# import gurobipy as gp # Keep if you use GRB constants, though PuLP uses 1 for Optimal

# # --- IMPORTS ---
# from ILP_LAS import ILP_LAS 
# from utility.d import process_satellite_data
# # Note: Ensure your dense shadow code is saved as 'utility/shadow_test.py'
# from utility.shadow_test import generate_shadow_csv, get_shadow_s_mapped

# def main():
#     print("--- INITIALIZING DRIVER SCRIPT ---")

#     # --- CONFIGURATION ---
#     base_dir = path.dirname(path.abspath(__file__))
    
#     main_input_csv = path.join(base_dir, 'utility', 'input_data.csv')
#     tle_input_csv  = path.join(base_dir, 'utility', 'repaired_data.csv')
#     shadow_out_csv = path.join(base_dir, 'utility', 'example_data_with_shadow_light_1.csv') 
    
#     # Start Time
#     start_time_str = "2025-11-28 09:11:54" 

#     # --- STEP 1: LOAD MAIN DATA FIRST ---
#     print(f"\n[Step 1] Processing Main Inputs from {path.basename(main_input_csv)}...")
#     col, com, dims = process_satellite_data(main_input_csv)
    
#     # Dynamic Duration
#     duration_sec = dims['p'] 
#     print(f" -> Dynamic Duration Set: {duration_sec} seconds")

#     # --- STEP 2: GENERATE SHADOW DATA ---
#     print(f"\n[Step 2] Generating Shadow Data...")
#     generate_shadow_csv(tle_input_csv, shadow_out_csv, start_time_str, duration_sec)
    
#     # --- STEP 3: MAP SHADOWS TO SOLVER INDICES ---
#     print(f"\n[Step 3] Mapping Shadows to Solver Indices...")
#     # This must return the DENSE dictionary (0s and 1s) to work with your ILP
#     s_mapped = get_shadow_s_mapped(shadow_out_csv, dims)

#     # --- STEP 4: DEFINE SETS & PARAMETERS ---
#     p = dims['p'] 
#     n = dims['n'] 
#     m = dims['m'] 
#     o = dims['o'] 

#     H = list(range(p))
#     S = list(range(m))
#     A = list(range(n))
#     B = list(range(o))
    
#     print(f"\n[Setup] Problem Size: {p} Time Steps, {m} Sats, {n} Areas, {o} Stations")

#     # Physics Parameters
#     mem = {j: 3 for j in S}
#     up = {j: 2 for j in S}
#     down = {k: 2 for k in B}
    
#     C = {j: 5.65 for j in S}
#     beta = {j: 20 for j in S}
#     theta = {j: 3 for j in S}
    
#     # Costs
#     c_solar = 0.4
#     d_idle = 0.3
#     e_col = 0.2
#     f_com = 0.2
#     g_proc = 0.0
#     pt_proc_time = 1

#     # --- STEP 5: RUN SOLVER ---
#     print(f"\n[Step 5] Launching Optimization...")
    
#     # Capture the TUPLE return values (status, obj, _, _)
#     status, obj_val, _, _ = ILP_LAS(
#         H, S, A, B,
#         C, mem, up, down,
#         col, com,
#         theta,
#         p, pt_proc_time,
#         c_solar, d_idle, e_col, f_com, g_proc,
#         s_mapped,
#         beta
#     )
    
#     # --- CHECK RESULTS ---
#     # PuLP Status: 1 = Optimal
#     if status == 1:
#         print(f"\n--- OPTIMAL SOLUTION FOUND (Obj: {obj_val}) ---")
#         print("Detailed variable assignments were printed above by ILP_LAS.")
#     else:
#         print(f"\n[Result] Optimization Ended with Status Code: {status}")

# if __name__ == "__main__":
#     main()

from os import path

# --- IMPORTS ---
from ILP_LAS import ILP_LAS 
from utility.d import process_satellite_data
from utility.shadow_test import generate_shadow_csv, get_shadow_s_mapped

def main():
    print("--- INITIALIZING DRIVER SCRIPT (CBC) ---")

    # --- CONFIGURATION ---
    base_dir = path.dirname(path.abspath(__file__))
    
    main_input_csv = path.join(base_dir, 'utility', 'input_data.csv')
    tle_input_csv  = path.join(base_dir, 'utility', 'repaired_data.csv')
    shadow_out_csv = path.join(base_dir, 'utility', 'example_data_with_shadow_light_1.csv') 
    
    start_time_str = "2025-11-28 19:58:24" 

    # --- STEP 1: LOAD MAIN DATA ---
    print(f"\n[Step 1] Processing Main Inputs...")
    col, com, dims = process_satellite_data(main_input_csv)
    duration_sec = dims['p'] 
    print(f" -> Duration: {duration_sec} seconds")

    # --- STEP 2: GENERATE SHADOWS ---
    print(f"\n[Step 2] Generating Shadow Data...")
    generate_shadow_csv(tle_input_csv, shadow_out_csv, start_time_str, duration_sec)
    
    # --- STEP 3: MAP SHADOWS ---
    print(f"\n[Step 3] Mapping Shadows...")
    s_mapped = get_shadow_s_mapped(shadow_out_csv, dims)

    # --- STEP 4: PARAMETERS ---
    p, n, m, o = dims['p'], dims['n'], dims['m'], dims['o']

    H, S, A, B = list(range(p)), list(range(m)), list(range(n)), list(range(o))
    
    print(f"\n[Setup] Problem: {p} Steps, {m} Sats, {n} Areas, {o} Stations")

    mem = {j: 3 for j in S}
    up = {j: 2 for j in S}
    down = {k: 2 for k in B}
    C = {j: 100 for j in S}
    beta = {j: 250 for j in S}
    theta = {j: 3 for j in S}
    
    c_solar, d_idle, e_col, f_com, g_proc = 0.4, 0.3, 0.2, 0.2, 0.0
    pt_proc_time = 1

    # --- STEP 5: SOLVE ---
    print(f"\n[Step 5] Launching Optimization...")
    
    status, obj_val, _, _ = ILP_LAS(
        H, S, A, B,
        C, mem, up, down,
        col, com,
        theta,
        p, pt_proc_time,
        c_solar, d_idle, e_col, f_com, g_proc,
        s_mapped,
        beta
    )
    
    # --- RESULTS ---
    # PuLP Status Code 1 = Optimal
    if status == 1:
        print(f"\n--- OPTIMAL SOLUTION FOUND (Obj: {obj_val}) ---")
    else:
        print(f"\n[Result] Optimization Failed/Infeasible. Status Code: {status}")

if __name__ == "__main__":
    main()