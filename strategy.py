import Queue
import numpy as np

# strategy class
class Strategy:
	def __init__(self, prices, positions, priceQueue):
		#self.candles = prices.prices(pricePeriod)
		self.positions = positions
		#self.sd = prices.sd(self.candles)
		#self.avgPrice = prices.avg(candles)
		#self.doubleSd = 2 * sd
		#self.takeProfitIncrement = 0.0010
		#lastPrice = candles[len(candles)-1]['closeMid']	

	# if there is an open position, returns the type of position that is open
	# right now, we're trying to be only long or only short at any given time
	def checkOpen(self):
		for index in self.positions:
			if self.positions[index]:
				return index
			else:
				pass

	# take a queue, queue length and row, and load the row it into the queue, while offloading the earliest element
	def doQueue(self, queue, queueLength, row):
		price = (row['Buy'] + row['Sell']) / 2 # using the average of bid/ask as the historical price
		stats = self.queueStats(queue)
		array = {"price":price,"sd":stats["sd"],"avg":stats["avg"]}
		queue.put(array)
		if (queue.qsize() > queueLength):
			removed = queue.get()
		return queue

	def queueStats(self, currentQueue):
		stats = {"sd":0,"avg":0}
		qsize = currentQueue.qsize()
		queueAsList = list(currentQueue.queue)
		if (currentQueue.qsize() > 0):
			stats["sd"] = np.std(list(x["price"] for x in queueAsList))
			stats["avg"] = np.mean(list(x["price"] for x in queueAsList))
		return stats

	# bollinger strategy: purchase at the 2*sd with a take profit at the 20-period MA.
	# set a stop loss 1/2 sd beyond the 2*sd line. if the stop loss is triggered, enter
	# a trade as soon as the price crosses the sd line again. USE LIMIT ORDERS and perhaps
	# even do that instead of setting some price-watching thing.
	# Don't buy when the market is downtrending > x
	# Don't sell when the market is uptrending > y
	def bollinger(self, pricePeriod, lastPrice):

		tradeOpen = (self.checkOpen() is not None)

		#if tradeOpen:			# close conditions

		#elif not tradeOpen:		# open conditions


"""		if (lastPrice > (self.avgPrice + self.doublesd)):
			signal = "sell"
			trailingStop = 5
		elif (lastPrice < (self.avgPrice - self.doublesd)):
			signal = "buy"
			trailingStop = 5"""