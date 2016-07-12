import Queue
import numpy as np
from plot import doFigure
from scipy import stats

# strategy class
class Strategy:
	def __init__(self, positions, priceQueue, backtestSettings, strategySettings):
		#self.candles = prices.prices(pricePeriod)
		self.positions = positions
		self.i = 0
		self.wait = 0
		self.strategySettings = strategySettings
		self.nextOrder = "";

	# if there is an open position, returns the type of position that is open
	# right now, we're trying to be only long or only short at any given time
	def checkOpen(self):
		returnVar = None
		for index in self.positions:
			if self.positions[index]:
				returnVar = index
			else:
				pass
		return returnVar

	# take a queue, queue length and row, and load the row it into the queue, while offloading the earliest element
	def doQueue(self, queue, queueLength, row):
		price = (row['Buy'] + row['Sell']) / 2 # using the average of bid/ask as the historical price
		spread = abs(row['Buy'] - row['Sell'])
		stats = self.queueStats(queue)
		#print "avgSd: ", stats["avgSd"]
		array = {"price":price,"sd":stats["sd"],"avg":stats["avg"],"spread":spread,"avgSd":stats["avgSd"]}
		queue.put(array)
		if (queue.qsize() > queueLength):
			removed = queue.get()
		return queue

	# return standard deviation and average of a queue
	def queueStats(self, currentQueue):
		stats = {"sd":0,"avg":0,"avgSd":0}
		qsize = currentQueue.qsize()
		queueAsList = list(currentQueue.queue)
		if (currentQueue.qsize() > 0):
			stats["sd"] = np.std(list(x["price"] for x in queueAsList))
			stats["avg"] = np.mean(list(x["price"] for x in queueAsList))
			stats["avgSd"] = np.std(list(x["avg"] for x in queueAsList))
			#print stats["avg"]
		return stats

	# return very last item in the queue
	def returnLastQueueItem(self, currentQueue):
		queueAsList = list(currentQueue.queue)
		return queueAsList[len(queueAsList) - 1]	

	# return very first item in the queue
	def returnFirstQueueItem(self, currentQueue):
		queueAsList=list(currentQueue.queue)
		return queueAsList[0]

	def returnQueueItemByIndex(self, currentQueue, index):
		queueAsList=list(currentQueue.queue)
		try:
			toReturn = queueAsList[index]
		except:
			toReturn =  {"price":0,"sd":0,"avg":0}
		return toReturn

	def checkTrend(self, currentQueue):
		queueAsList=list(x["price"] for x in list(currentQueue.queue))
		#print "checkTrend: ", np.mean(np.diff(queueAsList))
		return np.mean(np.diff(queueAsList))

	def returnQueueRange(self, currentQueue):
		maxVal=np.amax(list(x["avg"] for x in list(currentQueue.queue)))
		minVal=	np.amin(list(x["avg"] for x in list(currentQueue.queue)))	
		return abs(maxVal - minVal)

	# bollinger strategy: purchase at the 2*sd with a take profit at the 20-period MA.
	# set a stop loss 1/2 sd beyond the 2*sd line. if the stop loss is triggered, enter
	# a trade as soon as the price crosses the sd line again. USE LIMIT ORDERS and perhaps
	# even do that instead of setting some price-watching thing.
	# Don't buy when the market is downtrending > x
	# Don't sell when the market is uptrending > y
	# reverse trade if stoploss is triggered
