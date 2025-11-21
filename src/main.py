from ILP_LAS import ILP_LAS
from ILP2 import ILP2
from ILP import ILP

#Example 1
n = 9	#Number of regions
m = 2 #Number of satellites
o = 1 #Number of ground stations
p = 9 #Time


#Horizon
H = [i for i in range(0,p)]
#Satellites
S = [i for i in range(0,m)]
#AoI's
A = [i for i in range(0,n)]
#Ground stations
B = [i for i in range(0,o)]

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
for j in S:
	C[j] = 4
	theta[j] = 3
#"""
c = 0.4     #charging per unit time 		
d = 0.3     #constant discharging per unit time
e = 0.25    #collection discharging per unit time
f = 0.25    #communication discharging per unit time
g = 0.4     #computation/processing discharging per unit time
"""
c = 0.4
d = 0.3
e = 0.2
f = 0.2
g = 0  
#"""
    
#Collection opportunities <t,Sj,Ai>
col =  {(0,0,0): 0.25, 
		(0,0,4): 0.75, 
		(1,1,1): -1.0,  
		(2,0,2): 1.5, 
		(2,1,0): 0.0, 
		(3,0,5): 0.5, 
		(5,0,1): -0.25,
		(5,0,3): -0.5, 
		(6,1,0): 0.5, 
		(6,1,2): -0.5, }
			


#Communication opportunities
com = { (4,0,0): 1, 
		(4,1,0): 1,
		(7,1,0): 1,  
		(8,0,0): 1 }

pt = 3

s = {}
for t in H:
	if t < 4:
		s[t,0] = 0
	else:
		s[t,0] = 1

for t in H:
	if t < 4:
		s[t,1] = 0
	else:
		s[t,1] = 1


print("\n\nSCHEDULE WITHOUT BATTERY CONSTRAINT AND PROCESSING CAPABILITY")
ILP(H, S, A, B, mem, up, down, col, com, p)


print("\n\nSCHEDULE WITHOUT BATTERY CONSTRAINT")
ILP2(H, S, A, B, mem, up, down, col, com, p, pt)


print("\n\nSCHEDULE FOLLOWING BATTERY CONSTRAINT AND PROCESSING CAPABILITY")
ILP_LAS(H, S, A, B, C, mem, up, down, col, com, theta, p, pt, c, d, e, f, g, s)

