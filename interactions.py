from particles import Particle_Set
from parameters import EPS, dt
import numpy as np


class Interactions:
	''' Class to deal with interactions (forces, collisions, ...) '''
	def __init__(self, particles):
		self.particles = particles

	def elastic_collision(self, part1, part2):
		''' Update speeds of two particles considering an elastic collision. '''
		pos1, pos2 = part1.pos, part2.pos
		v1, v2 = part1.speed, part2.speed
		m1, m2 = part1.mass, part2.mass 

		# updating
		m_factor1 = 2*m2/(m1+m2)
		m_factor2 = 2*m1/(m1+m2)

		scal1 = (v1-v2).dot(pos1-pos2)
		scal2 = (v2-v1).dot(pos2-pos1)
		if np.abs(scal1) < 0.1: # slight condition to prevent tangential behavior error.
			scal1 = 10*scal1/np.abs(scal1)
			scal2 = 10*scal2/np.abs(scal2)

		delta_pos1 = (pos1 - pos2) / np.linalg.norm(pos2-pos1)**2
		delta_pos2 = -delta_pos1

		part1.speed = v1 - m_factor1 * scal1 * delta_pos1
		part2.speed = v2 - m_factor2 * scal2 * delta_pos2

	def is_out_of_bounds(self, part):
		''' Checks if a particle is out of bounds.'''
		out_of_bounds = False
		x, y = part.pos
		s = part.size
		break_loop = False
		for x_ in range(int(x-s/2), int(x+s/2)+1):
			if break_loop:
				break
			for y_ in range(int(y-s/2), int(y+s/2)+1):
				if True:
					out_of_bounds = (self.particles.map[(x_,y_)] < 0)
					if out_of_bounds:
						break_loop = True
						break
		return out_of_bounds

	def boundaries_collision(self, part, index):
		''' Update particle when it hits a boundary '''
		if index == -11:
			norm = np.array([0,1])
		if index == -12:
			norm = np.array([0,-1])
		if index == -21:
			norm = np.array([1,0])
		if index == -22:
			norm = np.array([-1,0])

		# the speed is updated accordingly.
		part.speed = part.speed - 2*part.speed.dot(norm)*norm

		# update positions
		previous_pos = part.pos
		while self.is_out_of_bounds(part):
			part.pos += norm

		# wipe the current index in the map.
		self.particles.map[tuple(previous_pos)] = 0
		self.particles.map[tuple(part.pos)] = part.index

	def check_collisions(self, part):
		''' Applies the collision between particles.
			The use of hash map makes the check constant.
		'''
		x, y = part.pos
		s = part.size
		k = part.index

		stop_loop_x = False
		# iterate over the particle area.
		for x_ in range(int(x-s/2), int(x+s/2)+1):

			if stop_loop_x:
				stop_loop_x = False
				break

			# first, find out if we hit a boundary.
			for y_ in range(int(y-s/2), int(y+s/2)+1):
	
				k_ = self.particles.map[(int(x_),int(y_))]
				if k_ in [-11,-12,-21,-22]:
					self.boundaries_collision(part, k_)
					stop_loop_x = True
					break

				# then check if we collide with another particle.
				elif k_ != 0 and k_ != k:
					# avoid out of disk + eps
					if (x_-x)**2 + (y_-y)**2 > s**2/4 + EPS:
						continue

					part_ = self.particles[k_-1]
					self.elastic_collision(part, part_)

					# update positions
					part.pos += dt*part.speed + part.speed / np.linalg.norm(part.speed)
					part_.pos += dt*part_.speed + part_.speed / np.linalg.norm(part_.speed)

					# we found a correct place to set the particle. Stop the loop.
					stop_loop_x = True
					break


