import pandas as pd

# Input list of (x, y, z) tuples
col =  {(0,0,0): 0.25, 
		(0,0,8): 0.75, 
		(0,1,4): -0.5,
		(1,0,1): -0.25,
		(1,1,6): -1.0,
		(2,0,3): 1.5,
		(2,1,5): 0.0, 
		(2,1,6): 0.0,
		(3,1,7): 0.0,
		(4,0,4): 0.0,
		(5,0,8): -0.25,
		(5,1,0): -0.5,
		(6,0,6): 0.5, 
		(7,1,1): 0.5,
		(7,1,2): -0.5,
		(8,0,8): -0.5}

# Convert to list of dictionaries for DataFrame
rows = []
for (x,y,z), val in col.items():
    rows.append({
        "time": x,
        "satellite": f"S{y}",
        "ROI": f"A{z}"
    })

# Create DataFrame
df = pd.DataFrame(rows)

# Save to CSV
df.to_csv("./input/output.csv", index=False)

print("CSV generated as output.csv")