#	def bollinger(self, lastPriceArray, currentQueue, longQueue, settings, tradeOpen, display, backtest):
	def bollinger(self, lastPriceArray, currentQueue, longQueue, settings, tradeOpen):
		lastPrice = (lastPriceArray["Buy"] + lastPriceArray["Sell"]) / 2
		settings["units"] = (settings["tradeAmount"] / lastPrice) *	 settings["leverage"]
		signal = ""
		stopLoss = 0
		takeProfit = 0
		signalArray = {"signal":"","stopLoss":0,"takeProfit":0}
		lastItem = self.returnLastQueueItem(currentQueue)
		firstItem = self.returnFirstQueueItem(currentQueue)
		upperBand = lastItem["avg"] + (2 * lastItem["sd"])
		lowerBand = lastItem["avg"] - (2 * lastItem["sd"])
		self.upperBand = upperBand
		self.lowerBand = lowerBand
		self.movingAverage = lastItem["avg"]
		self.sd = lastItem["sd"]
		#print "upperBand: ", upperBand
		#print "lowerBand: ", lowerBand
		#print "avg: ", lastItem["avg"]
		#print "lastItem SD: ", lastItem["sd"]
		uptrend = (1 if lastItem["avg"] - firstItem["avg"] > (1*lastItem["sd"]) else 0)
		downtrend = (1 if firstItem["avg"] - lastItem["avg"] > (1*lastItem["sd"]) else 0)
		spreadOkay = (1 if lastItem["spread"] < 0.000033 else 0)
		display.drawGraph(self.i, upperBand, lastPrice, lowerBand)
		self.i = self.i + 1

		if not tradeOpen:	# open conditions
			if (lastPrice >= upperBand and not uptrend and spreadOkay):# or backtest["lastStopLoss"] == "sell"):# and not uptrend):
				signal = "sell"
				stopLoss = lastPrice + (1.5*lastItem["sd"])
				takeProfit = lastItem["avg"]# - lastItem["sd"]# - (2*lastItem["sd"])
			elif (lastPrice <= lowerBand and not downtrend and spreadOkay):# or backtest["lastStopLoss"] == "buy"):# and not downtrend):
				signal = "buy"
				stopLoss = lastPrice - (1.5*lastItem["sd"])
				takeProfit = lastItem["avg"]# + lastItem["sd"]# + (2*lastItem["sd"])

		# BACKTEST ONLY
		if tradeOpen:
			signal = backtest.checkPrice(lastPriceArray, backtest.checkOpen())	# also adjust open positions

		signalArray = {"signal":signal,"stopLoss":stopLoss,"takeProfit":takeProfit}

		if signal:
			print signalArray
			display.drawLine(self.i, signal)

		return signalArray

	# maCrossStrategy
	def maCross(self, lastPriceArray, currentQueue, longQueue, settings, tradeOpen):
		lastPrice = (lastPriceArray["Buy"] + lastPriceArray["Sell"]) / 2
		#settings["units"] = (settings["tradeAmount"] / lastPrice) *	 settings["leverage"]
		signal = ""
		stopLoss = 0
		takeProfit = 0
		signalArray = {"signal":"","stopLoss":0,"takeProfit":0}
		lastItem = self.returnLastQueueItem(currentQueue)
		lastItemLongQueue = self.returnLastQueueItem(longQueue)
		firstItem = self.returnFirstQueueItem(currentQueue)
		twoBackShort = self.returnQueueItemByIndex(currentQueue, -2)
		twoBackLong = self.returnQueueItemByIndex(longQueue, -2)
		self.movingAverage = lastItem["avg"]
		self.sd = lastItem["sd"]
		#print "Range: ", self.returnQueueRange(longQueue)
		lowRange = (1 if self.returnQueueRange(longQueue) < 0.0025 else 0)
		spreadOkay = (1 if lastItem["spread"] < 0.00004 else 0)
		uptrend = (1 if lastItemLongQueue["avg"] - twoBackLong["avg"] > (1*twoBackLong["sd"]) else 0)
		downtrend = (1 if twoBackLong["avg"] - lastItemLongQueue["avg"] > (1*twoBackLong["sd"]) else 0)
		lowVolatility = (1 if lastItemLongQueue["avgSd"] < 0.00065 else 0)
		#display.drawGraph(self.i, lastItemLongQueue["avg"], lastItem["avg"], lastPrice)
		self.i = self.i + 1

		if not tradeOpen:	# open conditions
			#settings["tradeAmount"] = backtest.account["cash"] * 0.2
			if (lastItem["avg"] < lastItemLongQueue["avg"] and twoBackShort["avg"] > twoBackLong["avg"] and (lowVolatility and spreadOkay and not uptrend and lowRange)):# or backtest["lastStopLoss"] == "sell"):# and not uptrend):
				signal = "sell"
				stopLoss = lastPrice + (4*lastItem["sd"])#(0.5*lastItem["sd"])
				takeProfit = lastItem["avg"] - (8*lastItem["sd"])
			elif (lastItem["avg"] > lastItemLongQueue["avg"] and twoBackShort["avg"] < twoBackLong["avg"] and (lowVolatility and spreadOkay and not downtrend and lowRange)):# or backtest["lastStopLoss"] == "buy"):# and not downtrend):
				signal = "buy"
				stopLoss = lastPrice - (4*lastItem["sd"])#(0.5*lastItem["sd"])
				takeProfit = lastItem["avg"] + (8*lastItem["sd"])

		# BACKTEST ONLY
		#if tradeOpen:
		#	signal = backtest.checkPrice(lastPriceArray, backtest.checkOpen())	# also adjust open positions

		signalArray = {"signal":signal,"stopLoss":round(stopLoss,5),"takeProfit":round(takeProfit,5),"lastPrice":round(lastPrice,5)}

		print "signalArray: ", signalArray

		if signal:
			print ""
			#display.drawLine(self.i, signal)

		return signalArray

