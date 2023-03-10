import numpy as np
import time

class ProgressBar:
	''' Progress bar utility.'''
	def __init__(self, n_iter, width=50, text=""):
		''' To be called before the loop.'''
		self.grad = width/n_iter
		self.width = width
		self.n_iter = n_iter
		self.text = text
		print(text+ '[' + width*' ' + ']', end="\r")

	def update(self, i):
		''' Called at each iteration.
			i for the iteration number.
		'''
		part1 = int(self.grad*i)
		part2 = self.width - part1 - 1
		perc = np.round(100*(i+1)/self.n_iter, 2)
		print(self.text + " {:0.2f}% ".format(perc) + '[' + part1 * "#" + part2*' ' + ']', end="\r")
		time.sleep(0.01)

	def end(self, text=""):
		print()
		print(text)