#With processing capability and battery constraint

import timeit
import pulp as plp
import pandas as pd
from pulp.constants import LpMaximize



#A: Set of Areas
#B: Set of Ground stations
#S: Set of satellites
#H: Horizon (set of time instants [0, ..., (p-1)])
#up: uplink capacity of the satellites
#mem: Memory capacity of the satellites
#down: downlink capacity of the satellites
#col: Set of all collection opportunities
#com: Set of all communication opportunities
#theta: minimum battery capacity for each satellite
#p: Horizon
#pt: Processing time for one data unit
#C: Battery capacity of each satellite (dictionary [0, .., q])
#c: charge unit/time
#d: discharege unit/time
#e: discharge on collection unit/time
#f: discharge on communication unit/time
#g: discharge on computation unit/time 
#s: (t,j) if 1 then satellite is in shadow otherwise in light
def ILP_LAS3(H, S, A, B, C, mem, up, down, col, com, theta, p, pt, c, d, e, f, g, s,beta,s_mapped,shadow):
	prob = plp.LpProblem('LEO_K', plp.LpMaximize)
	
	
	###################################### VARIABLES ###########################################
	#Denotes that data from Ai is collected by satellite Sj at time instant t
	x = plp.LpVariable.dicts("x", [(t,i,j) for t in H for i in A for j in S], cat = "Binary")
	#Denotes that at time instant t,  Sj starts processing data collected from sub-region Ai
	z = plp.LpVariable.dicts("z", [(t,i,j) for t in H for i in A for j in S], cat = "Binary")
	#Denotes that data from Ai collected by Sj is downloaded at GS Bk at time instant t
	y = plp.LpVariable.dicts("y", [(t,i,j,k) for t in H for i in A for j in S for k in B], cat = 'Binary')






	###################################### CONSTRAINTS ###########################################
	#Remove the invalid collection and communication opportunities
	for t in H:
		for i in A:
			for j in S:
				if (t,j,i) not in col:
					prob += x[t,i,j] == 0		#To remove the variables that are not collection opportunities
				else:
					prob += z[t,i,j] == 0		#If there is a collection opportunity, it can be processed starting from at least next instant
				
				for k in B:
					if (t,j,k) not in com:
						prob += y[t,i,j,k] == 0 #Invalid communication opportunities
					if t==0:
						prob += y[t,i,j,k] == 0
				
				if t == 0:						#Communication/Computation cannot occur at time instant 0
					prob += z[t,i,j] == 0
					

				if t > (p-pt):
					prob += z[t,i,j] == 0

						
	
	#Each satellite collects at most one area in an instant
	for j in S:
		for t in H:
			prob += plp.lpSum(x[t,i,j] for i in A) <= 1
	
	
	#Each area is collected at-most once
	for i in A:
		prob += plp.lpSum(x[t,i,j] for t in H for j in S) <= 1

	
	#Memory bound
	for j in S:
		for t in H:
			downloaded = plp.lpSum(y[t1,i,j,k] for k in B for i in A for t1 in range(0,t+1)) 
			processed = plp.lpSum(z[t1,i,j] for t1 in range(0,t-pt+1) for i in A)
			prob += plp.lpSum(x[t1,i,j] for i in A for t1 in range(0,t+1)) - (downloaded + processed) <= mem[j]
			
			
	#Downlink capacity of ground stations
	for t in H:
		for k in B:
			prob += plp.lpSum(y[t,i,j,k] for i in A for j in S) <= down[k]
	
	
	#Uplink capacity of satellites
	for j in S:
		for t in H:
			prob += plp.lpSum(y[t,i,j,k] for i in A for k in B) <= up[j]
	

	#Process all collected data
	for (t,j,i) in col:
		prob += x[t,i,j] - ( plp.lpSum(y[t1,i,j,k] for t1 in range(t+1,p) for k in B) + plp.lpSum(z[t1,i,j] for t1 in  range(t+1,p)) ) == 0


	#Sequential processing
	for j in S:
		for t in range(1,p-pt+1):
			prob += plp.lpSum(z[t1,i,j] for i in A for t1 in range(t, min(t+pt, p))) <= 1

	
	#Download validation
	for i in A:
		for j in S:
			for t in range(1,p):
				prob += plp.lpSum(y[t,i,j,k] for k in B) <= plp.lpSum(x[t1,i,j] for t1 in range(0, t))

	
	#Processing validation
	for i in A:
		for j in S:
			for t in range(1,p-pt):
				prob += z[t,i,j] <= plp.lpSum(x[t1,i,j] for t1 in range(0, t))
	

	#Battery constraint

	##Battery constraint on underflow
	"""
	for j in S:
		for t in H:
			prob += C[j] - ( (e * plp.lpSum(x[t1,i,j] for i in A for t1 in range(0,t+1))) + (f * plp.lpSum(y[t1,i,j,k] for i in A for k in B for t1 in range(0,t+1))) + (g * plp.lpSum(z[t1,i,j] for i in A for t1 in range(0,t+1))) + (d * plp.lpSum(s[t1,j] for t1 in range(0,t+1))) ) + (c * plp.lpSum((1 - s[t1,j]) for t1 in range(0,t+1))) >= theta[j]
	"""
	# for j in S:
	# 	for t in H:
	# 		prob += C[j] - ( (e * plp.lpSum(x[t1,i,j] for i in A for t1 in range(0,t+1))) + (f * plp.lpSum(y[t1,i,j,k] for i in A for k in B for t1 in range(0,t+1))) + (pt * g * plp.lpSum(z[t1,i,j] for i in A for t1 in range(0,t+1))) + (d * (t+1)) ) + (c * plp.lpSum((1 - s[t1,j]) for t1 in range(0,t+1))) >= theta[j]

	##Battery constraint on overflow
	# 1. Create a master dictionary to hold all the data
	telemetry_tracker = {}

	for j in S:
		for t in H:
			current_battery = C[j] - ( (e * plp.lpSum(x[t1,i,j] for i in A for t1 in range(0,t+1))) + (f * plp.lpSum(y[t1,i,j,k] for i in A for k in B for t1 in range(0,t+1))) + (pt * g * plp.lpSum(z[t1,i,j] for i in A for t1 in range(0,t+1))) + (d * (t+1)) ) + (c * plp.lpSum((1 - s[t1,j]) for t1 in range(0,t+1)))
			in_shadow = s_mapped.get((t,j), 0)
			current_theta = 0
			if in_shadow == 1:
				for every_shadow in shadow[j]:
					if every_shadow[0] <= t <= every_shadow[1]:
						current_theta = (every_shadow[1] - t) * d
						break
					
			# print(f"Satellite {j}, Time {t}: Current Theta = {current_theta}, Theta = {theta[j]}")

			# --- THE FIX: Save all three values into the tracker ---
			telemetry_tracker[(t, j)] = {
            'battery_expr': current_battery, # This is a PuLP expression (unsolved)
            'theta': current_theta,          # This is a standard float/int
            'beta': beta[j]                  # This is a standard float/int
        	}
			prob += current_battery >= current_theta, f"Bat_Min_S{j}_T{t}"
			prob += current_battery <= beta[j], f"Bat_Max_S{j}_T{t}"


	#Objective function
	prob.setObjective(plp.lpSum(x[t,i,j] for t in H for i in A for j in S))
	
	status = prob.solve(plp.PULP_CBC_CMD(msg = False))
	print("STATUS: ", status)
	
	# Check if it actually found a valid schedule
	if plp.LpStatus[prob.status] == 'Optimal':
		print("\n--- Extracting Telemetry Data ---")
		
		# Let's say you want to look specifically at Satellite 0
		target_sat = 1
		
		sat_times = []
		sat_batteries = []
		sat_thetas = []
		sat_betas = []
		
		for t in H:
			# 1. Get the dictionary for this exact time and satellite
			data = telemetry_tracker[(t, target_sat)]
			
			# 2. Evaluate the battery expression to get the final float number
			final_battery = plp.value(data['battery_expr'])
			
			# 3. Grab the saved theta and beta (they are already numbers)
			final_theta = data['theta']
			final_beta = data['beta']
			
			# 4. Save to our lists (useful for plotting later!)
			sat_times.append(t)
			sat_batteries.append(final_battery)
			sat_thetas.append(final_theta)
			sat_betas.append(final_beta)
			
			# 5. Print to the terminal
			print(f"Time {t:03d} | Bat: {final_battery:>6.2f} | Theta: {final_theta:>5.2f} | Beta: {final_beta}")

	if status == 1:
		#print("COLLECTIONS DONE: ", prob.objective)
		print("COLLECTIONS DONE: ")
		for t in H:
			for j in S:
				for i in A:
					if x[t,i,j].value() == 1:
						print(t, ": ", j, " - ", i)

		print("ON SATELLITE PROCESSING DONE: ")
		for t in H:
			for j in S:
				for i in A:
					if z[t,i,j].value() == 1:
						print(t, ": ", j, " - ", i)
						
		#print("COMMUNICATIONS DONE: ", prob.objective)
		print("COMMUNICATIONS DONE: ")
		for t in H:
			for k in B:
				for j in S:
					for i in A:
						if y[t,i,j,k].value() == 1:
							print(t, ": ", j, " " , i, " -> ", k)
	
		"""
		MEM = {}
		print("MEMORY USAGE BY ILP: ")
		for j in S:
			first = 0
			for t in H:
				count_data = 0
				for i in A:
					if x[t,i,j].value() == 1:
						count_data += 1
				print("S", j, ", t", t, ": ", count_data, " unit collected")
				if count_data > 0:
					if t > 0:
						MEM[t,j] = MEM[t-1,j] + count_data
					else:
						MEM[t,j] = count_data
				else: 
					if t > 0:
						MEM[t,j] = MEM[t-1,j]				
		max_mem_used = 0	
		print("\n\nNUMBER OF DATA UNITS IN MEMORY TILL TIME INSTANT t (ignoring the downloads): <Sj, tk: collects till tk - downloads till tk - processed till tk> ")
		for j in S:
			for t in H:
				downloaded = 0
				processed = 0
				for k in B:
					for i in A:
						for t1 in range(1,t+1):
							if y[t1,i,j,k].value() == 1.0:
								downloaded += 1
				
				for t1 in range(0,t):
					for i in A:
						if z[t1,i,j].value() == 1.0:
							if (t - t1) >= pt:
								processed += 1
				
				print("S", j, ", t", t,": ", MEM[t,j], "-", downloaded, "-", processed)		
				if max_mem_used < (MEM[t,j] - downloaded - processed):
					max_mem_used = MEM[t,j] - downloaded - processed		
		print("MAXIMUM MEMORY USED: ", max_mem_used)
		"""			
							
	#return status, prob.objective, exc_ilp, mem_ilp
	# print("Objective =", plp.value(prob.objective))
	return status, plp.value(prob.objective), [x,y,z]