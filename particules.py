import numpy as np
from collections import defaultdict
import pygame
from parameters import *


class Particule(pygame.sprite.Sprite):
	def __init__(self, shape="disk", index=0, pos=(W/2, H/2), speed=(0,0), size=5, color=WHITE):
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
	particules = []
	x_rand = np.random.permutation(W)
	y_rand = np.random.permutation(H)
	p_map = defaultdict(int)
	s = SIZE
	for i in range(1, n+1):
		pos = (x_rand[i], y_rand[i])
		
		# this is the large particule
		if i == n:
			s = 50
			speed = (0.1,0)
			pos = (W/2+s/2, H/2+s/2)

		# fixed loop to avoid superposition. If we reach max_iter, the particule i is not created.
		max_iter = 100
		it = 0
		ok = False
		while it < max_iter and ok:
			it += 1
			break_loop = False
			x, y = pos
	
			for x_ in range(int(x), int(x+s)):
				if break_loop:
					break
				for y_ in range(int(y), int(y+s)):
					if p_map[(int(x_),int(y_))] != 0:
						ok = True
						break

		# no superposition, we can add the particule
		if it < max_iter:
			speed = MAX_SPEED*np.random.rand(2) + 0.05
			speed = (-1)**np.random.randint(2)*speed 
			color = np.random.randint(50, 256, 3)
			particule = Particule(index=i, pos=pos, speed=speed, size=s, color=color)
			particules.append(particule)
			p_map = set_map(p_map, particule)

	return particules, p_map

def set_map(p_map, part):
	x, y = part.pos
	s = part.size
	for x_ in range(int(x), int(x)+s):
		for y_ in range(int(y), int(y+s)):
			if part.shape == "square":
				p_map[(int(x_),int(y_))] = part.index
			elif part.shape == "disk":
				if (x_-x)**2 + (y_-y)**2 < s**2/4:
					p_map[(int(x_),int(y_))] = part.index
			else:
				print("Unknown shape argument.")
				raise TypeError
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
	for x_ in range(int(x), int(x+s)):

		if stop_loop_x:
			stop_loop_x = False
			break

		for y_ in range(int(y), int(y+s)):
			k_ = p_map[(int(x_),int(y_))]

			# case where it collides with another particule.
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

