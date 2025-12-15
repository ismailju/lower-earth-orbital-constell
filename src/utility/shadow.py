






import pandas as pd
from skyfield.api import load, EarthSatellite
from datetime import timedelta

ts = load.timescale()
eph = load('de421.bsp')

# df = pd.read_csv('src/utility/example_data.csv')

# t0 = ts.utc(2025, 11, 28, 9, 11, 54)
# Set Start Time to TODAY (UTC)
t0 = ts.utc(2025, 12, 15, 12, 0, 0) # Example: 12:00 UTC today

# for row in df[["sat_name", "TLE_Line1", "TLE_Line2"]].itertuples(index=True, name=None):
# idx, sat_name, TLE_Line1, TLE_Line2 = row

# sat_name = "CALSPHERE 1"
# CORRECT TLE (Preserving strictly fixed spacing)
sat_name = "ISS (ZARYA)"
# Note: Fixed-width spacing is critical!
TLE_Line1 = "1 25544U 98067A   25348.86277765  .00007299  00000-0  13766-3 0  9993"
TLE_Line2 = "2 25544  51.6306 131.9662 0003207 249.8734 110.1909 15.49595360543189"
states = []
sat = EarthSatellite(TLE_Line1, TLE_Line2, sat_name, ts)
for sec in range(0,7201):
  print(f"Processing satellite {sat_name}, second {sec}/5400", end="\r")
  t_cur = t0 + (sec/86400.0)
  sunlit = sat.at(t_cur).is_sunlit(eph)
  states.append((sec, sunlit))
  # states = [
  # (0, True),
  # (1, True),
  # (2, False),
  # (3, False),
  # ...
  # ]
light_ranges = []
shadow_ranges = []

start = states[0][0]
prev_state = states[0][1]

for sec, curr_state in states[1:]:
  if curr_state != prev_state:
    # range ended at previous second
    end = sec - 1

    if prev_state:   # True → light
      light_ranges.append((start, end))
    else:            # False → shadow
      shadow_ranges.append((start, end))

    start = sec
    prev_state = curr_state

# close the last range
end = states[-1][0]
if prev_state:
  light_ranges.append((start, end))
else:
  shadow_ranges.append((start, end))

print(f"Light ranges: {light_ranges}")
print(f"Shadow ranges: {shadow_ranges}")
# # Store the results back into the DataFrame
# df.at[idx, "light_ranges"] = str(light_ranges)
# df.at[idx, "shadow_ranges"] = str(shadow_ranges)

# # Save the updated DataFrame to a new CSV file
# df.to_csv("src/utility/example_data_with_light_shadow.csv", index=False)
