import pandas as pd
import os

# number of folders (change as needed)
N = 4

for i in range(1, N+1):
    path = f"./src/data/data_{i}/input_data.csv"

    if os.path.exists(path):
        df = pd.read_csv(path)

        # remove duplicates based on all columns
        df = df.drop_duplicates()

        # overwrite the same file
        df.to_csv(path, index=False)

        print(f"Processed: {path}")
    else:
        print(f"File not found: {path}")