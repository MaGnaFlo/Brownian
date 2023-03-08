import pygame
from pygame.locals import QUIT
import time
from parameters import *
from particules import *



if __name__ == "__main__":
	############################# MAIN LOOP #################################

	# initialize
	pygame.init()
	screen = pygame.display.set_mode([W, H])
	particules, p_map = generate_particules(N_PARTICULES, size=SIZE)
	print("Generated {} particules.".format(len(particules)))
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

		# particules update
		p_map = set_map_all(p_map, particules)
		for part in particules:
			check_collisions(part, particules, p_map)
			part.update(screen)
		
		# update
		pygame.display.flip()

	pygame.quit()

