import pandas as pd
import numpy as np
import ast
from os import path
from skyfield.api import load, EarthSatellite

# --- PART A: CSV GENERATOR ---
def generate_shadow_csv(input_tle_csv, output_csv, t0_str, duration_seconds):
    """
    Reads TLEs, calculates Light/Shadow ranges using Skyfield, 
    and saves them to 'output_csv'.
    """
    # 1. Load Data
    if not path.exists(input_tle_csv):
        print(f"Error: TLE file {input_tle_csv} not found.")
        return

    df = pd.read_csv(input_tle_csv)

    # 2. Setup Skyfield
    ts = load.timescale()
    eph = load('de421.bsp')
    
    # Parse Start Time
    # Note: Ensure t0_str matches the format in your input_data.csv
    t_start = pd.to_datetime(t0_str, utc=True)
    t0_sf = ts.from_datetime(t_start)
    
    # Create Time Vector (0 to Duration)
    seconds = np.arange(duration_seconds + 1)
    # Build array of Skyfield Time objects
    times = ts.utc(t_start.year, t_start.month, t_start.day, 
                   t_start.hour, t_start.minute, t_start.second + seconds)

    # 3. Calculate Shadows
    print(f"Calculating shadows for {len(df)} satellites over {duration_seconds}s...")
    
    light_list = []
    shadow_list = []

    for row in df.itertuples():
        # Create Satellite Object
        sat = EarthSatellite(row.TLE_Line1, row.TLE_Line2, row.sat_name, ts)
        
        # Calculate Sunlit Boolean Array (True=Light, False=Shadow)
        sunlit = sat.at(times).is_sunlit(eph)
        
        # --- Convert Boolean Array to Ranges [(start, end), ...] ---
        l_ranges = []
        s_ranges = []
        
        # 0=Shadow, 1=Light
        states = sunlit.astype(int)
        
        # Find indices where state changes
        # diffs[i] = states[i+1] - states[i]
        #  1 means 0->1 (Shadow to Light)
        # -1 means 1->0 (Light to Shadow)
        diffs = np.diff(states, prepend=states[0]-1, append=states[-1]-1)
        
        # Identify start/end indices
        # We start a range whenever the state *becomes* that value
        # We end a range whenever the state *stops* being that value
        
        # Simple Iterative approach for robustness
        current_state = states[0]
        start_idx = 0
        
        for i in range(1, len(states)):
            if states[i] != current_state:
                # Range closed at i-1
                rng = (start_idx, i-1)
                if current_state == 1:
                    l_ranges.append(rng)
                else:
                    s_ranges.append(rng)
                
                # Start new range
                current_state = states[i]
                start_idx = i
        
        # Close the final range
        rng = (start_idx, len(states)-1)
        if current_state == 1:
            l_ranges.append(rng)
        else:
            s_ranges.append(rng)

        light_list.append(str(l_ranges))
        shadow_list.append(str(s_ranges))

    # 4. Save to CSV
    df['light_ranges'] = light_list
    df['shadow_ranges'] = shadow_list
    
    df.to_csv(output_csv, index=False)
    print(f"Shadow CSV generated: {output_csv}")


# --- PART B: THE SOLVER INTERFACE ---
def get_shadow_s_mapped(csv_path, dims_dict):
    """
    Reads the Shadow CSV and maps it to the solver's indices
    using 'dims_dict' (from d.py).
    Returns: s_mapped {(t_idx, sat_idx): 0 or 1}
    """
    
    # Unpack Dimensions
    p = dims_dict['p']                # Total Solver Time Steps
    time_map = dims_dict['time_map']  # {Raw_Rel_Time: Solver_Index}
    unique_sats = dims_dict['unique_sats'] # ['SatA', 'SatB'...]
    
    # Invert Time Map (Index -> Raw Time)
    inv_time_map = {v: k for k, v in time_map.items()}
    
    if not path.exists(csv_path):
        raise FileNotFoundError(f"Shadow CSV missing: {csv_path}")
        
    df = pd.read_csv(csv_path)
    
    # 1. Build Lookup Table: { 'SatName': [(start, end), ...] }
    shadow_lookup = {}
    for row in df.itertuples():
        try:
            # literal_eval is safer than eval
            ranges = ast.literal_eval(row.shadow_ranges)
        except:
            ranges = []
        shadow_lookup[row.sat_name] = ranges
        
    # 2. Map to Solver Indices
    s_mapped = {}
    m = len(unique_sats)
    
    # We must provide a value for every (t, s) pair in the solver grid
    for t_idx in range(p):
        # Find the REAL time (seconds) for this index
        real_time = inv_time_map[t_idx]
        
        for s_idx in range(m):
            sat_name = unique_sats[s_idx]
            
            val = 0 # Default = Light
            
            # Check Shadow
            if sat_name in shadow_lookup:
                # Is real_time inside any shadow range?
                for (start, end) in shadow_lookup[sat_name]:
                    if start <= real_time <= end:
                        val = 1 # Shadow
                        break
            
            s_mapped[(t_idx, s_idx)] = val
            
    return s_mapped