import numpy as np
import pandas as pd
from skyfield.api import load, EarthSatellite

# 1. Setup Skyfield
ts = load.timescale()
eph = load('de421.bsp')

# 2. Load Data
df = pd.read_csv("src/utility/repaired_data.csv")

# --- CRITICAL: MATCH THIS EXACTLY TO YOUR OTHER SCRIPT'S T0 ---
# Example: If your other script sees '2025-11-28T09:11:54Z' as Time 0
year, month, day, hour, minute, second = 2025, 11, 28, 9, 11, 54
# -------------------------------------------------------------

# Initialize new columns to avoid errors
df["light_ranges"] = None
df["shadow_ranges"] = None

# Create the relative seconds array ONCE (0 to 7200 seconds)
seconds_range = np.arange(0, 7201)

# Generate the Skyfield Time objects for this range starting from your specific T0
# Note: ts.utc allows adding seconds array directly to the 'second' argument
t_times = ts.utc(year, month, day, hour, minute, second + seconds_range)

for idx, row in df.iterrows(): # iterrows is often easier for writing back to 'idx'
    sat_name = row['sat_name']
    line1 = row['TLE_Line1']
    line2 = row['TLE_Line2']
    
    sat = EarthSatellite(line1, line2, sat_name, ts)

    # 3. CALCULATE SUNLIGHT (Vectorized)
    # Using the 't_times' we generated relative to the specific T0
    sunlit_array = sat.at(t_times).is_sunlit(eph)

    # 4. EXTRACT RANGES
    light_ranges = []
    shadow_ranges = []

    start = 0
    prev_state = sunlit_array[0] # True (Light) or False (Shadow)

    # Iterate starting from index 1
    for sec, curr_state in enumerate(sunlit_array[1:], start=1):
        if curr_state != prev_state:
            end = sec - 1
            if prev_state:
                light_ranges.append((start, end))
            else:
                shadow_ranges.append((start, end))
            
            start = sec
            prev_state = curr_state

    # Close the last range
    end = len(sunlit_array) - 1
    if prev_state:
        light_ranges.append((start, end))
    else:
        shadow_ranges.append((start, end))

    # Store as string (simplest for CSV)
    # df.at is fast for scalar assignment
    df.at[idx, "light_ranges"] = str(light_ranges)
    df.at[idx, "shadow_ranges"] = str(shadow_ranges)

# Save
output_path = "src/utility/example_data_with_light_shadow.csv"
df.to_csv(output_path, index=False)
print(f"Saved shadow data to {output_path}")