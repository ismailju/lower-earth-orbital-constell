import csv
import random
import os

input_file = os.path.join("data", "data_10", "input_data.csv")
temp_file = os.path.join("data", "data_10", "temp_input_data.csv")

# satellites you want to add
new_satellites = ["RADIO ROSTO (RS-15)"]

sat_index = 0
rows_since_insert = 0
next_insert = random.randint(7, 10)

with open(input_file, "r", newline="") as infile, open(temp_file, "w", newline="") as outfile:

    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)

    writer.writeheader()

    for row in reader:

        writer.writerow(row)
        rows_since_insert += 1

        if rows_since_insert >= next_insert:

            new_sat = new_satellites[sat_index]

            # check to avoid copying same satellite
            if row["sat_name"] != new_sat:

                new_row = row.copy()
                new_row["sat_name"] = new_sat
                writer.writerow(new_row)

                # move to next satellite
                sat_index = (sat_index + 1) % len(new_satellites)

            rows_since_insert = 0
            next_insert = random.randint(10, 20)

# os.replace(temp_file, input_file)
