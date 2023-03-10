import numpy as np
from collections import defaultdict
import pygame
from parameters import *
from utils import ProgressBar


class Particle(pygame.sprite.Sprite):
	''' Represents a single particle, defined as an element
		of the frame having various properties:
			position
			speed
			mass
			size
			index
			color
		'''
	def __init__(self, shape="square", index=0, pos=(W/2, H/2), speed=(0,0), 
					mass=1, size=10, color=(255,255,255)):
		super().__init__()
		self.shape = shape
		self.mass = mass
		self.size = size
		
		self.pos = np.array(pos, dtype=float)
		if self.shape == "disk":
			self.pos += self.size/2
		self.speed = np.array(speed, dtype=float)
		self.index = index

		self.color = color
		self.surf = pygame.Surface((self.size, self.size))
		self.rect = self.surf.get_rect()

	def __repr__(self):
		return "particle {} :\n\tPosition: {}\n\tSpeed: {}\n\tSize: {}\n\tMass: {}".format(
				self.index, self.pos, self.speed, self.size, self.mass)

	def update(self, screen):
		''' Update the position and blit the screen. '''
		self.pos = self.pos + dt*self.speed
		if self.shape == "disk":
			pygame.draw.circle(screen, self.color, self.pos, self.size/2)
		else:
			screen.blit(self.surf, self.pos.astype(int))


class Particle_Set:
	''' Container of particles. Additionally deals with the collision map. '''
	def __init__(self, n_part=100, shape="disk"):
		self.n_particles = n_part
		self.map = defaultdict(int)
		self.particles = []

	def __len__(self):
		return len(self.particles)

	def set_map(self, part):
		''' Sets the particle map at the area of the particle to its index. '''
		x, y = part.pos
		s = part.size
		for x_ in range(int(x-s/2), int(x+s/2)+1):
			for y_ in range(int(y-s/2), int(y+s/2)+1):
				if part.shape == "square":
					self.map[(int(x_), int(y_))] = part.index
				elif part.shape == "disk":
					if (x_-x)**2 + (y_-y)**2 <= s**2/4:
						self.map[(int(x_),int(y_))] = part.index
				else:
					print("Unknown shape argument.")
					raise TypeError

	def set_map_all(self):
		''' Sets the particle map for all particles and for the boudaries. '''
		self.map = defaultdict(int)
		for part in self.particles:
			self.set_map(part)

		# create boundaries
		for x in range(-1, W):
			self.map[(x,0)] = -11
			self.map[(x,H-1)] = -12

		for y in range(-1, H):
			self.map[(0,y)] = -21
			self.map[(W-1,y)] = -22

	def create_central_particle(self, size=50, mass=50, color=(40,90,250)):
		''' Creates the large particle at the center of the frame. '''
		particle = Particle(index=1, shape="disk", pos=np.array([W/2, H/2]), 
							  speed=(0,0), size=size, mass=mass, color=color)
		self.set_map(particle)
		self.particles.append(particle)

	def generate_particles(self, size=10, mass=10, shape="disk", color=None):
		''' particle generation. Makes sure particles are not superimposed.'''
		s = size

		# loop over the number of desired additional particles
		i = 2
		pbar = ProgressBar(self.n_particles+1, text="Generating particles")
		while i < self.n_particles+1:
			it = 0
			found = True

			while it < MAX_FIND_GENERATION and found:
				x = np.random.randint(s+1, W-2*s-1)
				y = np.random.randint(s+1, H-2*s-1)

				# loop over the particle area (will assume square)
				stop_loop = False
				for x_ in range(int(x-s/2), int(x+s/2)+1):
					if stop_loop:
						break
					for y_ in range(int(y-s/2), int(y+s/2)+1):
						if (x_-x)**2 + (y_-y)**2 <= s**2/4-EPS:
							if self.map[x_,y_] != 0:
								found = False
								stop_loop = True
								break
				
				it += 1

			# if we found a empty spot, randomize it and add it to the set/map.
			if found:
				pos = np.array([x, y])
				speed = MAX_SPEED*np.random.rand(2) + 0.05
				speed = (-1)**np.random.randint(2)*speed 
				color_ = np.random.randint(50, 256, 3) if color is None else color

				particle = Particle(index=i, shape=shape, pos=pos, size=size, speed=speed, mass=mass, color=color_)
				self.particles.append(particle)
				self.set_map(particle)
				i+=1
			pbar.update(i)

		pbar.end("Generated {} particles.".format(i-1))
