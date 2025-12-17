from ILP_LAS import ILP_LAS
import pandas as pd
from os import path
import ast # Needed to parse the string "[(0,10), (20,30)]" into a list
from utility.d import process_satellite_data

# 1. SETUP PATHS
base_dir = path.dirname(path.abspath(__file__))
csv_path = path.join(base_dir, 'utility', 'input_data.csv')

# 2. LOAD CONNECTIVITY DATA (col, com)
# Note: process_satellite_data returns (col, com, unique_sats_index)
col, com, unique_sats_index = process_satellite_data(csv_path)

# 3. LOAD SHADOW DATA (s) - MANUALLY
# We need to read the CSV again to get the 'shadow_ranges' column
df = pd.read_csv(csv_path)
s = {}

# Re-create sat_map helper from the loaded index for consistency
# unique_sats_index is the list ['SatA', 'SatB'...]
sat_name_to_code = {name: i for i, name in enumerate(unique_sats_index)}

for row in df.itertuples():
    # Convert Sat Name -> Code
    if row.sat_name not in sat_name_to_code: continue # Skip unknown sats
    s_idx = sat_name_to_code[row.sat_name]
    
    # Parse the shadow string "[(0, 100), ...]"
    try:
        ranges = ast.literal_eval(row.shadow_ranges)
    except:
        ranges = [] # Handle empty or malformed strings
        
    # Mark these times as "1" (Shadow) in 's' dictionary
    for (start, end) in ranges:
        for t in range(int(start), int(end) + 1):
            s[(t, s_idx)] = 1

# 4. EXTRACT RAW LISTS & CREATE MAPPINGS
times_raw = sorted({t for (t,_,_) in list(col.keys()) + list(com.keys())})
# Add shadow times to known times to avoid "KeyError" later
times_raw = sorted(list(set(times_raw) | {t for (t,_) in s.keys()}))

sats_raw  = sorted(list(range(len(unique_sats_index)))) # 0..m
areas_raw = sorted({a for (t,s,a) in col.keys()})
grounds_raw= sorted({g for (t,s,g) in com.keys()})

# Create Mappings
time_map = {t:i for i,t in enumerate(times_raw)}
inv_time_map = {i:t for t,i in time_map.items()}
sat_map  = {s:s for s in sats_raw} # Identity map (0->0) since we used factorize
area_map = {a:i for i,a in enumerate(areas_raw)}
ground_map= {g:i for i,g in enumerate(grounds_raw)}

# 5. REMAP DICTIONARIES TO COMPACT INDICES
col_mapped = {
    (time_map[t], sat_map[j], area_map[i]): v
    for (t, j, i), v in col.items()
}

com_mapped = {
    (time_map[t], sat_map[j], ground_map[k]): v
    for (t, j, k), v in com.items()
}

s_mapped = {}
# Fill s_mapped: Default to 0 (Light), set 1 (Shadow) if exists
for t_raw in times_raw:
    t_idx = time_map[t_raw]
    for s_idx in sats_raw:
        # Check raw 's' using raw time and sat index
        if s.get((t_raw, s_idx), 0) == 1:
            s_mapped[(t_idx, s_idx)] = 1
        else:
            s_mapped[(t_idx, s_idx)] = 0

# 6. DEFINE DIMENSIONS
n = len(areas_raw)   # Regions
m = len(sats_raw)    # Satellites
o = len(grounds_raw) # Ground Stations
p = len(times_raw)   # Time steps

H = list(range(p))
S = list(range(m))
A = list(range(n))
B = list(range(o))

# 7. GENERATE OMEGA SETS (Sparse Indices)

# omega_collection: (t, sat, area) - Directly from 'col'
omega_collection = list(col_mapped.keys())

# omega_comm: (t, sat, ground) - Directly from 'com'
omega_comm = list(com_mapped.keys())

# omega_transmit: (t, sat, area, ground)
# CRITICAL FIX: Allow transmission of ANY Area 'a' if a link exists
omega_transmit = []
for (t, sat, ground) in omega_comm:
    for area in A:
        # We can try to download ANY area 'area'
        # if the connection (t, sat, ground) exists.
        omega_transmit.append((t, sat, area, ground))

# 8. PARAMETERS (Hardcoded for now)
mem = {j: 3 for j in S}
up = {j: 2 for j in S}
down = {k: 2 for k in B}
C = {j: 5.65 for j in S}
theta = {j: 3 for j in S}
beta = {j: 20 for j in S}

c = 0.4
d = 0.3
e = 0.2
f = 0.2
g = 0
pt = 1

# 9. RUN SOLVER
print("\n--- Running ILP_LAS ---")
print(f"Time Steps: {p}, Satellites: {m}, Areas: {n}, Stations: {o}")

ILP_LAS(
    H, S, A, B,
    C, mem, up, down,
    col_mapped, com_mapped,
    theta,
    p, pt,
    c, d, e, f, g,
    s_mapped,
    beta
)