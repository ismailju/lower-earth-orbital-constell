import pandas as pd
import re

def process_satellite_data(file_path):
    # 1. Load Data
    df = pd.read_csv(file_path)
    
    # 2. Process Time (UTC -> Relative Integer Seconds)
    # Ensure UTC handling is active (handles 'Z' correctly)
    df['time'] = pd.to_datetime(df['time'], utc=True)
    
    # Set t0 to the time of the VERY FIRST row in the file
    t0 = df['time'].iloc[0]
    
    # Calculate difference in seconds
    df['rel_time'] = (df['time'] - t0).dt.total_seconds().round().astype(int)
    
    # 3. Process Satellite IDs
    df['sat_code'], unique_sats = pd.factorize(df['sat_name'])
    # unique_sats now holds the mapping from code to satellite name
    # Index(['Sat-A', 'Sat-B', 'Sat-C'], dtype='object')

    # This means:
    # 0 -> 'Sat-A'
    # 1 -> 'Sat-B'
    # 2 -> 'Sat-C'
    # 4. Initialize Dictionaries
    col = {} # (t, sat, area_id) : Stores 'angle_g_param' (e.g. 0.25)
    com = {} # (t, sat, station_id) : Stores 'angle_g_param' (e.g. 1.0)
    
    number_pattern = re.compile(r'(\d+)$')

    # 5. Iterate and Populate
    # pandas names tuple fields based on column headers. 
    # 'angle_g_param' and 'subRegion' must match your CSV headers exactly.
    for row in df.itertuples(index=False):
        t = row.rel_time
        sat = row.sat_code
        
        # Read the Value (Angle or Param)
        # Using the new column name provided
        param_val = float(row.angle_g_param)
        
        # Read the Target (subRegion)
        target = str(row.subRegion).strip()
        
        # Extract ID
        match = number_pattern.search(target)
        if match:
            target_id = int(match.group(1))
            
            # Classification Logic
            if target.startswith('A'):
                # Assign the parameter value (e.g., 0.25)
                col[(t, sat, target_id)] = param_val
                
            elif target.startswith('G'):
                # Assign the parameter value (e.g., 1.0)
                com[(t, sat, target_id)] = param_val

    return col, com, unique_sats

if __name__ == "__main__":
    # 1. Define the path to your CSV file
    # Make sure this file exists in the same folder!
    csv_file = "input_data.csv" 
    
    # 2. Call your function
    try:
        col_data, com_data, sats = process_satellite_data(csv_file)
        
        # 3. Print the results to verify
        print("--- Processing Successful ---")
        print(f"Unique Satellites Found: {sats}")
        print(f"Number of Observation Opportunities (col): {len(col_data)}")
        print(f"Number of Downlink Opportunities (com): {len(com_data)}")
        
        # Optional: Print first few items to check values
        print("\nSample 'col' data (first 2):")
        print(list(col_data.items())[:2])
        
        print("\nSample 'com' data (first 2):")
        print(list(com_data.items())[:2])

    except FileNotFoundError:
        print(f"Error: Could not find file '{csv_file}'. Please check the name.")
    except Exception as e:
        print(f"An error occurred: {e}")