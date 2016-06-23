import pandas


def groupResample(year, startMonth, endMonth, resamplePeriod, currency):
	currentMonth = startMonth
	currentWeek = 1
	ind = True
	arrayOfDataframes = []
	while (ind):
		filename = "historical/" + currency + "_" + str(year) + "_" + str(currentMonth) + "-Week" + str(currentWeek) + ".csv"

		try:
			df = pandas.read_csv(filename, parse_dates={'DateTime'}, index_col='DateTime', names=['Tid', 'Dealable', 'Pair', 'DateTime', 'Buy', 'Sell'], header=1, date_parser=parse)
			print filename
		except:
			ind = (currentMonth != endMonth)
			currentMonth = currentMonth + 1
			currentWeek = 1
			continue

		del df['Tid'] 
		del df['Dealable']
		del df['Pair']

		grouped_data = df.resample(resamplePeriod).mean()
		arrayOfDataframes.append(grouped_data)
		currentWeek = currentWeek + 1
	final = pandas.concat(arrayOfDataframes)
	response = final.to_pickle("historical/"+currency+"_"+str(year)+"_"+str(startMonth)+"_through_"+str(endMonth)+".pkl")
	return response

def parse(datetime):
	for fmt in ('%Y-%m-%d %H:%M:%S.%f000000', '%Y-%m-%d %H:%M:%S'):
		try:
			return pandas.datetime.strptime(datetime, fmt)
		except ValueError:
			pass
	raise ValueError('no valid date format found')

# backtest class
class Backtest:
	def __init__(self, filename, backtest, leverage, closeDictionary, positions):
		self.filename = filename
		self.account = {"cash":backtest['capital'], "instruments":0}
		self.accountValue = self.account['cash'] + self.account['instruments']
		self.backtest = backtest
		self.positions = positions
		self.closeDictionary=closeDictionary

	# parse datetimes
	def parse(self, datetime):
		for fmt in ('%Y-%m-%d %H:%M:%S.%f000000', '%Y-%m-%d %H:%M:%S'):
			try:
				return pandas.datetime.strptime(datetime, fmt)
			except ValueError:
				pass
		raise ValueError('no valid date format found')

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

	# resamble tick data
	def resample(self, resamplePeriod):
		df = pandas.read_csv(self.filename, parse_dates={'DateTime'}, index_col='DateTime', names=['Tid', 'Dealable', 'Pair', 'DateTime', 'Buy', 'Sell'], header=1, date_parser=self.parse)

		del df['Tid'] 
		del df['Dealable']
		del df['Pair']

		grouped_data = df.resample(resamplePeriod).mean()
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
		if not side:
			return

		tradeValueMultiplier = {"buy":1,"sell":-1}
		cashSum = 0
		instrumentSum = 0

		price = (row['Buy'] + row['Sell']) / 2

		checkOpen = self.checkOpen()
		if (checkOpen is not None):
			print "Trade Closed!"
			multiplier = tradeValueMultiplier[checkOpen]
			positionPrice = self.positions[checkOpen]
			pipDifference = (price - positionPrice) * multiplier
			cashValue = (self.account["instruments"] / leverage)

			instrumentDifference = -1 * self.account['instruments']
			cashDifference = cashValue + (pipDifference * self.backtest['units'])
		else:
			print "Trade Opened!"
			instrumentDifference = (self.backtest['units'] * price)
			cashDifference = -1 * (instrumentDifference) / leverage

		print "*** TRADE ***"
		print "Side: ", side
		print "Price: ", price
		print "instrumentDifference: ", instrumentDifference
		print "cashDifference: ", cashDifference

		self.backtest['takeProfit'] = takeProfit
		self.backtest['stopLoss'] = stopLoss
		self.account['instruments'] = self.account['instruments'] + instrumentDifference
		self.account['cash'] = self.account['cash'] + cashDifference

		if (self.backtest['positions'][self.closeDictionary[side]]):	# if we've passed side as "buy" and there's a "sell" open
			#trade is being closed
			self.backtest['positions'][side] = 0
			self.backtest['positions'][closeDictionary[side]] = 0
		else:	# if there is no trade open
			#trade is being opened
			self.backtest['positions'][side] = price
			self.backtest['positions'][self.closeDictionary[side]] = 0
		#print self.account
		#print self.backtest['positions']

	# check price to see if a stop-loss or take-profit event has been triggered for an open trade
	def checkPrice(self, row, openSide):
		price = (row['Buy'] + row['Sell']) / 2
		self.account["instruments"] = self.backtest["units"] * price;
		takeProfit = self.backtest['takeProfit']
		stopLoss = self.backtest['stopLoss']
		if (self.backtest['positions']['buy'] != 0):
			if (stopLoss > 0 and price <= stopLoss):
				print "stoploss!"
				self.backtest["lastStopLoss"] = "sell"
				signal = "sell"
			elif (takeProfit > 0 and price >= takeProfit):
				print "takeprofit!"
				signal = "sell" 
			else:
				signal = ""
		elif (self.backtest['positions']['sell'] != 0):
			if (stopLoss > 0 and price >= stopLoss):
				print "stoploss!"
				self.backtest["lastStopLoss"] = "buy"
				signal = "buy"
			elif (takeProfit > 0 and price <= takeProfit):
				print "takeprofit!"
				signal = "buy"
			else:
				signal = ""
		else:
			signal = ""
		returnArray = {"signal":signal,"stopLoss":0,"takeProfit":0}
		return returnArray
