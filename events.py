class tradeEvent:
	def __init__(self, instrument, units, side, stopLoss, takeProfit):
		self.instrument = instrument
		self.units = units
		self.order_type = "market"
		self.side = side
		self.stopLoss = stopLoss
		self.takeProfit = takeProfit