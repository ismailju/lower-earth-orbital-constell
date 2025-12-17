import pandas as pd

def repair_tle_line1(line):
    # Split by whitespace to get the raw data chunks
    parts = line.split()
    
    # Safety check: Line 1 should have roughly 9 parts
    if len(parts) < 9: return line
    
    # Reconstruct with strict spacing rules
    # 1: Line Number
    # 2: SatID + Classification (6 chars)
    # 3: Int. Designator (8 chars, padded left with spaces?) -> Actually padded RIGHT in most raw, but let's align.
    #    Standard: Cols 10-17.
    # 4: Epoch (14 chars)
    # 5: First Deriv (10 chars)
    # 6: Second Deriv (8 chars)
    # 7: BSTAR (8 chars)
    # 8: Ephemeris (1 char)
    # 9: Element Set + Checksum
    
    # Standard SGP4 Format String:
    # "1 NNNNNU NNNNNN   YYDDD.DDDDDDDD  .NNNNNNNN  NNNNN-N  NNNNN-N N NNNN"
    
    # Extract
    line_num = parts[0]
    sat_id_class = parts[1] # "00900U"
    int_des = parts[2]      # "64063C"
    epoch = parts[3]        # "25330.13720199"
    d1 = parts[4]           # ".00000861"
    d2 = parts[5]           # "00000+0"
    bstar = parts[6]        # "87064-3"
    eph = parts[7]          # "0"
    el_set_check = parts[8] # "9995"
    
    # REPAIR:
    # {int_des:<8} ensures the designator is 8 chars long (adds spaces to the right)
    fixed = f"1 {sat_id_class} {int_des:<8} {epoch:>14} {d1:>10} {d2:>8} {bstar:>8} {eph} {el_set_check:>4}"
    
    # Note: This is a "Best Effort" repair. 
    # Valid TLE requires checksum recalculation if we change spaces, 
    # but Skyfield usually ignores checksums if strict=False.
    return fixed

def repair_tle_line2(line):
    parts = line.split()
    if len(parts) < 8: return line
    
    # 1: Line Num
    # 2: SatID (5 chars)
    # 3: Inclination (8 chars)
    # 4: RAAN (8 chars)
    # 5: Eccentricity (7 chars)
    # 6: Arg Perigee (8 chars)
    # 7: Mean Anom (8 chars)
    # 8: Mean Motion + Rev + Checksum
    
    sat_id = parts[1]
    inc = parts[2]
    raan = parts[3]
    ecc = parts[4]
    argp = parts[5]
    ma = parts[6]
    
    # The last part is tricky because Rev number might be attached to Mean Motion or Checksum
    # Let's join the rest and formatting assumes standard lengths
    rest = " ".join(parts[7:]) 
    
    # REPAIR:
    # {inc:>8} adds spaces to the LEFT to make it 8 chars long
    fixed = f"2 {sat_id:5} {inc:>8} {raan:>8} {ecc} {argp:>8} {ma:>8} {rest:>16}"
    
    return fixed

# --- MAIN EXECUTION ---
input_csv = "src/utility/example_data.csv" # Your bad file
output_csv = "src/utility/repaired_data.csv" # The new good file

df = pd.read_csv(input_csv)

print("Repairing TLEs...")
df['TLE_Line1'] = df['TLE_Line1'].apply(repair_tle_line1)
df['TLE_Line2'] = df['TLE_Line2'].apply(repair_tle_line2)

df.to_csv(output_csv, index=False)
print(f"Fixed CSV saved to: {output_csv}")
print("Use this new file for Skyfield/Gurobi!")