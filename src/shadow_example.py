from os import path
from utility.shadow_test import generate_shadow_csv, get_shadow_s_mapped
from utility.repair_tle import repair_tle 
    

def shadow_example(dims,start_time_str,input_csv, tle_repaired_csv,shadow_out_csv,batch_size):
##################################################################################
    #### Call repair_tle() from utility.repair_tle ####
    #### Generate repaired_data.csv ####
    repair_tle(input_csv,tle_repaired_csv)

##################################################################################
    #### Call generate_shadow_csv() from utility.shadow_test ####
    #### Generate example_data_with_shadow_light_2.csv ####
    # base_dir = path.dirname(path.abspath(__file__))
    # shadow_out_csv = path.join(base_dir, 'utility', 'example_data_with_shadow_light_2.csv')
    
#################################################################################
    #### --- STEP 2: GENERATE SHADOWS --- ####
    #### Call generate_shadow
    # tle_input_csv  = path.join(base_dir, 'utility', 'repaired_data.csv')
    duration_sec = dims['p']
    # batch_size=2
    print(f"\n[Step 2] Generating Shadow Data...")
    generate_shadow_csv(tle_repaired_csv, shadow_out_csv, start_time_str, duration_sec,batch_size)
    
    
    # --- STEP 3: MAP SHADOWS ---
    print(f"\n[Step 3] Mapping Shadows...")
    s_mapped = get_shadow_s_mapped(shadow_out_csv, dims)

    return s_mapped