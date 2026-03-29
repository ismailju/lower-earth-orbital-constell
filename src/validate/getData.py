# def get_mission_data():
#     # col,com,proc = result
#     # --- Satellite 0 ---
#     # Collections: Single area per timestamp
#     sat0_col = {
#         0: 9, 1: 17, 2: 28, 11: 38, 17: 39, 23: 16, 
#         29: 11, 31: 18, 32: 8, 40: 27, 43: 14
#     }
#     # Communications: Note T=27, 40, 44 have multiple areas -> List
#     sat0_com = {
#         11: [28], 13: [38], 23: [39], 26: [9], 
#         27: [16, 17], 
#         40: [8, 18], 
#         42: [27], 
#         44: [11, 14]
#     }
#     # Processing: None for Sat 0
#     sat0_proc = {}

#     # --- Satellite 1 ---
#     sat1_col = {
#         1: 26, 11: 40, 12: 12, 18: 5, 
#         35: 30, 41: 34, 44: 13, 50: 3
#     }
#     sat1_com = {
#         13: [26, 40], 
#         38: [12, 30], 
#         56: [3, 34]
#     }
#     sat1_proc = {
#         47: 5, 59: 13
#     }

#     # --- Satellite 2 ---
#     sat2_col = {
#         1: 41, 2: 0, 12: 23, 22: 21, 
#         33: 6, 35: 1, 39: 32, 49: 19, 50: 37
#     }
#     sat2_com = {
#         4: [0], 20: [23], 
#         35: [6, 41], 
#         46: [1, 32], 
#         48: [21], 
#         55: [19, 37]
#     }
#     sat2_proc = {}

#     # --- Satellite 3 ---
#     sat3_col = {
#         5: 10, 9: 29, 12: 35, 26: 4, 37: 25
#     }
#     sat3_com = {
#         9: [10], 
#         17: [29, 35], 
#         49: [4, 25]
#     }
#     sat3_proc = {}

#     # --- Satellite 4 ---
#     sat4_col = {
#         20: 20, 27: 15, 32: 24, 50: 33
#     }
#     sat4_com = {
#         46: [20, 24], 
#         54: [15, 33]
#     }
#     sat4_proc = {}

#     # --- Grouping into Lists by Satellite ID ---
#     col_list = [sat0_col, sat1_col, sat2_col, sat3_col, sat4_col]
#     com_list = [sat0_com, sat1_com, sat2_com, sat3_com, sat4_com]
#     proc_list = [sat0_proc, sat1_proc, sat2_proc, sat3_proc, sat4_proc]

#     return col_list, com_list, proc_list

# # --- Verification / Usage ---
# if __name__ == "__main__":
#     cols, coms, procs = get_mission_data()
    
#     print("--- Generated Dictionary Lists ---")
#     for i in range(5):
#         print(f"\nSatellite {i}:")
#         print(f"  Col: {cols[i]}")
#         print(f"  Com: {coms[i]}")
#         print(f"  Proc: {procs[i]}")





def extract_schedule_list(variable_dict):
    from collections import defaultdict
    """
    Transforms PuLP variable dict into a list of {Time: [List of Areas]} dicts.
    
    Changes from previous version:
    1. Handles keys with length 3 (t,i,j) OR length 4 (t,i,j,k).
    2. Stores values as LISTS to handle duplicates at the same timestamp.
    """
    
    # --- Step 1: Determine List Size ---
    max_sat_id = -1
    
    # for key in variable_dict.keys():
    #     # Key structure: index 2 is always Satellite (j), regardless of tuple length
    #     j = key[2] 
        
    #     # Handle "Sat1" vs 1
    #     current_id = int(j.replace("Sat", "")) if isinstance(j, str) else int(j)
    #     if current_id > max_sat_id:
    #         max_sat_id = current_id
            
    # Initialize list of empty dictionaries
    # schedule_list = [{} for _ in range(max_sat_id + 1)]

    temp_data = defaultdict(lambda: defaultdict(list))
    # --- Step 2: Populate Data ---
    for key, var in variable_dict.items():
        # Robust Unpacking:
        # We explicitly grab the first 3 elements. 
        # This works for (t, i, j) AND (t, i, j, k).
        t = key[0]
        i = key[1]
        j = key[2]

        # Normalize Satellite ID
        sat_idx = int(j.replace("Sat", "")) if isinstance(j, str) else int(j)
        if sat_idx > max_sat_id:
            max_sat_id = sat_idx
        # Check if variable is active
        if var.varValue and var.varValue > 0.5:
            
            # Initialize the list for this time 't' if it doesn't exist yet
            # if t not in temp_data[sat_idx]:
            #     temp_data[sat_idx][t] = []
            
            # Append the value (Area/ID) to the list
            temp_data[sat_idx][t].append(i)

    # --- Step 3: Sort ---
    final_list = []
    for sat_idx in range(max_sat_id + 1):
        # Get the schedule for this ID (or empty dict if missing)
        schedule = temp_data.get(sat_idx, {})
        # 1. Sort the dictionary by Time (Key)
        sorted_keys = sorted(schedule.keys())
        sorted_schedule = {}
        
        for t in sorted_keys:
            # 2. Also sort the list of values for deterministic output
            #    e.g. {20: [15, 10]} becomes {20: [10, 15]}
            sorted_schedule[t] = sorted(schedule[t])
            
        final_list.append(sorted_schedule)

    return final_list

def process_mission_data(result):
    """
    Takes a tuple of (x, y, z) variables, processes them individually 
    using extract_schedule_list, and returns the three schedule lists.
    """
    # 1. Unpack the raw variables
    x_var, y_var, z_var = result

    # 2. Call the extraction function for each type
    col_list = extract_schedule_list(x_var)
    com_list = extract_schedule_list(y_var)
    proc_list = extract_schedule_list(z_var)
    # 3. Return the processed lists
    return col_list, com_list, proc_list

import pandas as pd
import ast

def parse_shadow_ranges(csv_file_path):
    """
    Parses 'shadow_ranges' column from a CSV using Pandas.
    Returns a list of lists of lists: [[[31, 60]], [[0, 15], [46, 60]]]
    """
    # 1. Read ONLY the shadow_ranges column (efficient)
    df = pd.read_csv(csv_file_path, usecols=['shadow_ranges'])
    
    # 2. Parse strings and convert tuples to lists in one go
    #    We use a list comprehension because it is generally faster than df.apply() 
    #    for Python object manipulation (ast.literal_eval).
    '''
    shadow_list = [
        [list(interval) for interval in ast.literal_eval(row)] 
        for row in df['shadow_ranges']
    ]
    '''
    shadow_list = []
    for row in df['shadow_ranges']:
        parsed = ast.literal_eval(row)
        
        # Safety check: If data is triple-nested (e.g., [[[0, 15], [46, 60]]]), grab the inner list
        if len(parsed) > 0 and isinstance(parsed[0], list) and isinstance(parsed[0][0], list):
            parsed = parsed[0]
            
        shadow_list.append([list(interval) for interval in parsed])
    print(f"\n[Shadow Parsing] Parsed {shadow_list} shadow entries from CSV.")
    return shadow_list

# # --- Verification / Usage ---
# if __name__ == "__main__":
#     cols, coms, procs = process_mission_data(None)
    
#     print("--- Generated Dictionary Lists ---")
#     for i in range(5):
#         print(f"\nSatellite {i}:")
#         print(f"  Col: {cols[i]}")
#         print(f"  Com: {coms[i]}")
#         print(f"  Proc: {procs[i]}")
