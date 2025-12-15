import pandas as pd
import re

def process_satellite_data(file_path):
    # 1. Load Data
    df = pd.read_csv(file_path)
    
    # 2. Process Time (UTC -> Relative Integer Seconds)
    # Convert string timestamps to datetime objects
    df['time'] = pd.to_datetime(df['time'])
    
    # Set t0 to the time of the VERY FIRST row in the file
    t0 = df['time'].iloc[0]
    
    # Calculate difference in seconds, round to nearest int
    df['rel_time'] = (df['time'] - t0).dt.total_seconds().round().astype(int)
    
    # 3. Process Satellite IDs (String Name -> Unique Numeric Code)
    # Using factorize to create a unique ID for each unique string
    df['sat_code'], unique_sats = pd.factorize(df['sat_name'])

    # 4. Initialize Dictionaries
    col = {} # For subRegions (Starts with A)
    com = {} # For Ground Stations (Starts with G)
    s = {}   # For Shadow Status
    
    # Regex to find the number at the end of the string (e.g., '32' from 'A--32')
    number_pattern = re.compile(r'(\d+)$')

    # 5. Iterate and Populate
    for row in df.itertuples(index=False):
        t = row.rel_time
        sat = row.sat_code
        
        # Handle Target (subRegion column)
        # We strip whitespace just in case
        target = str(row.subRegion).strip()
        
        # Handle Shaded Status (String "TRUE"/"FALSE" -> Integer 1/0)
        # If the CSV has actual booleans, this handles it. If strings, it handles that too.
        raw_shaded = str(row.shaded).upper()
        if raw_shaded == 'TRUE':
            is_shaded = 1
        elif raw_shaded == 'FALSE':
            is_shaded = 0
        else:
            is_shaded = int(row.shaded) # Fallback for 0/1 inputs
        
        # Populate 's' dictionary: {(Time, Sat) : Status}
        s[(t, sat)] = is_shaded
        
        # Extract ID and Populate 'col' or 'com'
        match = number_pattern.search(target)
        if match:
            target_id = int(match.group(1))
            
            # Classification Logic
            if target.startswith('A'):
                col[(t, sat, target_id)] = 1
            elif target.startswith('G'):
                com[(t, sat, target_id)] = 1

    return col, com, s