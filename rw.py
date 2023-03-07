import pygame
from pygame.locals import (
    QUIT
)
import time
import numpy as np
import matplotlib.pyplot as plt

WHITE = (255,255,255)
w, h = 1000, 800
dt = 0.001

class Square(pygame.sprite.Sprite):
	def __init__(self, size=5, color=WHITE):
		super(Square, self).__init__()
		self.size = size
		self.surf = pygame.Surface((size, size))
		self.surf.fill(color)
		self.rect = self.surf.get_rect()

def update_pos(pos, size, w, h):
	n = np.random.randint(4)
	if n == 0:
		if pos[0] < w-1:
			pos = (pos[0]+size, pos[1])
	if n == 1:
		if pos[0] > 0:
			pos = (pos[0]-size, pos[1])
	if n == 2:
		if pos[1] < h-1:
			pos = (pos[0], pos[1]+size)
	if n == 3:
		if pos[1] > 0:
			pos = (pos[0], pos[1]-size)
	return pos

class Walk:
	def __init__(self, size, shape="square", pos=(w//2, h//2), plot=True):
		self.size = size
		self.pos = pos 
		self.shape = shape
		self.radii = []
		self.draw()

		if plot:
			plt.ion()
			self.fig = plt.figure()
			self.ax = self.fig.add_subplot(111)
			self.ax.set_xlim(0, 10000)
			self.ax.set_ylim(0, 1000)
			self.line, = self.ax.plot(np.arange(len(self.radii)), self.radii)


	def draw(self):
		if self.shape == "square":
			square = Square(size=self.size)
			screen.blit(square.surf, self.pos)

	def update(self):
		self.draw()
		self.pos = update_pos(self.pos, self.size, w, h)
		self.radii.append(np.linalg.norm([self.pos[0]-w//2, self.pos[1]-h//2]))

	def update_plot(self):
		self.line.set_xdata(np.arange(len(self.radii)))
		self.line.set_ydata(self.radii)
		self.fig.canvas.draw()
		self.fig.canvas.flush_events()
		self.ax.set_title(f'{np.round(self.radii[-1], 1)}')

		if plot:
			self.update_plot()

##############################################################

pygame.init()
screen = pygame.display.set_mode([w,h])


walk = Walk(5)

running = True
while running:

	for event in pygame.event.get():
		if event.type == QUIT:
			running = False

	walk.update()

	pygame.display.flip()
	time.sleep(dt)


pygame.quit()