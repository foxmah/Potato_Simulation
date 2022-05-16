import random
import time
import pygame
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import pandas as pd


class Map:
	def __init__(self, height, length, X, Y, sleep, visualize=False):
    	# Number of horizontal & vertical cells respectively
		self.length, self.height = length, height

		# Length & width of pygame window
		self.X, self.Y = X, Y

		# Number of horizontal & vertical pixels for each cell
		self.cell_len, self.cell_hgt = self.X/length, self.Y/height

		# Days & hours past since the game started
		self.day, self.hour = 0, 0

		# List of the cells constituting the map	
		self.list = [[Cell(i, j) for j in range(self.length)] for i in range(self.height)]

		# Number of benevolent & greedy potatoes in the begining
		self.counter = [0, 0]

		self.vis = visualize
		self.sleep = sleep
		if(self.vis):
			self.display = pygame.display.set_mode((X, Y))


	def visualize(self):
		# Drawing the map with pygame
		if(self.vis):
			white, blue, green =(255, 255, 255), (0, 0, 128), (0, 255, 0)
			self.display.fill(white)

			# Drawing potatoes & food
			for i in self.list:
				for j in i:
					for k in j.residents:
						k.draw_potato()
					if(j.food==1):
						j.draw_food(self)

			# Drawing vertical & horizontal lines to show a cell
			for i in range(1, self.length):
				pygame.draw.line(self.display, (0, 0, 0), (self.cell_len*i, 0), (self.cell_len*i, self.Y))
			for i in range(1, self.height):
				pygame.draw.line(self.display, (0, 0, 0), (0, self.cell_hgt*i), (self.X, self.cell_hgt*i))

			# Checking if the user has quitted the pygame window
			for event in pygame.event.get():
				if event.type==pygame.QUIT:
					pygame.quit()
					quit()

			# Showing the number of days & hours passed
			clock_font = pygame.font.Font('freesansbold.ttf', 11)
			clock = clock_font.render(f'D:{self.day} h:{self.hour}', True, green, blue)
			clock_rect = clock.get_rect()
			clock_rect.center = (self.cell_len, self.cell_hgt)
			self.display.blit(clock, clock_rect)

			# Showing the number of benevolent & greedy potatoes
			counter_font = pygame.font.Font('freesansbold.ttf', 11)		
			counter_text = counter_font.render(f'B:{self.counter[0]} G:{self.counter[1]}', True, green, blue)
			counter_text_rect = counter_text.get_rect()
			counter_text_rect.center = (self.cell_len, self.cell_hgt*2)
			self.display.blit(counter_text, counter_text_rect)

			pygame.display.update()
			# Sleep time between cycles (comment if not needed)
			time.sleep(self.sleep)


	def random_coord_in_map(self):
		return random.randint(0, self.height-1), random.randint(0, self.length-1)


	def new_gen(self):
		# Determining whether a potato dies, lives or reproduces on the next day
		l = []
		for row in self.list:
			for cell in row:
				if(cell.residents!=[]):
					cell.split_food()
					for potato in cell.residents:
						l.append([potato, potato.food])
						potato.food = 0
				cell.food = 0

		for i in l:
			potato, food = i[0], i[1]
			potato.life_exp(food)


	def dist_food(self, pcs):
		# Distributing pieces of food randomly in the map 
		for i in range(pcs):
			n, m = self.random_coord_in_map()
			self.list[n][m].food = 1


	def move_all(self):
		# Moving all the potatoes to adjacent cells randomly if not occupied
		for rows in self.list:
			for cell in rows:
				for potato in cell.residents:
					potato.move()

		for rows in self.list:
			for cell in rows:
				for potato in cell.residents:
					potato.moved_yet = False


class Cell:
	def __init__(self, n, m):
		self.food = 0
		self.residents = []  # List of potatoes in the cell
		self.coord = [n, m]


	def vacant(self):
		# Determining if a cell is occupied or not
		if(len(self.residents)<2):
			return 1
		return 0


	def add_resident(self, res):
		self.residents.append(res)


	def split_food(self):
		# Determining what portion of the food in the cell is given to a potato based on it's personality
		if(self.food==0):
			for potato in self.residents: potato.food = 0

		# If there's only one resident in a cell, it takes all of the food
		elif(len(self.residents)==1):
			self.residents[0].food = 2

		elif(len(self.residents)==2):
			# 1- If both residents are greedy, they receive no food.
			# 2- If both residents are benevolent, each one receives one piece.
			# 3- If one resident is benevolent & the other greedy, the former
			#    takes half of a peice & the latter takes one & a half pieces of food.
			if(self.residents[0].type == self.residents[1].type):
				for potato in self.residents:  potato.food = 1-potato.type
			else:
				for potato in self.residents:  potato.food = (potato.type + 0.5)


	def draw_food(self, mp):
		# Drawing two circles representing two tangerines
		tangerine = (242, 133, 0)
		x_1 = mp.cell_len*(self.coord[1]+0.250)
		x_2 = mp.cell_len*(self.coord[1]+0.750)
		y = mp.cell_hgt*(self.coord[0]+0.75)
		r = int(min(mp.cell_hgt/6, mp.cell_len/6))
		pygame.draw.circle(mp.display, tangerine, (x_1, y), r, width=0)
		pygame.draw.circle(mp.display, tangerine, (x_2, y), r, width=0)


