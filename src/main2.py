from ILP_LAS import ILP_LAS
import pandas as pd
# from ILP2 import ILP2
# from ILP import ILP
from os import path
from utility.dictionaryGene import process_satellite_data


# import your dictionary generator function
# from utility.dictionaryGene import process_satellite_data  # or whatever the function name is

# Get the directory where main2.py is located
base_dir = path.dirname(path.abspath(__file__))

# Join it with the relative path to the CSV (assuming it's in 'utility')
csv_path = path.join(base_dir, 'utility', 'time_sat_reg_1.csv')

# Now pass csv_path to your function
col,com = process_satellite_data(csv_path)

# col keys: (time, satcode, area_code)  where area_code starts with 'A'
# com keys: (time, satcode, ground_code) where ground_code starts with 'G'

# print("Collection Opportunities:", col)
# print("Communication Opportunities:", com)

# extract unique raw values
times_raw = sorted({t for (t,_,_) in list(col.keys()) + list(com.keys())})
sats_raw  = sorted({s for (_,s,_) in list(col.keys()) + list(com.keys())}, key=lambda x: int(x))
areas_raw = sorted({a for (t,s,a) in col.keys()})
grounds_raw= sorted({g for (t,s,g) in com.keys()})

# create mapping to contiguous indices
time_map = {t:i for i,t in enumerate(times_raw)}         # raw time -> compact index
inv_time_map = {i:t for t,i in time_map.items()}         # optional inverse mapping index -> raw time
sat_map  = {s:i for i,s in enumerate(sats_raw)}          # sat code -> sat_index
area_map = {a:i for i,a in enumerate(areas_raw)}        # area code -> area_index
ground_map= {g:i for i,g in enumerate(grounds_raw)}     # ground code -> ground_index

# counts (replaces n,m,o,p)
n = len(areas_raw) #Number of regions
m = len(sats_raw)  #Number of satellites
o = len(grounds_raw) #Number of ground stations
p = len(times_raw)   # number of distinct time stamps in the data

# lists (useful)
#Horizon, Satellites, AoI's, Ground stations
H = list(range(p))            # mapped time indices 0..p-1
S = list(range(m))						# mapped sat indices 0..m-1	
A = list(range(n))				    # mapped area indices 0..n-1
B = list(range(o)) 					  # mapped ground indices 0..o-1

# #Horizon
# H = [i for i in range(0,p)]
# #Satellites
# S = [i for i in range(0,m)]
# #AoI's
# A = [i for i in range(0,n)]
# #Ground stations
# B = [i for i in range(0,o)]

# For all valid collection opportunities:
# omega_collection: (t_idx, sat_idx, area_idx)
omega_collection = [
    (time_map[t_raw], sat_map[s_raw], area_map[a_raw])
    for (t_raw, s_raw, a_raw) in col.keys()
]

# For all valid communication opportunities:
# omega_comm: (t_idx, sat_idx, ground_idx)
omega_comm = [
    (time_map[t_raw], sat_map[s_raw], ground_map[g_raw])
    for (t_raw, s_raw, g_raw) in com.keys()
]

omega_transmit = []

# group collection by (t,s)
col_by_ts = {}
for (t_idx, s_idx, a_idx) in omega_collection:
    col_by_ts.setdefault((t_idx, s_idx), []).append(a_idx)

# group communication by (t,s)
com_by_ts = {}
for (t_idx, s_idx, g_idx) in omega_comm:
    com_by_ts.setdefault((t_idx, s_idx), []).append(g_idx)

# join groups: only where both collection and comm exist at same (t,s)
for (t_idx, s_idx), areas in col_by_ts.items():
    if (t_idx, s_idx) in com_by_ts:
        grounds = com_by_ts[(t_idx, s_idx)]
        for a_idx in areas:
            for g_idx in grounds:
                omega_transmit.append((t_idx, s_idx, a_idx, g_idx))

# # For checking purposes
# pd.DataFrame(omega_collection, columns=['t','s','a']).to_csv("omega_collection.csv", index=False)
# pd.DataFrame(omega_comm, columns=['t','s','g']).to_csv("omega_comm.csv", index=False)
# pd.DataFrame(omega_transmit, columns=['t','s','a','g']).to_csv("omega_transmit.csv", index=False)


#Memory capacity of the satellites
mem = {}
for j in S:
	mem[j] = 3
	
#Uplink capacity of each satellite
up = {}
for j in S:
	up[j] = 2
		
#Download capacity of the ground station
down = {}
for k in B:
	down[k] = 2
	

#Initial battery capacity of satellites
C = {}
theta = {}
beta = {}

for j in S:
	C[j] = 5.65
	theta[j] = 3
	beta[j] = 20

#"""
c = 0.4 #CHARGING		
d = 0.3 #DISCHARGING
e = 0.25 #COLLECTION
f = 0.25 #COMMUNICATION
g = 0.4  #COMPUTATION
"""
c = 0.4

d = 0.3
e = 0.2
f = 0.2

g = 0  
#"""
    
# #Collection opportunities <t,Sj,Ai>
# col =  {(0,0,0): 0.25, 
# 		(0,0,8): 0.75, 
# 		(0,1,4): -0.5,
# 		(1,0,1): -0.25,
# 		(1,1,6): -1.0,
# 		(2,0,3): 1.5,
# 		(2,1,5): 0.0, 
# 		(2,1,6): 0.0,
# 		(3,1,7): 0.0,
# 		(4,0,4): 0.0,
# 		(5,0,8): -0.25,
# 		(5,1,0): -0.5,
# 		(6,0,6): 0.5,
# 		(7,1,1): 0.5,
# 		(7,1,2): -0.5,
# 		(8,0,8): -0.5}
			


# #Communication opportunities <t,j,k>:__
# com = { (3,0,0): 1, 
# 		(3,1,1): 1,
# 		(7,0,1): 1,  
# 		(7,1,0): 1 }

# pt = 3



pt = 1

s = {}
for t in H:
	if t < 4:
		s[t,0] = 0 #LIGHT FOR S0
	else:
		s[t,0] = 1 #SHADOW FOR S0

for t in H:
	if t < 5:
		s[t,1] = 0 #LIGHT FOR S1
	else:
		s[t,1] = 1 #SHADOW FOR S1

'''
print("\n\nSCHEDULE WITHOUT BATTERY CONSTRAINT AND PROCESSING CAPABILITY")
ILP(H, S, A, B, mem, up, down, col, com, p)


print("\n\nSCHEDULE WITHOUT BATTERY CONSTRAINT")
ILP2(H, S, A, B, mem, up, down, col, com, p, pt)
'''
print("\n\nSCHEDULE FOLLOWING BATTERY CONSTRAINT AND PROCESSING CAPABILITY")
ILP_LAS(H, S, A, B, C, mem, up, down, col, com, theta, p, pt, c, d, e, f, g, s, beta)