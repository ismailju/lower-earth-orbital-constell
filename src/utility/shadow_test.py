import pandas as pd
import numpy as np
import ast
from os import path
from skyfield.api import load, EarthSatellite

# --- PART A: CSV GENERATOR (Stays the same) ---
def generate_shadow_csv(input_tle_csv, output_csv, t0_str, duration_seconds):
    """
    Reads TLEs, calculates Light/Shadow ranges using Skyfield, 
    and saves them to 'output_csv'.
    """
    # 1. Load Data
    if not path.exists(input_tle_csv):
        print(f"[Error] TLE file {input_tle_csv} not found.")
        return

    df = pd.read_csv(input_tle_csv)

    # 2. Setup Skyfield
    print("Loading Ephemeris data (downloading if missing)...")
    ts = load.timescale()
    eph = load('de421.bsp')
    
    # Parse Start Time
    try:
        t_start = pd.to_datetime(t0_str, utc=True)
    except Exception as e:
        print(f"[Error] Invalid date format: {e}")
        return
    
    # Create Time Vector
    seconds = np.arange(duration_seconds + 1)
    times = ts.utc(t_start.year, t_start.month, t_start.day, 
                   t_start.hour, t_start.minute, t_start.second + seconds)

    # 3. Calculate Shadows
    print(f"Calculating shadows for {len(df)} satellites over {duration_seconds}s...")
    print(f"Start Time: {t_start}")
    
    light_list = []
    shadow_list = []

    for row in df.itertuples():
        # Create Satellite Object
        try:
            sat = EarthSatellite(row.TLE_Line1, row.TLE_Line2, row.sat_name, ts)
        except AttributeError:
            print("[Error] CSV missing columns. Needs: 'sat_name', 'TLE_Line1', 'TLE_Line2'")
            return
        
        # Calculate Sunlit Boolean Array
        sunlit = sat.at(times).is_sunlit(eph)
        
        # --- Convert Boolean Array to Ranges ---
        l_ranges = []
        s_ranges = []
        states = sunlit.astype(int)
        
        current_state = states[0]
        start_idx = 0
        
        for i in range(1, len(states)):
            if states[i] != current_state:
                rng = (start_idx, i-1)
                if current_state == 1:
                    l_ranges.append(rng)
                else:
                    s_ranges.append(rng)
                current_state = states[i]
                start_idx = i
        
        rng = (start_idx, len(states)-1)
        if current_state == 1:
            l_ranges.append(rng)
        else:
            s_ranges.append(rng)

        light_list.append(str(l_ranges))
        shadow_list.append(str(s_ranges))

    # 4. Save to CSV
    output_df = df.copy()
    output_df['light_ranges'] = light_list
    output_df['shadow_ranges'] = shadow_list
    
    output_df.to_csv(output_csv, index=False)
    print(f"[Success] Shadow Data saved to: {output_csv}")


# --- PART B: THE SOLVER INTERFACE (FIXED FOR DENSE LOGIC) ---
def get_shadow_s_mapped(csv_path, dims_dict):
    """
    Reads the Shadow CSV and maps it to the solver's integer indices.
    Returns a DENSE dictionary s_mapped where every (t, s) exists.
    """
    
    # Unpack Dimensions
    p = dims_dict['p']                
    time_map = dims_dict['time_map']  
    unique_sats = dims_dict['unique_sats'] 
    
    inv_time_map = {v: k for k, v in time_map.items()}
    m = len(unique_sats)

    # --- 1. PRE-FILL DENSE DICTIONARY ---
    # This is the Critical Fix. 
    # We create a dictionary with 0 (Sun) for EVERY satellite at EVERY time step.
    # This ensures s[t,j] never raises a KeyError in the solver.
    print(f"Initializing dense shadow map ({p} x {m})...")
    s_mapped = {(t, s): 0 for t in range(p) for s in range(m)}
    
    if not path.exists(csv_path):
        print(f"[Warning] Shadow CSV not found. Returning all-sun map.")
        return s_mapped
        
    df = pd.read_csv(csv_path)
    
    # --- 2. LOAD SHADOW INTERVALS ---
    shadow_lookup = {}
    for row in df.itertuples():
        try:
            ranges = ast.literal_eval(row.shadow_ranges)
        except:
            ranges = []
        shadow_lookup[row.sat_name] = ranges
        
    # --- 3. OVERWRITE SHADOWS ---
    print(f"Mapping Shadow Data...")

    # We iterate only the solver time steps
    for t_idx in range(p):
        real_time = inv_time_map.get(t_idx, -1)
        
        if real_time == -1: continue

        for s_idx in range(m):
            sat_name = unique_sats[s_idx]
            
            # If this satellite has shadow data
            if sat_name in shadow_lookup:
                # Check if current real_time is in any shadow range
                for (start, end) in shadow_lookup[sat_name]:
                    if start <= real_time <= end:
                        # Mark as Shadow (1)
                        # This overwrites the default 0
                        s_mapped[(t_idx, s_idx)] = 1
                        break
            
    print(f"[Info] Shadow mapping complete. Dictionary size: {len(s_mapped)}")
    return s_mapped


# --- MAIN EXECUTION BLOCK ---
if __name__ == "__main__":
    print("--- RUNNING SHADOW MODULE TEST ---")
    
    # 1. CONFIGURATION
    INPUT_FILE = "src/utility/repaired_data.csv"
    OUTPUT_FILE = "src/utility/example_data_with_shadow_light_1.csv"
    START_TIME = "2025-11-28 09:11:54"
    DURATION = 7200 

    # --- TEST PART A ---
    generate_shadow_csv(INPUT_FILE, OUTPUT_FILE, START_TIME, DURATION)

    # --- TEST PART B ---
    if path.exists(OUTPUT_FILE):
        df_check = pd.read_csv(OUTPUT_FILE)
        mock_sats = df_check['sat_name'].tolist()
        mock_dims = {
            'p': DURATION + 1,
            'time_map': {t: t for t in range(DURATION + 1)},
            'unique_sats': mock_sats
        }
        
        result_map = get_shadow_s_mapped(OUTPUT_FILE, mock_dims)
        
        # Verify it is truly DENSE
        expected_size = (DURATION + 1) * len(mock_sats)
        print(f" -> Map Size: {len(result_map)} (Expected: {expected_size})")
        
        if len(result_map) == expected_size:
            print(" -> VERIFIED: Dictionary is fully dense.")
        else:
            print(" -> FAILED: Dictionary is missing keys.")