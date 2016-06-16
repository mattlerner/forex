import pandas

# backtest class
class Backtest:
	def __init__(self, filename, backtest, leverage, closeDictionary):
		self.filename = filename
		self.account = {"cash":backtest['capital'], "instruments":0}
		self.accountValue = self.account['cash'] + self.account['instruments']
		self.backtest = backtest
		self.closeDictionary=closeDictionary

	# parse datetimes
	def parse(self, datetime):
		for fmt in ('%Y-%m-%d %H:%M:%S.%f000000', '%Y-%m-%d %H:%M:%S'):
			try:
				return pandas.datetime.strptime(datetime, fmt)
			except ValueError:
				pass
		raise ValueError('no valid date format found')

	# resamble tick data
	def resample(self, resamplePeriod):
		df = pandas.read_csv(self.filename, parse_dates={'DateTime'}, index_col='DateTime', names=['Tid', 'Dealable', 'Pair', 'DateTime', 'Buy', 'Sell'], header=1, date_parser=self.parse)

		del df['Tid'] 
		del df['Dealable']
		del df['Pair']

		grouped_data = df.resample(resamplePeriod).ohlc()
		response = grouped_data.to_pickle(self.filename+'_'+resamplePeriod+'-OHLC.pkl')
		return response

	# read and return pickle as generator
	def readPickle(self):
		pickle = pandas.read_pickle(self.filename)
		return pickle.iterrows()

	# return positions
	def positions(self):
		return self.backtest['positions']

	# execeute simulated trade
	def executeTrade(self, side, row, stopLoss, takeProfit, leverage, closeDictionary):

		# pass if "buy" or "sell" is unspecified
		if not side:
			return

		cashSum = 0
		instrumentSum = 0

		#Some test assumptions here: Buy at high and sell at low to be conservative
		#highOrLow = {"buy":"high","sell":"low"}
		price = row[str.title(side)]
		#price = row[str.lower(side)][highOrLow[str.lower(side)]]
		tradeValue = self.backtest['units'] * price
		marginUsed = tradeValue / leverage
		self.backtest['takeProfit'] = takeProfit
		self.backtest['stopLoss'] = stopLoss

		if (self.backtest['positions'][self.closeDictionary[side]]):	# if we've passed side as "buy" and there's a "sell" open
			#trade is being closed
			cashSum = tradeValue / (price * leverage)
			instrumentSum = -1 * self.account['instruments']
			self.backtest['positions'][side] = 0
			self.backtest['positions'][closeDictionary[side]] = 0
			self.backtest['takeProfit'] = 0
			self.backtest['stopLoss'] = 0	
		else:	# if there is no trade open
			#trade is being opened
			cashSum = marginUsed * -1
			instrumentSum = tradeValue
			self.backtest['positions'][side] = price
			self.backtest['positions'][self.closeDictionary[side]] = 0

		self.account['cash'] = self.account['cash'] + cashSum
		self.account['instruments'] = self.account['instruments'] + instrumentSum

		#print "tradeValue ", tradeValue
		#print "cashSum ", cashSum
		#print "trade price ", price
		#print self.account
		#print self.positions()

	# check price to see if a stop-loss or take-profit event has been triggered for an open trade
	def checkPrice(self, row, openSide):
		highOrLow = {"buy":"high","sell":"low"}
		price = row[str.title(openSide)][highOrLow[openSide]]
		takeProfit = self.backtest['takeProfit']
		stopLoss = self.backtest['stopLoss']
		if (self.backtest['positions']['buy'] != 0):
			if (stopLoss > 0 and price <= stopLoss) or (takeProfit > 0 and price >= takeProfit):
				signal = "sell" 
			else:
				signal = ""
		elif (self.backtest['positions']['sell'] != 0):
			if (stopLoss > 0 and price >= stopLoss) or (takeProfit > 0 and price <= takeProfit):
				signal = "buy"
			else:
				signal = ""
		else:
			signal = ""
		return signal
