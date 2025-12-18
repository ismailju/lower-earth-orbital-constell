import pandas as pd
import re

def process_satellite_data(file_path):
    """
    Reads satellite data and converts IDs to integer indices.
    CRITICAL CHANGE: Time is mapped directly to relative seconds (0, 1, 2...)
    instead of compressed indices. This ensures alignment with the physical solver.
    """
    # 1. Load Data
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Could not find file: {file_path}")

    # 2. Process Time (UTC -> Relative Integer Seconds)
    # Ensure UTC handling is active
    df['time'] = pd.to_datetime(df['time'], utc=True)
    t0 = df['time'].iloc[0]
    
    # Calculate seconds from start
    df['rel_time'] = (df['time'] - t0).dt.total_seconds().round().astype(int)
    
    # 3. GENERATE MAPPINGS
    
    # A. Satellites (0..m)
    df['sat_code'], unique_sats = pd.factorize(df['sat_name'])
    
    # B. Targets (Areas) & Stations (Grounds)
    raw_targets = set()
    raw_stations = set()
    number_pattern = re.compile(r'(\d+)$')
    
    for row in df.itertuples(index=False):
        target_str = str(row.subRegion).strip()
        match = number_pattern.search(target_str)
        if match:
            raw_id = int(match.group(1))
            if target_str.startswith('A'):
                raw_targets.add(raw_id)
            elif target_str.startswith('G'):
                raw_stations.add(raw_id)
    
    sorted_targets = sorted(list(raw_targets))
    sorted_stations = sorted(list(raw_stations))
    
    area_map = {raw: i for i, raw in enumerate(sorted_targets)}
    station_map = {raw: i for i, raw in enumerate(sorted_stations)}

    # C. Times (Identity Map)
    # OLD WRONG WAY: Compressed 0,1,2...
    # NEW CORRECT WAY: Identity 0, 10, 25...
    # We still keep a map for metadata, but the index IS the time.
    unique_times = sorted(df['rel_time'].unique())
    time_map = {t: t for t in unique_times} 

    # 4. POPULATE DICTIONARIES
    col = {} 
    com = {}
    
    for row in df.itertuples(index=False):
        # 1. Map Time (Directly use the second)
        t_idx = int(row.rel_time)
        
        # 2. Map Satellite
        sat_idx = row.sat_code
        
        # 3. Get Value
        val = float(row.angle_g_param)
        
        # 4. Map Target/Station
        target_str = str(row.subRegion).strip()
        match = number_pattern.search(target_str)
        
        if match:
            raw_id = int(match.group(1))
            
            if target_str.startswith('A'):
                if raw_id in area_map:
                    a_idx = area_map[raw_id]
                    col[(t_idx, sat_idx, a_idx)] = val
                
            elif target_str.startswith('G'):
                if raw_id in station_map:
                    g_idx = station_map[raw_id]
                    com[(t_idx, sat_idx, g_idx)] = val

    # 5. PACK METADATA
    # p is now the Maximum Time Index + 1, so range(p) covers the last event
    max_time_idx = max(unique_times) if unique_times else 0
    
    dims = {
        'p': max_time_idx + 1,      # Horizon covers up to the last event found
        'm': len(unique_sats),      # Total Satellites
        'n': len(sorted_targets),   # Total Areas
        'o': len(sorted_stations),  # Total Stations
        'time_map': time_map,       # Useful for debugging
        'unique_sats': unique_sats  # Needed for Shadow Integration
    }
    
    return col, com, dims

# --- MAIN CHECK BLOCK ---
if __name__ == "__main__":
    csv_file = "src/utility/input_data.csv"
    print(f"--- Processing {csv_file} ---")
    
    try:
        col_data, com_data, dimensions = process_satellite_data(csv_file)
        
        print("\n[Dimensions Generated]")
        print(f"Horizon (p):    {dimensions['p']} seconds")
        print(f"Satellites (m): {dimensions['m']}")
        print(f"Areas (n):      {dimensions['n']}")
        
        print("\n" + "="*40)
        print(" SAMPLE 'col' OBSERVATIONS")
        print(" Key: (Time_Sec, Sat_Idx, Area_Idx)")
        print("="*40)
        
        count = 0
        for k in sorted(col_data.keys()):
            print(f" {k} : {col_data[k]}")
            count += 1
            if count > 5: break
            
    except Exception as e:
        print(f"\n[Error] Failed to process: {e}")