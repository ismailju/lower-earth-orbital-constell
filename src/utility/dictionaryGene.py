import pandas as pd
import re

def process_satellite_data(file_path):
    # Load the csv file
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print("File not found.")
        return None, None

    collection = {}
    communication = {}

    for index, row in df.iterrows():
        # OPTIONAL: Round time to nearest integer and convert to int for cleaner keys
        # If you prefer the exact float value, use: time_val = row['time']
        time_val = int(round(row['time']))
        
        satcode_val = row['satcode']
        region_str = str(row['region_or_station']).strip()
        
        # Regex to find the number at the end
        match = re.search(r'(\d+)$', region_str)
        
        if match:
            region_id = int(match.group(1))
            key_tuple = (time_val, satcode_val, region_id)
            
            if region_str.startswith('A'):
                collection[key_tuple] = 0.25
            elif region_str.startswith('G'):
                communication[key_tuple] = 1

    return collection, communication

# --- Example Run ---
# collection, communication = process_satellite_data('time_sat_reg_1.csv')