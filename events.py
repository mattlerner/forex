class tradeEvent:
	def __init__(self, instrument, units, side, stopLoss, takeProfit):
		self.instrument = instrument
		self.units = units
		self.order_type = "market"
		self.side = side
		self.stopLoss = stopLoss
		self.takeProfit = takeProfit

class tradeEventLimit:
	def __init__(self, instrument, units, side, stopLoss, takeProfit, lastPrice, expiry):
		self.instrument = instrument
		self.units = units
		self.order_type = "limit"
		self.side = side
		self.stopLoss = stopLoss
		self.takeProfit = takeProfit
		self.price = lastPrice
		self.expiry = expiry