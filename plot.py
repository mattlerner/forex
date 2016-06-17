import matplotlib.pyplot as plt
import time

class doFigure(object):

	def __init__(self):
		#self.fig = plt.figure(1)
		plt.axis([0,1000,0,2])
		self.priceX = list()
		self.priceY = list()
		self.upperY = list()
		self.lowerY = list()
		plt.show()
		plt.ion()

	def drawGraph(self, priceXvalue, priceYvalue, lowerYvalue, upperYvalue):
		self.priceX.append(priceXvalue)
		self.priceY.append(priceYvalue)
		self.upperY.append(upperYvalue)
		self.lowerY.append(lowerYvalue)
		plt.plot(priceXvalue, upperYvalue, '.r-')
		plt.plot(priceXvalue, priceYvalue, '.b-')
		plt.plot(priceXvalue, lowerYvalue, '.g-')
		plt.draw()
		plt.show()
		plt.pause(0.001)

	def drawScatter(self, priceXvalue, priceYvalue, lowerYvalue, upperYvalue):
		self.priceX.append(priceXvalue)
		self.priceY.append(priceYvalue)
		self.upperY.append(upperYvalue)
		self.lowerY.append(lowerYvalue)
		plt.scatter(priceXvalue, upperYvalue, color='red')
		plt.scatter(priceXvalue, priceYvalue, color='blue')
		plt.scatter(priceXvalue, lowerYvalue, color='green')
		plt.draw()
		plt.pause(0.001)