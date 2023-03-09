import pygame
from pygame.locals import QUIT
import time
from parameters import *
from particles import Particle_Set
from interactions import Interactions


if __name__ == "__main__":
	############################# MAIN LOOP #################################

	# initialize
	pygame.init()
	screen = pygame.display.set_mode([W, H])
	
	particles = Particle_Set(N_PARTICULES, shape="disk")
	particles.create_central_particle()
	particles.generate_particles()
	particles.set_map_all()

	interactions = Interactions(particles)

	print("Generated {} particles.".format(len(particles)))
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
		for part in particles.particles:
			interactions.check_collisions(part)
			part.update(screen)
		
		# update
		pygame.display.flip()

	pygame.quit()