"""	# maCrossStrategy - $7000 profit in 2mo
	def maCross(self, lastPriceArray, currentQueue, longQueue, settings, tradeOpen, display, backtest):
		lastPrice = (lastPriceArray["Buy"] + lastPriceArray["Sell"]) / 2
		settings["units"] = (settings["tradeAmount"] / lastPrice) *	 settings["leverage"]
		signal = ""
		stopLoss = 0
		takeProfit = 0
		signalArray = {"signal":"","stopLoss":0,"takeProfit":0}
		lastItem = self.returnLastQueueItem(currentQueue)
		lastItemLongQueue = self.returnLastQueueItem(longQueue)
		firstItem = self.returnFirstQueueItem(currentQueue)
		twoBackShort = self.returnQueueItemByIndex(currentQueue, -2)
		twoBackLong = self.returnQueueItemByIndex(longQueue, -2)
		self.movingAverage = lastItem["avg"]
		self.sd = lastItem["sd"]
		print "Range: ", self.returnQueueRange(longQueue)
		lowRange = (1 if self.returnQueueRange(longQueue) < 0.0025 else 0)
		spreadOkay = (1 if lastItem["spread"] < 0.00004 else 0)
		uptrend = (1 if lastItemLongQueue["avg"] - twoBackLong["avg"] > (1*twoBackLong["sd"]) else 0)
		downtrend = (1 if twoBackLong["avg"] - lastItemLongQueue["avg"] > (1*twoBackLong["sd"]) else 0)
		lowVolatility = (1 if lastItemLongQueue["avgSd"] < 0.00065 else 0)
		#display.drawGraph(self.i, lastItemLongQueue["avg"], lastItem["avg"], lastPrice)
		self.i = self.i + 1

		if not tradeOpen:	# open conditions
			if (lastItem["avg"] < lastItemLongQueue["avg"] and twoBackShort["avg"] > twoBackLong["avg"] and (lowVolatility and spreadOkay and not uptrend) or lowRange):# or backtest["lastStopLoss"] == "sell"):# and not uptrend):
				signal = "sell"
				stopLoss = lastPrice + (0.5*lastItem["sd"])
				takeProfit = lastItem["avg"] - (4*lastItem["sd"])
			elif (lastItem["avg"] > lastItemLongQueue["avg"] and twoBackShort["avg"] < twoBackLong["avg"] and (lowVolatility and spreadOkay and not downtrend) or lowRange):# or backtest["lastStopLoss"] == "buy"):# and not downtrend):
				signal = "buy"
				stopLoss = lastPrice - (0.5*lastItem["sd"])
				takeProfit = lastItem["avg"] + (4*lastItem["sd"])

		# BACKTEST ONLY
		if tradeOpen:
			signal = backtest.checkPrice(lastPriceArray, backtest.checkOpen())	# also adjust open positions

		signalArray = {"signal":signal,"stopLoss":stopLoss,"takeProfit":takeProfit}

		if signal:
			print signalArray
			#display.drawLine(self.i, signal)

		return signalArray"""