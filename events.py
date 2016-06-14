class tradeEvent:
	def __init__(self, instrument, units, side, trailingStop, takeProfit):
		self.instrument = instrument
		self.units = units
		self.order_type = "market"
		self.side = side
		self.trailingStop = trailingStop
		self.takeProfit = takeProfit