class Potato:
	mp = []
	def __init__(self, personality, x, y):
		self.type = personality  # 0 for benevolent & 1 for greedy
		self.coord = [x, y]
		self.food = 0
		self.moved_yet = False # Whether a potato has moved in a round or not
		self.mp.list[x][y].add_resident(self)
		self.mp.counter[personality] += 1


	def remove(self):
		self.mp.list[self.coord[0]][self.coord[1]].residents.remove(self)


	def vacant_neighbours(self):
		# Discovering vacant, adjacent cells to a potato
		l = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
		nghbrs = []
		for i in l:
			x, y = self.coord[0]+i[0], self.coord[1]+i[1]
			if(x>=0 and x<self.mp.height and y>=0 and y<self.mp.length):
				if(self.mp.list[x][y].vacant()):
					nghbrs.append(i)
		return nghbrs


	def move(self):
		# Moving a potato to adjacent cells if possible
		if not self.moved_yet:
			self.moved_yet = True
			x, y = self.coord[0], self.coord[1]
			nghbrs = self.vacant_neighbours()
			if(self.mp.list[x][y].food == 0 and len(nghbrs)): 
				next_move = random.choice(self.vacant_neighbours())
				next_x, next_y = x+next_move[0], y+next_move[1]
				self.remove()
				self.coord = [next_x, next_y]
				self.mp.list[next_x][next_y].add_resident(self)


	def life_exp(self, p):
		# Determining the probablity of a potato dying, living or reproducing
		# based on the food it's eaten the day before
		r = random.randint(0, 1)
		if(p==0):
			Potato.mp.counter[self.type] -= 1
			self.remove()
		elif(p==0.5 and r):
			Potato.mp.counter[self.type] -= 1
			self.remove()
		elif(p==1.5 and r):
			self.reproduce()
		elif(p==2):
			self.reproduce()


	def reproduce(self):
		# Creating a new potato similar to the one that it's descended from
		x, y = self.mp.random_coord_in_map()
		if(self.mp.list[x][y].vacant()):
			Potato(self.type, x, y)

	def draw_potato(self):
		brown, dark_brown = (245, 207, 133), (142, 107, 36) 
		color = [brown, dark_brown]
		cell_len, cell_hgt = self.mp.cell_len, self.mp.cell_hgt
		x, y = self.coord[0], self.coord[1]
		cell = self.mp.list[x][y]
		index = cell.residents.index(self)
		top_left_x = cell_len*(y+(0.5*index)) + index
		top_left_y = cell_hgt*x
		rct = [top_left_x, top_left_y, cell_len//2 -1, cell_hgt//2]
		pygame.draw.rect(self.mp.display, color[self.type], rct)


def cycle(mp, days, hours_per_day, food_cycle, food_per_cycle, n_potatoes):
	if(mp.vis):
		pygame.init()

	# The number of benevolent and greedy potatoes on each day
	greedy_list, benevolent_list = [], []

	# Adding a number of benevolent and greedy potatoes to the map based on the input
	for i, j in enumerate(n_potatoes):
		for k in range(j):
			x, y = mp.random_coord_in_map()
			if(mp.list[x][y].vacant()):
				Potato(i, x, y)

	benevolent_list.append(mp.counter[0])
	greedy_list.append(mp.counter[1])
	mp.visualize()

	for i in range(1, days*hours_per_day+1):
		mp.day, mp.hour = i//hours_per_day, i%hours_per_day
		mp.move_all()
		mp.visualize()
		if(i%food_cycle==0):
			mp.dist_food(food_per_cycle)
			mp.visualize()
		if(i%hours_per_day==0):
			mp.new_gen()
			mp.visualize()
			benevolent_list.append(mp.counter[0])
			greedy_list.append(mp.counter[1])
	return benevolent_list, greedy_list


def graph(benevolent, greedy, days, axis, kind="line"):
	if(kind=="line"):
		axis.plot(list(range(0, days+1)), benevolent, color="g", linewidth=1)
		axis.plot(list(range(0, days+1)), greedy, color="r", linewidth=1)
		axis.set_xlabel("Time(day)")
	elif(kind=="stacked"):
		axis.stackplot(list(range(0, days+1)),
	          [benevolent, greedy],
	          labels=['mean_B', 'mean_G'],
	          colors=['g', 'r'],
	          alpha=0.7)
		axis.legend(loc=2, fontsize='large')
		axis.set_xlabel("Time(day)")