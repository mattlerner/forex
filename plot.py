import matplotlib.pyplot as plt
import time

class doFigure(object):

	def __init__(self):
		fig = plt.figure()
		plt.axis([0,1000,0,2])
		self.arrayLine = {"sell":"r","buy":"g"}
		self.priceX = list()
		self.priceY = list()
		self.upperY = list()
		self.lowerY = list()
		plt.show()
		plt.ion()
		plt.close(fig)

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
		plt.pause(0.0001)

	def drawCashGraph(self, accountXvalue, accountYvalue):
		self.priceX.append(accountXvalue)
		self.priceY.append(accountYvalue)
		plt.plot(accountXvalue, accountYvalue, '.b-')
		plt.draw()
		plt.show()
		plt.pause(0.0001)

	def drawLine(self, i, side):
		plt.axvline(x=i, linewidth=1, color=self.arrayLine[side])

	def drawScatter(self, priceXvalue, priceYvalue, lowerYvalue, upperYvalue):
		self.priceX.append(priceXvalue)
		self.priceY.append(priceYvalue)
		self.upperY.append(upperYvalue)
		self.lowerY.append(lowerYvalue)
		plt.scatter(priceXvalue, upperYvalue, color='red')
		plt.scatter(priceXvalue, priceYvalue, color='blue')
		plt.scatter(priceXvalue, lowerYvalue, color='green')
		plt.draw()
		plt.pause(0.0001)

	def saveFigure(self, filepath):
		fig = plt.gcf()
		fig.savefig(filepath)