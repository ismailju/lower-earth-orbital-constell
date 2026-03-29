# Finds overlapping intervals
def isOverlapping(a,b,c,d) -> bool:
  return (a<=d and b>=c)

# Finds next light region start (next shadow max)
def listOfShadowMax(shadow,H):
  '''
  print(f"\n[Shadow Analysis] Calculating shadow max intervals for H={H}...")
  print(f"Shadow Intervals: {shadow}")
  '''
  shadowMaxArray = []
  ########### ADDED SAFETY CHECKS FOR H ############
  max_H = H[-1] if isinstance(H, list) and len(H) > 0 else 0
  for pair in shadow:
    '''
    print(f"Checking shadow interval {pair} against H={H}...")
    print(f"Types: pair[0]={type(pair[0])}, pair[1]={type(pair[1])}, H={type(H)}")
    '''
    if(isOverlapping(pair[0],pair[1],0,max_H)):
      shadowMaxArray.append(pair[1])
  return shadowMaxArray

def inShadow(shadow,t):
  for pair in shadow:
    if pair[0] <= t <= pair[1] :
      return True
  return False

def validate(shadow,col,com,proc,H,Cj,Bj,d,c,discharge_rate_col,discharge_rate_com,discharge_rate_proc):
  charge = Cj
  no_of_collection = 0
  shadowMaxArray = listOfShadowMax(shadow,H)
  sizeOfList = len(shadowMaxArray)
  sMaxIteratior = 0
  Smax = shadowMaxArray[0] if sizeOfList > 0 else 0
  if sizeOfList > 0: sMaxIteratior += 1
  # Smax = H #need to calculate separately for some cases
  for t in H:
    try:
      col_discharge = discharge_rate_col if t in col else 0
      com_discharge = discharge_rate_com * len(com[t]) if t in com else 0
      proc_discharge = discharge_rate_proc if t in proc else 0
      
      charge -= d #constant discharge

      if inShadow(shadow,t): #in shadow check || need to calculate separately in a function
        if(t>Smax and sMaxIteratior<sizeOfList):
          Smax = shadowMaxArray[sMaxIteratior]
          sMaxIteratior += 1
        thetaj = d * (Smax - t) #need to calculate Smax
        if charge < thetaj : 
          break
        if(charge - col_discharge >=thetaj):
          charge -= col_discharge
          if col_discharge > 0: no_of_collection += 1
          if (charge - proc_discharge >= thetaj):
            charge -= proc_discharge
            if (charge - com_discharge >= thetaj):
              charge -= com_discharge
            elif com_discharge > 0:
              print(f"[t={t}] Shadow: Dropped Communication to save survival buffer.")
          elif proc_discharge > 0:
            print(f"[t={t}] Shadow: Dropped Processing and Comms to save survival buffer.")
        elif col_discharge > 0:
          print(f"[t={t}] Shadow: Dropped Collection to protect survival buffer.")
      else:
        net_dissip = c - d - col_discharge - com_discharge - proc_discharge
        if charge + net_dissip > 0:
          charge += net_dissip
          if ( charge > Bj ):
            charge = Bj
          if(col_discharge>0) : 
            no_of_collection += 1 #if collection takes place
        else:
          charge = charge + c - d
          if charge - col_discharge > 0:
            charge -= col_discharge
            if col_discharge > 0: no_of_collection += 1
            if charge - proc_discharge > 0:
              charge -= proc_discharge
              if charge - com_discharge > 0:
                charge -= com_discharge
              elif com_discharge > 0:
                print(f"[t={t}] Sunlight: Dropped Communication to save Collection.")
            elif proc_discharge > 0:
              print(f"[t={t}] Sunlight: Dropped Processing to save Collection.")
          elif col_discharge > 0:
            print(f"[t={t}] Sunlight: Collection failed - Insufficient energy.")
    except KeyError as e:
      print(f"[t={t}] Data Error: Missing key {e}")
      continue
    except TypeError as e:
      print(f"[t={t}] Format Error: Dictionary value at {t} is not a list. {e}")
      continue
    #end for
  accuracy = (100 * no_of_collection)/len(col) if len(col) > 0 else 0
  return [no_of_collection,len(col),accuracy]

