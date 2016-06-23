import Queue
import numpy as np
from plot import doFigure

# strategy class
class Strategy:
	def __init__(self, prices, positions, priceQueue):
		#self.candles = prices.prices(pricePeriod)
		self.positions = positions
		self.i = 0
		self.strategyVariables = {}
		#self.sd = prices.sd(self.candles)
		#self.avgPrice = prices.avg(candles)
		#self.doubleSd = 2 * sd
		#self.takeProfitIncrement = 0.0010
		#lastPrice = candles[len(candles)-1]['closeMid']	

	# take a queue, queue length and row, and load the row it into the queue, while offloading the earliest element
	def doQueue(self, queue, queueLength, row):
		price = (row['Buy'] + row['Sell']) / 2 # using the average of bid/ask as the historical price
		stats = self.queueStats(queue)
		array = {"price":price,"sd":stats["sd"],"avg":stats["avg"]}
		queue.put(array)
		if (queue.qsize() > queueLength):
			removed = queue.get()
		return queue

	# return standard deviation and average of a queue
	def queueStats(self, currentQueue):
		stats = {"sd":0,"avg":0}
		qsize = currentQueue.qsize()
		queueAsList = list(currentQueue.queue)
		if (currentQueue.qsize() > 0):
			stats["sd"] = np.std(list(x["price"] for x in queueAsList))
			stats["avg"] = np.mean(list(x["price"] for x in queueAsList))
		return stats

	# return very last item in the queue
	def returnLastQueueItem(self, currentQueue):
		queueAsList = list(currentQueue.queue)
		return queueAsList[len(queueAsList) - 1]

	# return very first item in the queue
	def returnFirstQueueItem(self, currentQueue):
		queueAsList=list(currentQueue.queue)
		return queueAsList[0]

	# bollinger strategy: purchase at the 2*sd with a take profit at the 20-period MA.
	# set a stop loss 1/2 sd beyond the 2*sd line. if the stop loss is triggered, enter
	# a trade as soon as the price crosses the sd line again. USE LIMIT ORDERS and perhaps
	# even do that instead of setting some price-watching thing.
	# Don't buy when the market is downtrending > x
	# Don't sell when the market is uptrending > y
	# reverse trade if stoploss is triggered
	def bollinger(self, lastPriceArray, currentQueue, backtest, checkOpen, account, display):
		lastPrice = (lastPriceArray["Buy"] + lastPriceArray["Sell"]) / 2
		backtest["units"] = (2000 / lastPrice) * backtest["leverage"]
		signal = ""
		stopLoss = 0
		takeProfit = 0
		signalArray = {"signal":"","stopLoss":0,"takeProfit":0}
		tradeOpen = (checkOpen is not None)
		lastItem = self.returnLastQueueItem(currentQueue)
		firstItem = self.returnFirstQueueItem(currentQueue)
		upperBand = lastItem["avg"] + (2 * lastItem["sd"])
		lowerBand = lastItem["avg"] - (2 * lastItem["sd"])
		#print "upperBand: ", upperBand
		#print "lowerBand: ", lowerBand
		#print "avg: ", lastItem["avg"]
		#print "lastItem SD: ", lastItem["sd"]
		uptrend = (1 if lastPrice - firstItem["price"] > (2*lastItem["sd"]) else 0)
		downtrend = (1 if firstItem["price"] - lastPrice > (2*lastItem["sd"]) else 0)
		display.drawGraph(self.i, upperBand, lastPrice, lowerBand)
		self.i = self.i + 1

		if not tradeOpen:	# open conditions
			if (lastPrice > upperBand):# or backtest["lastStopLoss"] == "sell"):# and not uptrend):
				signal = "sell"
				stopLoss = lastPrice + (1.5*lastItem["sd"])
				takeProfit = lastItem["avg"] - (2*lastItem["sd"])
				#takeProfit = lowerBand
			elif (lastPrice < lowerBand):# or backtest["lastStopLoss"] == "buy"):# and not downtrend):
				signal = "buy"
				stopLoss = lastPrice - (1.5*lastItem["sd"])
				takeProfit = lastItem["avg"] + (2*lastItem["sd"])
				#takeProfit = upperBand
		backtest["lastStopLoss"] = ""

		signalArray = {"signal":signal,"stopLoss":stopLoss,"takeProfit":takeProfit}
		return signalArray