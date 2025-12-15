from skyfield.api import load, EarthSatellite

ts = load.timescale()
eph = load('de421.bsp')

# Use the TLE you are testing
line1 = "1 00900U 64063C   25330.13720199  .00000861  00000+0  87064-3 0  9995"
line2 = "2 00900  90.2213  67.0709 0026517 183.6006 248.3038 13.76334507 43499"
sat = EarthSatellite(line1, line2, "CALSPHERE 1", ts)

# Check the Middle of the window (45 mins in)
t_check = ts.utc(2025, 11, 28, 9, 11 + 45, 54) # T0 + 45 mins

print("--- DEBUGGING MIDDLE OF WINDOW ---")
print(f"Time: {t_check.utc_iso()}")
print(f"Sunlit? {sat.at(t_check).is_sunlit(eph)}")

# Check Position
geocentric = sat.at(t_check)
subpoint = geocentric.subpoint()
print(f"Sat Lat: {subpoint.latitude.degrees:.4f}")
print(f"Sat Lon: {subpoint.longitude.degrees:.4f}")
print(f"Sat Height: {subpoint.elevation.km:.2f} km")

# If this says 'True' (Sunlit) but Latitude is near the Equator (0 deg), 
# then something is wrong with the Shadow calculation (eph file).
# If Latitude is near the Pole (+/- 90), then 'Sunlit' is likely CORRECT.