def call_validate(col_list, com_list, proc_list,shadow_list,H,Cj,Bj,d,c,dr_col,dr_com,dr_proc):
  # from getData import process_mission_data
  # # from getData import get_mission_data
 
  # print("Loading mission data from getData.py...")
  # col_list, com_list, proc_list = process_mission_data()
  # # col_list, com_list, proc_list = get_mission_data()


  print("\n--- Starting Validation Loop ---")
  print(f"{'Sat ID':<10} | {'Scheduled':<10} | {'Collected':<18} | {'Accuracy (%)':<15}")
  print("-" * 40)

  # Scalars - Setting Cj low to trigger the "Dropped" messages
  # H = 2 

  # Cj = 80.0                 
  # Bj = 100.0       

  # c, d, dr_col, dr_com, dr_proc = 0.4, 0.3, 0.25, 0.25, 0.4

  # Extract specific data for this satellite
  # Parsed from "shadow_ranges" column
  # shadow_list = [
  #   [[0, 15], [46, 60]],      # SAT_4
  #   [[31, 60]],              # SAT_0
  #   [[0, 30]],               # SAT_1
  #   [[31, 60]],              # SAT_2
  #   [[16, 45]]              # SAT_3
  # ]
  # 4. Loop through each satellite
  # print(col_list)
  # print(com_list)
  # print(proc_list)
  for sat_id in range(len(col_list)):
    # 1. EXTRACT Shadow for THIS satellite
    # Safety check to e
    # nsure we have shadow data for this ID
    if sat_id < len(shadow_list):
      current_shadow = shadow_list[sat_id]
      '''
      print(f"\n[Satellite {sat_id}] Shadow Intervals: {current_shadow}")
      '''
    else:
      current_shadow = [] # Default to no shadow if data missing
    col = col_list[sat_id]
    com = com_list[sat_id]
    proc = proc_list[sat_id]

    ##FIXES for specific satellite##
    current_Cj = Cj[sat_id] if isinstance(Cj, dict) else Cj
    current_Bj = Bj[sat_id] if isinstance(Bj, dict) else Bj

    # Run Validation
    accuracy = validate(
        current_shadow, col, com, proc, 
        H, current_Cj, current_Bj, d, c, 
        dr_col, dr_com, dr_proc
    )

    # Print Result
    total_tasks = len(col)
    collection,total,accur = accuracy
    print(f"{sat_id:<10} | {total_tasks:<10} | {collection:<5} out of {total:<5} | {accur:<15.2f}")

  print("-" * 40)
  print("Simulation Complete.")


def main():
  from getData import process_mission_data
  # from getData import get_mission_data
 
  print("Loading mission data from getData.py...")
  col_list, com_list, proc_list = process_mission_data()
  # col_list, com_list, proc_list = get_mission_data()


  print("\n--- Starting Validation Loop ---")
  print(f"{'Sat ID':<10} | {'Scheduled':<10} | {'Accuracy (%)':<15}")
  print("-" * 40)

  # Scalars - Setting Cj low to trigger the "Dropped" messages
  H = 6

  Cj = 80                 
  Bj = 100      

  c, d, dr_col, dr_com, dr_proc = 0.4, 0.3, 0.25, 0.4, 0.25

  # Extract specific data for this satellite
  # Parsed from "shadow_ranges" column
  shadow_list = [
    [[31, 60]],              # SAT_0
    [[0, 30]],               # SAT_1
    [[31, 60]],              # SAT_2
    [[16, 45]],              # SAT_3
    [[0, 15], [46, 60]]      # SAT_4
  ]
  # 4. Loop through each satellite
  for sat_id in range(len(col_list)):
    # 1. EXTRACT Shadow for THIS satellite
    # Safety check to e
    # nsure we have shadow data for this ID
    if sat_id < len(shadow_list):
      current_shadow = shadow_list[sat_id]
    else:
      current_shadow = [] # Default to no shadow if data missing
    col = col_list[sat_id]
    com = com_list[sat_id]
    proc = proc_list[sat_id]

    # Run Validation
    accuracy = validate(
        current_shadow, col, com, proc, 
        H, Cj, Bj, d, c, 
        dr_col, dr_com, dr_proc
    )

    # Print Result
    total_tasks = len(col)
    print(f"{sat_id:<10} | {total_tasks:<10} | {accuracy:<15.2f}")

  print("-" * 40)
  print("Simulation Complete.")


# if __name__ == "__main__":
#     call_validate()