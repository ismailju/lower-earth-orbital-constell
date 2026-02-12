import pulp as plp
import pandas as pd

def ILP_LAS(H, S, A, B, C, mem, up, down, col, com, theta, p, pt, c, d, e, f, g, s_mapped, beta):
    print("--- SOLVER INITIALIZED (CBC) ---")
    
    # 1. Initialize Problem
    prob = plp.LpProblem('LEO_K', plp.LpMaximize)

    # 2. Define Variables (Sparse Dictionaries)
    # Collection
    x = plp.LpVariable.dicts("x", [(t, i, j) for (t, j, i) in col], cat="Binary")
    
    # Processing (only if time allows)
    z = plp.LpVariable.dicts("z", [(t, i, j) for (t, j, i) in col if t <= p - pt], cat="Binary")
    
    # Communication
    y = plp.LpVariable.dicts("y", [(t, i, j, k) for (t, j, k) in com for i in A], cat="Binary")

    # --- CONSTRAINTS ---

    # 1. Single Collection per Sat
    for j in S:
        for t in H:
            prob += plp.lpSum(x[t,i,j] for (tt,i,jj) in x if tt == t and jj == j) <= 1
  
    # 2. Unique Area Collection
    for i in A:
        prob += plp.lpSum(x[t,i,j] for (t,ii,j) in x if ii == i) <= 1

    # 3. Memory Capacity
    for j in S:
        for t in H:
            collected = plp.lpSum(x[t1,i,j] for (t1,i,jj) in x if jj == j and t1 <= t)
            downloaded = plp.lpSum(y[t1,i,j,k] for (t1,i,jj,k) in y if jj == j and t1 <= t)
            processed = plp.lpSum(z[t1,i,j] for (t1,i,jj) in z if jj == j and t1 + pt <= t)
            prob += collected - downloaded - processed <= mem[j]

    # 4. Ground Station Bandwidth
    for t in H:
        for k in B:
            prob += plp.lpSum(y[t,i,j,k] for (tt,i,j,kk) in y if tt == t and kk == k) <= down[k]
  
    # 5. Satellite Uplink Bandwidth
    for j in S:
        for t in H:
            prob += plp.lpSum(y[t,i,j,k] for (tt,i,jj,k) in y if tt == t and jj == j) <= up[j]

    # 6. Flow Conservation
    for (t,j,i) in col:
        prob += (
            x[(t,i,j)]
            - plp.lpSum(y[(t1,i,j,k)] for (t1,ii,jj,k) in y if ii == i and jj == j and t1 > t)
            - plp.lpSum(z[(t1,i,j)] for (t1,ii,jj) in z if ii == i and jj == j and t1 > t)
            == 0
        )

    # 7. Sequential Processing
    for j in S:
        for t in range(1, p - pt + 1):
            prob += plp.lpSum(z[(t1,i,j)] for (t1,i,jj) in z if jj == j and t <= t1 < t + pt) <= 1
    
    # 8. Download Causality
    for (t,i,j,k) in y:
        prob += y[(t,i,j,k)] <= plp.lpSum(x[(t1,i,j)] for (t1,ii,jj) in x if ii == i and jj == j and t1 < t)

    # 9. Processing Causality
    for (t,i,j) in z:
        prob += z[(t,i,j)] <= plp.lpSum(x[(t1,i,j)] for (t1,ii,jj) in x if ii == i and jj == j and t1 < t)
            
    # 10. Battery Constraints
    #shodow needed to be inputted as list of list of pair/list
    shadow = []
    for j in S:
        for t in H:
            current_battery = (
                C[j]
                - e * plp.lpSum(x[(t1,i,j)] for (t1,i,jj) in x if jj == j and t1 <= t)
                - f * plp.lpSum(y[(t1,i,j,k)] for (t1,i,jj,k) in y if jj == j and t1 <= t)
                - pt * g * plp.lpSum(z[(t1,i,j)] for (t1,i,jj) in z if jj == j and t1 <= t)
                - d * (t + 1)
                + c * plp.lpSum((1 - s_mapped.get((t1,j), 0)) for t1 in range(0, t + 1))
            )
            in_shadow = s_mapped.get((t,j), 0)
            if in_shadow == 1:
                for every_shadow in shadow[j]:
                    if every_shadow[0] <= t <= every_shadow[1]:
                        current_theta = (every_shadow[1] - t) * d
                        break
            else: current_theta = 0
            
            prob += current_battery >= current_theta, f"Bat_Min_S{j}_T{t}"
            # prob += current_battery >= theta[j], f"Bat_Min_S{j}_T{t}"
            prob += current_battery <= beta[j], f"Bat_Max_S{j}_T{t}"
    

    # --- OBJECTIVE ---
    prob.setObjective(plp.lpSum(x.values()))
  
    # --- SOLVE (USING Gurobi) ---
    print("Launching Gurobi Solver...")
    # msg=True prints the log to your console so you see it working
    # status = prob.solve(plp.PULP_CBC_CMD(msg=True))
    # status = prob.solve(plp.PULP_CBC_CMD(msg=True, timeLimit=300, keepFiles=False))
    # Try using the direct Gurobi API first (fastest, lowest memory)
    try:
        # PRIORITY 1: Gurobi API (Fastest, In-Memory)
        print("Attempting to solve with Gurobi API...")
        status = prob.solve(plp.GUROBI(msg=True))

    except Exception as e_api:
        print(f"Gurobi API unavailable ({e_api}). Trying Gurobi CMD...")

        try:
            # PRIORITY 2: Gurobi Command Line (Slower I/O, but robust)
            status = prob.solve(plp.GUROBI_CMD(msg=True))

        except Exception as e_cmd:
            print(f"Gurobi CMD unavailable ({e_cmd}). Falling back to CBC...")

            # PRIORITY 3: CBC (Free, Open Source, comes bundled with PuLP)
            # Note: This is generally slower for large ILP problems
            status = prob.solve(plp.PULP_CBC_CMD(msg=True))
    
    print("STATUS: ", plp.LpStatus[status])

    # Print Non-Zero Variables
    # col_result = ()
    # com_result = ()
    # proc_result = ()
    if status == 1: # 1 is 'Optimal' in PuLP
        print("\n--- RESULTS ---")
        for (t,i,j), var in x.items():
            if var.value() == 1:
                print(f"COLLECT: T={t} Sat={j} Area={i}")
                # col_result[t] = i
        for (t,i,j), var in z.items():
            if var.value() == 1:
                print(f"PROCESS: T={t} Sat={j} Area={i}")
                # proc_result[t] = i
        for (t,i,j,k), var in y.items():
            if var.value() == 1:
                print(f"DOWNLNK: T={t} Sat={j} Area={i} -> Station={k}")
                # com_result.setdefault(t,[]).append(i)
    
    # print("Col Result:\n")
    # print(col_result)
    # print("Com Result\n")
    # print(com_result)
    # print("Process Result:\n")
    # print(proc_result)

    obj_val = plp.value(prob.objective)
    return status, obj_val, [x,y,z]
    # return status, obj_val, 0, 0