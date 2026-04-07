import pandas as pd
import random
import re
from collections import defaultdict

# -----------------------------
# Configuration
# -----------------------------
# Change this variable to 1, 2, 3, etc., to control how many NEW ground stations are generated
NUM_NEW_GROUND_STATIONS = 2 

# Load CSV
df = pd.read_csv("input_data.csv")

# -----------------------------
# Step 1: Filter ground data only
# -----------------------------
# We now focus entirely on ground stations (angle_g_param == 1)
ground_df = df[df["angle_g_param"] == 1]
satellites = ground_df["sat_name"].unique().tolist()

# -----------------------------
# Step 2: Count distribution (ONLY satellites for ground stations)
# -----------------------------
count_map = defaultdict(int)

for name in ground_df["sat_name"]:
    count_map[name] += 1

# -----------------------------
# Step 3: Generate new ground stations
# -----------------------------
# Assuming ground station names are stored in the same 'subRegion' column
ground_stations = ground_df["subRegion"].unique().tolist()

def split_name(name):
    # Splits strings like "GS-1" into "GS-" and 1
    match = re.match(r"([A-Za-z\-]+)(\d+)", str(name))
    if match:
        return match.group(1), int(match.group(2))
    return str(name), 0

prefix_max = {}

for g in ground_stations:
    prefix, num = split_name(g)
    prefix_max[prefix] = max(prefix_max.get(prefix, 0), num)

new_grounds = []
prefixes = list(prefix_max.keys())

# Fallback just in case there are no ground stations in the original file
if not prefixes:
    prefixes = ["GS-"]
    prefix_max["GS-"] = 0

# Generate exactly the number of ground stations specified by the variable
for _ in range(NUM_NEW_GROUND_STATIONS):
    prefix = random.choice(prefixes)
    prefix_max[prefix] += 1
    new_grounds.append(f"{prefix}{prefix_max[prefix]}")

print(f"Generated {NUM_NEW_GROUND_STATIONS} New Ground Stations:", new_grounds)

# -----------------------------
# Helper: balanced satellite
# -----------------------------
def get_balanced_satellite():
    min_count = min(count_map.values())
    candidates = [k for k, v in count_map.items() if v == min_count]
    return random.choice(candidates)

# -----------------------------
# Step 4: Process full dataset
# -----------------------------
new_rows = []
i = 0
n = len(df)

while i < n:
    row = df.iloc[i].to_dict()
    new_rows.append(row)

    # Only consider insertion AFTER ground station rows
    if row["angle_g_param"] == 1:
        gap = random.randint(10, 20)

        if i % gap == 0:
            # Insert 1 to 3 new ground station contact opportunities
            for _ in range(random.randint(1, 3)):
                sat = get_balanced_satellite()

                new_row = {
                    "time": row["time"],  # preserve order
                    "sat_name": sat,
                    "subRegion": random.choice(new_grounds), # Assign one of the new ground stations
                    "angle_g_param": 1    # ONLY ground type
                }

                new_rows.append(new_row)

                # update balance
                count_map[sat] += 1

    i += 1

# -----------------------------
# Step 5: Save
# -----------------------------
new_df = pd.DataFrame(new_rows)
new_df.to_csv("output_data.csv", index=False)

print(f"✅ Done! {NUM_NEW_GROUND_STATIONS} new Ground Stations added correctly without touching region data.")
