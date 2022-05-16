from Potato_Simulation import *

# Visualizing the simulation or not
VIS = True

# Length & width of pygame window if VIS is True
X, Y = 800, 800

# Number of horizontal & vertical cells respectively
N, M = 20, 20

# The interval between two visualizations(in seconds)
SLEEP = 0

# Simulation runs for DAYS. For example if DAYS = 50,
# simulation runs for 50 days.
DAYS = 100

# Number of hours in a day
HOURS_PER_DAY = 24

# Food is randomly distributed in the map every FOOD_CYCLE(in hours).
# For instance if FOOD_CYCLE = 12, food is randomly distributed in the map every 12 hours.
FOOD_CYCLE = 12

'''Number of benevolent and greedy potatoes in the begining.
(However the number of potatoes might not be exactly the same
as they're randomly distributed in the map. So if a potato
happens to fall on a nonvacant cell, it cannot be placed.
Since the overall effect is trivial, correcting it doesn't
make much difference.)
'''
BENEVOLENT, GREEDY = 100, 100

''' Number of pieces of food distributed at every FOOD_CYCLE. (FPC: food per cycle)
If INIT_FPC is not equal to FIN_FPC, then (FIN_FPC - INIT_FPC + 1) simulations
with different FPC run. Stacked graph will show their mean. And line graph will
show them individually.
'''
INIT_FPC, FIN_FPC = 200, 202



interval = FIN_FPC - INIT_FPC + 1
mean_bnv = [0 for i in range(DAYS+1)]
mean_grd = [0 for i in range(DAYS+1)]
figure, axis = plt.subplots(1, 2)

for i in range(interval):
	mp = Map(M, N, X, Y, SLEEP, VIS)
	Potato.mp = mp
	x, y = cycle(mp, DAYS, HOURS_PER_DAY, FOOD_CYCLE, INIT_FPC+i, [BENEVOLENT, GREEDY])
	for j in range(DAYS+1):
		mean_bnv[j] += x[j]/interval
		mean_grd[j] += y[j]/interval
	graph(x,y, DAYS, axis[1], kind="line")
graph(mean_bnv, mean_grd, DAYS, axis[0], kind="stacked")
plt.show()
