import numpy as np
from skyfield.api import load, EarthSatellite

ts = load.timescale()
eph = load('de421.bsp')

# 1. SETUP SATELLITE
# Note: I corrected the TLE checksum (added the missing '2' at the end of line 1)
sat_name = "CALSPHERE 4A"
# Use the exact strings you provided
TLE_Line1 = "1 01520U 65065H   25330.14823545  .00000142  00000+0  25554-3 0  99952"
TLE_Line2 = "2 01520  89.9085 124.3859 0068518 317.5441  92.2519 13.36234705935597"
sat = EarthSatellite(TLE_Line1, TLE_Line2, sat_name, ts)

# 2. CREATE TIME ARRAY (The Correct Way)
# We create an array of 5401 seconds and feed it to ts.utc all at once
seconds_range = np.arange(0, 7201)
t_times = ts.utc(2025, 12, 15, 12, 0, 0 + seconds_range)

# 3. CALCULATE SUNLIGHT (Vectorized)
# This runs instantly for all 5400 points without a loop
sunlit_array = sat.at(t_times).is_sunlit(eph)

# 4. EXTRACT RANGES
# (Your logic here was good, but applying it to the array is cleaner)
light_ranges = []
shadow_ranges = []

# Initialize state
start = 0
prev_state = sunlit_array[0] # True or False

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

print(f"Analysis for: {sat_name}")
print(f"Light ranges (seconds from start): {light_ranges}")
print(f"Shadow ranges (seconds from start): {shadow_ranges}")