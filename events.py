class tradeEvent:
	def __init__(self, instrument, units, side, stopLoss, takeProfit):
		self.instrument = instrument
		self.units = units
		self.order_type = "market"
		self.side = side
		self.stopLoss = stopLoss
		self.takeProfit = takeProfit

class tradeEventLimit:
	def __init__(self, instrument, units, side, stopLoss, takeProfit, tradePrice, expiry, upperBound, lowerBound):
		self.instrument = instrument
		self.units = units
		self.order_type = "limit"
		self.side = side
		self.stopLoss = stopLoss
		self.takeProfit = takeProfit
		self.price = tradePrice
		self.expiry = expiry
		self.upperBound = upperBound
		self.lowerBound = lowerBound