import pandas as pd

# Input list of (x, y, z) tuples
data = [(10, 5, 3), (12, 7, 2), (15, 2, 9)]

# Convert to list of dictionaries for DataFrame
rows = []
for x, y, z in data:
    rows.append({
        "time": x,
        "satellite": f"S{y}",
        "ROI": f"A{z}"
    })

# Create DataFrame
df = pd.DataFrame(rows)

# Save to CSV
df.to_csv("output.csv", index=False)

print("CSV generated as output.csv")
