import pygame
from pygame.locals import (
    QUIT
)
import time
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

WHITE = (255,255,255)
BLACK = (0,0,0)
w, h = 700, 700
dt = 2
N_PARTICULES = 50
SIZE = 10
MAX_SPEED = 5

DAMP = 0.999

G = 0.01
EPS = 0.5


class Square(pygame.sprite.Sprite):
	def __init__(self, index=0, pos=(w//2, h//2), speed=(0,0), size=5, color=WHITE):
		super(Square, self).__init__()
		self.size = size
		self*.surf = pygame.Surface((size, size))
		self.surf.fill(color)
		self.rect = self.surf.get_rect()
		self.pos = np.array(pos, dtype=float)
		self.speed = np.array(speed, dtype=float)
		self.index = index
		self.color = color

	def update_bounds(self):
		vx, vy = self.speed
		if self.pos[0] <= 0 or self.pos[0]+self.size >= w-1:
			self.speed = np.array([-vx, vy])
			part.pos += dt*part.speed
		if self.pos[1] <= 0 or self.pos[1]+self.size >= h-1:
			self.speed = np.array([vx, -vy])
			part.pos += dt*part.speed*(1+EPS)

	def update(self):
		self.pos = self.pos + dt*self.speed*(1+EPS)
		screen.blit(self.surf, self.pos.astype(int))

def weight(part):
	# f = ma
	# g = a
	# g = vt
	# v = g/t
	part.speed += G/dt * np.array([0,1])

def friction(part, exp=1):
	part.speed *= DAMP


def generate_particules(n, size=5):
	''' Particule generation. Makes sure particules are not superimposed.'''
	squares = []
	x_rand = np.random.permutation(w-size)
	y_rand = np.random.permutation(h-size)
	p_map = defaultdict(int)
	s = SIZE
	for i in range(1, n+1):

		# 
		pos = (x_rand[i], y_rand[i])
		

		if i == n:
			s = 50
			speed = (0.1,0)
			pos = (w//2+s//2, h//2+s//2)

		# fixed loop to avoid superposition. If we reach max_iter, the particule i is not created.
		max_iter = 100
		it = 0
		ok = False
		while it < max_iter and ok:
			it += 1
			break_loop = False
			x, y = pos
	
			for x_ in range(int(x), int(x)+s):
				if break_loop:
					break
				for y_ in range(int(y), int(y)+s):
					if p_map[(int(x_),int(y_))] != 0:
						ok = True
						break

		# no superposition, we can add the particule
		if it < max_iter:
			speed = MAX_SPEED*np.random.rand(2) + 0.05
			speed = (-1)**np.random.randint(2)*speed 
			color = np.random.randint(50, 256, 3)
			square = Square(index=i, pos=pos, speed=speed, size=s, color=color)
			squares.append(square)
			p_map = set_map(p_map, square)

	return squares, p_map

def set_map(p_map, part):
	x, y = part.pos
	s = part.size
	for x_ in range(int(x), int(x)+s):
		for y_ in range(int(y), int(y)+s):
			p_map[(int(x_),int(y_))] = part.index
	return p_map

def set_map_all(p_map, particules):
	p_map = defaultdict(int)
	for part in particules:
		p_map = set_map(p_map, part)
	return p_map

def check_collisions(part, particules, p_map):
	''' Applies the collision between particules.
		The use of hash map makes the check constant.
	'''
	x, y = part.pos
	s = part.size
	k = part.index

	stop_loop_x = False
	# iterate over the particule area
	for x_ in range(int(x), int(x)+s):

		if stop_loop_x:
			stop_loop_x = False
			break

		for y_ in range(int(y), int(y)+s):
			k_ = p_map[(int(x_),int(y_))]

			# case where we collide with another particule.
			if k_ != 0 and k_ != k:
				 part_ = particules[k_-1]

				 # delta position to change the direction
				 # in the future, we need to create a reflected direction.
				 dpos = np.array(part.pos) - np.array(part_.pos)

				 # the speed is updated accordingly
				 part.speed = dpos / np.linalg.norm(dpos) * np.linalg.norm(part.speed)
				 part_.speed = -dpos / np.linalg.norm(dpos) * np.linalg.norm(part_.speed)

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





##############################################################

pygame.init()
screen = pygame.display.set_mode([w,h])

particules, p_map = generate_particules(N_PARTICULES, size=SIZE)

# big_particule = Square(size=50)
# particules.append(big_particule)
# p_map[(int(big_particule.pos[0]), int(big_particule.pos[1]))] = big_particule.index
# p_map = set_map(p_map, big_particule)

running = True
while running:
	screen.fill(BLACK)
	for event in pygame.event.get():
		if event.type == QUIT:
			running = False

	index = 0
	while index < len(particules):
		part = particules[index]
		part.update_bounds()
		index += 1
	
	# [weight(part) for part in particules]


	# [friction(part) for part in particules]

	
	[check_collisions(part, particules, p_map) for part in particules]
	[part.update() for part in particules]
	p_map = set_map_all(p_map, particules)
	

	pygame.display.flip()
	time.sleep(0.01)


pygame.quit()