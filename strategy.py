import Queue

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

	def doQueue(self, queue, queueLength, row):
		queue.put(row)
		if (queue.qsize() > queueLength):
			removed = queue.get()
		return queue

	# bollinger strategy: purchase at the 2*sd with a take profit at the 20-period MA.
	# set a stop loss 1/2 sd beyond the 2*sd line. if the stop loss is triggered, enter
	# a trade as soon as the price crosses the sd line again. USE LIMIT ORDERS and perhaps
	# even do that instead of setting some price-watching thing.
	# Don't buy when the market is downtrending > x
	# Don't sell when the market is uptrending > y
	def bollinger(self, pricePeriod, lastPrice):

		tradeOpen = (self.checkOpen() is not None)

		if tradeOpen:			# close conditions

		elif not tradeOpen:		# open conditions


"""		if (lastPrice > (self.avgPrice + self.doublesd)):
			signal = "sell"
			trailingStop = 5
		elif (lastPrice < (self.avgPrice - self.doublesd)):
			signal = "buy"
			trailingStop = 5"""