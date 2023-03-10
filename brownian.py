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
	parser.add_argument("-m", "--mass", type=int, default=MASS_LARGE)
	parser.add_argument("-t", "--track", type=bool, default=False)
	args = parser.parse_args()

	n_particles = args.nparts
	parts_color = np.array(args.color.split(','), dtype=int)
	mass = args.mass
	track = args.track

	# initialize
	os.system("cls" if os.name == "nt" else "clear")
	pygame.init()
	if track:
		pad = 10
		screen = pygame.display.set_mode([W*2 + pad, H])
		tracked_pos = [(3*W//2+pad, H//2)]
	else:
		screen = pygame.display.set_mode([W, H])
	
	particles = Particle_Set(n_particles, shape="disk")
	particles.create_central_particle(mass=mass, size=SIZE_LARGE)
	particles.generate_particles(size=SIZE, color=parts_color)
	particles.set_map_all()
	particles.set_boundaries_map(pad=100)

	interactions = Interactions(particles)
	running = True

	while running:
		screen.fill(BLACK)
		if track:
			pygame.draw.line(screen, WHITE, (W+pad//2,0), (W+pad//2, H-1), 2)

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

		if track:
			x, y = particles[0].pos
			tracked_pos.append((x + W + pad, y))
			pygame.draw.circle(screen, WHITE, tracked_pos[-1], 3)
			for i in range(len(tracked_pos)-1):
				pygame.draw.line(screen, WHITE, tracked_pos[i], tracked_pos[i+1])
		
		# update
		pygame.display.flip()

	pygame.quit()

