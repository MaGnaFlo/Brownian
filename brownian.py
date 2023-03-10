import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from pygame.locals import QUIT
import time
from parameters import *
from particles import Particle_Set
from interactions import Interactions
import argparse
import numpy as np


if __name__ == "__main__":
	############################# MAIN LOOP #################################

	# arguments
	parser = argparse.ArgumentParser()
	parser.add_argument("-n", "--nparts", type=int, default=N_PARTICULES)
	parser.add_argument("-c", "--color", type=str, default=None)
	args = parser.parse_args()

	n_particles = args.nparts
	parts_color = np.array(args.color.split(','), dtype=int)
	# initialize
	os.system("cls" if os.name == "nt" else "clear")
	pygame.init()
	screen = pygame.display.set_mode([W, H])
	
	particles = Particle_Set(n_particles, shape="disk")
	particles.create_central_particle(mass=1000, size=SIZE_LARGE)
	particles.generate_particles(size=SIZE, color=parts_color)
	particles.set_map_all()

	interactions = Interactions(particles)
	running = True

	while running:
		screen.fill(BLACK)

		# events
		for event in pygame.event.get():
			if event.type == QUIT:
				running = False
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_q:
					running = False

		# particles update
		particles.set_map_all()
		for part in particles:
			interactions.check_collisions(part)
			part.update(screen)
		
		# update
		pygame.display.flip()

	pygame.quit()

