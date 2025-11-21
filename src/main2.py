from ILP_LAS import ILP_LAS
from ILP2 import ILP2
from ILP import ILP

#Example 1
n = 9	#Number of regions
m = 2 #Number of satellites
o = 3 #Number of ground stations
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
beta = {}

for j in S:
	C[j] = 4
	if j==0:
		C[j]=4.2
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
    
#Collection opportunities <t,Sj,Ai>
col =  {(0,0,0): 0.25, 
		(0,0,8): 0.75, 
		(0,1,4): -0.5,
		(1,0,1): -0.25,
		(1,1,6): -1.0,
		(2,0,3): 1.5,
		(2,1,5): 0.0, 
		(2,1,6): 0.0,
		(3,1,7): 0.0,
		(4,0,4): 0.0,
		(5,0,8): -0.25,
		(5,1,0): -0.5,
		(6,0,6): 0.5, 
		(7,1,1): 0.5,
		(7,1,2): -0.5,
		(8,0,8): -0.5}
			


#Communication opportunities <t,j,k>:__
com = { (3,0,0): 1, 
		(4,1,1): 1,
		(7,0,1): 1,  
		(8,1,0): 1 }

pt = 3

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

