def inputs(main_input_csv):
    from os import path
    from utility.d import process_satellite_data

    # --- STEP 1: LOAD MAIN DATA --- #
    print(f"\n[Step 1] Processing Main Inputs...")
    batch_size=21
    col, com, dims = process_satellite_data(main_input_csv,batch_size)
    print(f" -> Collection Tuples:{len(col)}## {col}")
    print(f" -> Communication Tuples:{len(com)}## {com}")
    print(f" -> Dimensions: {dims}")
    duration_sec = dims['p'] 
    print(f" -> Duration: {duration_sec} seconds")

    return col, com, dims
