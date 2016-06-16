import matplotlib.pyplot as plt
import time

class doFigure(object):

	def __init__(self):
		self.fig = plt.figure()
		plt.axis([0,1000,0,2])
		self.x = list()
		self.y = list()
		plt.ion()

	def drawGraph(self, xvalue, yvalue):
		print xvalue
		print yvalue
		self.x.append(xvalue)
		self.y.append(yvalue)
		plt.scatter(xvalue, yvalue)
		plt.draw()
		plt.pause(0.001)