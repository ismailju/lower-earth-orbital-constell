#ILP without processing capability and battery constraint

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
#p: Horizon
def ILP(H, S, A, B, mem, up, down, col, com, p):
	prob = plp.LpProblem('LEO_K', plp.LpMaximize)
	
	
	###################################### VARIABLES ###########################################
	#Denotes that data from Ai is collected by satellite Sj at time instant t
	x = plp.LpVariable.dicts("x", [(t,i,j) for t in H for i in A for j in S], cat = "Binary")
	#Denotes that data from Ai collected by Sj is downloaded at GS Bk at time instant t
	y = plp.LpVariable.dicts("y", [(t,i,j,k) for t in H for i in A for j in S for k in B], cat = 'Binary')






	###################################### CONSTRAINTS ###########################################
	#Remove the invalid collection and communication opportunities
	for t in H:
		for i in A:
			for j in S:
				if (t,j,i) not in col:
					prob += x[t,i,j] == 0
				
				for k in B:
					if (t,j,k) not in com:
						prob += y[t,i,j,k] == 0
				

	
						
	
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
			prob += plp.lpSum(x[t1,i,j] for i in A for t1 in range(0,t+1)) - plp.lpSum(y[t1,i,j,k] for k in B for i in A for t1 in range(0,t+1)) <= mem[j]
			
			
	#Downlink capacity of ground stations
	for t in H:
		for k in B:
			prob += plp.lpSum(y[t,i,j,k] for i in A for j in S) <= down[k]
	
	
	#Uplink capacity of satellites
	for j in S:
		for t in H:
			prob += plp.lpSum(y[t,i,j,k] for i in A for k in B) <= up[j]
	

	#Transfer all collected data
	for i in A:
		for j in S:
			prob += plp.lpSum(x[t,i,j] for t in H) - plp.lpSum(y[t,i,j,k] for t in H for k in B)  == 0

	
	#Download validation
	for i in A:
		for j in S:
			for t in range(1,p):
				prob += plp.lpSum(y[t,i,j,k] for k in B) <= plp.lpSum(x[t1,i,j] for t1 in range(0, t))
	

	

	#Objective function
	prob.setObjective(plp.lpSum(x[t,i,j] for t in H for i in A for j in S))
	
	
	
	
	status = prob.solve(plp.PULP_CBC_CMD(msg = False))
	tl = prob.solutionTime
	print("ILP EXECUTION TIME: ", prob.solutionTime, "s")
	print("STATUS: ", status)
	

	if status == 1:
		print("COLLECTIONS DONE: ")
		for t in H:
			for j in S:
				for i in A:
					if x[t,i,j].value() == 1:
						print(t, ": ", j, " - ", i)

						
		print("COMMUNICATIONS DONE: ")
		for t in H:
			for k in B:
				for j in S:
					for i in A:
						if y[t,i,j,k].value() == 1:
							print(t, ": ", j, " " , i, " -> ", k)
		

	
