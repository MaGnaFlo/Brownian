import numpy as np
from collections import defaultdict
import pygame
from parameters import *


class Particule(pygame.sprite.Sprite):
	def __init__(self, shape="square", index=0, pos=(W/2, H/2), speed=(0,0), size=5, color=WHITE):
		super().__init__()
		self.shape = shape
		self.size = size
		self.surf = pygame.Surface((size, size))
		self.surf.fill(color)
		self.rect = self.surf.get_rect()
		self.pos = np.array(pos, dtype=float)
		if self.shape == "disk":
			self.pos += self.size/2
		self.speed = np.array(speed, dtype=float)
		self.index = index
		self.color = color

	def __repr__(self):
		return "Particule {} :\n\tPosition: {}\n\tSpeed: {}\n\tSize: {}".format(
				self.index, self.pos, self.speed, self.size)

	def update_bounds(self):
		vx, vy = self.speed
		if self.pos[0] <= 0 or self.pos[0]+self.size >= W-1:
			self.speed = np.array([-vx, vy])
			self.pos += dt*self.speed
		if self.pos[1] <= 0 or self.pos[1]+self.size >= H-1:
			self.speed = np.array([vx, -vy])
			self.pos += dt*self.speed*(1+EPS)

	def update(self, screen):
		self.pos = self.pos + dt*self.speed*(1+EPS)
		if self.shape == "disk":
			pygame.draw.circle(screen, self.color, 
								self.pos+self.size/2, 
								self.size/2)
		else:
			screen.blit(self.surf, self.pos.astype(int))

def generate_particules(n, size=5):
	''' Particule generation. Makes sure particules are not superimposed.'''
	p_map = defaultdict(int)
	particules = []
	s = SIZE

	# first create the large central particule.
	color = np.random.randint(50, 256, 3)
	particule = Particule(index=1, shape="disk", pos=np.array([W/2, H/2]), speed=(0.1,0), size=50, color=color)
	particules.append(particule)
	p_map = set_map(p_map, particule)

	# loop over the number of desired additional particules
	for i in range(2, n+1):
		max_iter = 100
		it = 0
		found = True

		x = np.random.randint(s+1, W-2*s-1)
		y = np.random.randint(s+1, H-2*s-1)
		while it < max_iter and not found:
			# loop over the particule (will assume square)
			for x_ in range(x, x+s):
				for y_ in range(y, y+s):
					if p_map[x_,y_] == 0:
						found = False
			x = np.random.randint(s+1, W-2*s-1)
			y = np.random.randint(s+1, H-2*s-1)
			it += 1

		# if we found a point, randomize it and add it to the set/map.
		if found:
			pos = np.array([x, y])
			speed = MAX_SPEED*np.random.rand(2) + 0.05
			speed = (-1)**np.random.randint(2)*speed 
			color = np.random.randint(50, 256, 3)
			particule = Particule(index=i, shape="disk", pos=pos, speed=speed, size=s, color=color)
			particules.append(particule)
			p_map = set_map(p_map, particule)

	return particules, p_map

def set_map(p_map, part):
	x, y = part.pos
	s = part.size
	for x_ in range(int(x), int(x)+s):
		for y_ in range(int(y), int(y+s)):
			if part.shape == "square":
				p_map[(int(x_), int(y_))] = part.index
			elif part.shape == "disk":
				if (x_-x)**2 + (y_-y)**2 <= s**2/4:
					p_map[(int(x_),int(y_))] = part.index
			else:
				print("Unknown shape argument.")
				raise TypeError
	return p_map

def set_map_all(p_map, particules):
	p_map = defaultdict(int)
	for part in particules:
		p_map = set_map(p_map, part)

	for x in range(-1, W):
		p_map[(x,0)] = -11
		p_map[(x,H-1)] = -12
	for y in range(-1, H):
		p_map[(0,y)] = -21
		p_map[(W-1,y)] = -22
	return p_map

def check_collisions(part, particules, p_map):
	''' Applies the collision between particules.
		The use of hash map makes the check constant.
	'''
	x, y = part.pos
	s = part.size
	k = part.index

	stop_loop_x = False
	# iterate over the particule area.
	for x_ in range(int(x), int(x+s)):

		if stop_loop_x:
			stop_loop_x = False
			break

		# first, find out if we hit a boundary.
		for y_ in range(int(y), int(y+s)):
			k_ = p_map[(int(x_),int(y_))]
			if k_ in [-11,-12,-21,-22]:

				if k_ == -11:
					norm = np.array([0,1])
				if k_ == -12:
					norm = np.array([0,-1])
				if k_ == -21:
					norm = np.array([1,0])
				if k_ == -22:
					norm = np.array([-1,0])

				# the speed is updated accordingly.
				part.speed = part.speed - 2*part.speed.dot(norm)*norm

				# wipe the current index in the map.
				p_map[tuple(part.pos)] = 0

				# update positions
				part.pos += dt*part.speed*(1+EPS)

				# add indices to map at new position.
				x, y = part.pos 

				p_map[(int(x),int(y))] = part.index

				# we found a correct place to set the particule. Stop the loop.
				stop_loop_x = True
				break

			# then check if we collide with another particule.
			elif k_ != 0 and k_ != k and k != -1:
				part_ = particules[k_-1]

				# delta position to change the direction
				# in the future, we need to create a reflected direction.
				normal = np.array(part.pos) - np.array(part_.pos)
				normal = normal / np.linalg.norm(normal)

				# the speed is updated accordingly.
				part.speed = part.speed - 2*part.speed.dot(normal)*normal
				part_.speed = part_.speed - 2*part_.speed.dot(normal)*normal

				# wipe the current index in the map
				p_map[tuple(part.pos)] = 0
				p_map[tuple(part_.pos)] = 0

				# update positions
				part.pos += dt*part.speed*(1+EPS)
				part_.pos += dt*part_.speed*(1+EPS)

				# add indices to map at new position.
				x, y = part.pos 
				x_, y_ = part_.pos
				p_map[(int(x),int(y))] = part.index
				p_map[(int(x_),int(y_))] = part_.index

				# we found a correct place to set the particule. Stop the loop.
				stop_loop_x = True
				break


