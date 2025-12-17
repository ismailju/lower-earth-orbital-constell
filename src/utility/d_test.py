import pandas as pd
import re

def process_satellite_data(file_path):
    """
    Reads satellite data and converts all IDs (Time, Sat, Area, Station)
    into contiguous integer indices (0, 1, 2...) suitable for ILP solvers.
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
    df['rel_time'] = (df['time'] - t0).dt.total_seconds().round().astype(int)
    
    # 3. GENERATE MAPPINGS
    
    # A. Satellites (0..m)
    # factorize gives us a clean 0..m index automatically
    df['sat_code'], unique_sats = pd.factorize(df['sat_name'])
    
    # B. Targets (Areas) & Stations (Grounds)
    # We need to find all unique IDs first to assign them 0..n and 0..o
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
    
    # Sort them so the mapping is deterministic (32 -> 0, 105 -> 1)
    sorted_targets = sorted(list(raw_targets))
    sorted_stations = sorted(list(raw_stations))
    
    area_map = {raw: i for i, raw in enumerate(sorted_targets)}
    station_map = {raw: i for i, raw in enumerate(sorted_stations)}

    # C. Times (0..p)
    # We only care about times that exist in the data (sparse to dense)
    unique_times = sorted(df['rel_time'].unique())
    time_map = {t: i for i, t in enumerate(unique_times)}

    # 4. POPULATE DICTIONARIES
    col = {} 
    com = {}
    
    for row in df.itertuples(index=False):
        # 1. Map Time
        t_idx = time_map[row.rel_time]
        
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
                # Map Raw ID (e.g., 32) -> Solver Index (e.g., 0)
                a_idx = area_map[raw_id]
                col[(t_idx, sat_idx, a_idx)] = val
                
            elif target_str.startswith('G'):
                # Map Raw ID (e.g., 18) -> Solver Index (e.g., 0)
                g_idx = station_map[raw_id]
                com[(t_idx, sat_idx, g_idx)] = val

    # 5. PACK METADATA
    dims = {
        'p': len(unique_times),     # Total Time steps
        'm': len(unique_sats),      # Total Satellites
        'n': len(sorted_targets),   # Total Areas
        'o': len(sorted_stations),  # Total Stations
        'time_map': time_map,       # NEEDED for Shadow Integration
        'unique_sats': unique_sats  # NEEDED for Shadow Integration
    }
    
    return col, com, dims

# --- MAIN CHECK BLOCK ---
if __name__ == "__main__":
    # Define file path (Make sure input_data.csv is in the same folder)
    csv_file = "src/utility/input_data.csv"
    
    print(f"--- Processing {csv_file} ---")
    
    try:
        col_data, com_data, dimensions = process_satellite_data(csv_file)
        
        print("\n[Dimensions Generated]")
        print(f"Time Steps (p): {dimensions['p']}")
        print(f"Satellites (m): {dimensions['m']}")
        print(f"Areas (n):      {dimensions['n']}")
        print(f"Stations (o):   {dimensions['o']}")
        
        print("\n" + "="*40)
        print(" FULL 'col' DICTIONARY (Observations)")
        print(" Key Format: (Time_Index, Sat_Index, Area_Index) : Value")
        print("="*40)
        # Sort by time index for easier reading
        for k in sorted(col_data.keys()):
            v = col_data[k]
            print(f" {k} : {v}")
            
        print("\n" + "="*40)
        print(" FULL 'com' DICTIONARY (Downlinks)")
        print(" Key Format: (Time_Index, Sat_Index, Station_Index) : Value")
        print("="*40)
        for k in sorted(com_data.keys()):
            v = com_data[k]
            print(f" {k} : {v}")
            
        print("\n--- End of Data ---")

    except Exception as e:
        print(f"\n[Error] Failed to process: {e}")