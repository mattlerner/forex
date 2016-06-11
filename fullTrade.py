import Queue
import time
import warnings
from settings import STREAM_DOMAIN, API_DOMAIN, ACCESS_TOKEN, ACCOUNT_ID
from priceStream import StreamingForexPrices
import httplib
import json
import numpy as np
import httplib
import urllib
import pandas

#GLOBALS
signal = ""
openPositions = {"buy": 0, "sell":0}

#Things to change
instrument = "EUR_USD" 					# what instrument are we trading?
longPeriod = 50							# what is the period of our long moving average?
shortPeriod = 5							# what is the period of our short moving average?
closeInterval = 300
stopLoss = 0.01 						# default stoploss ticks
units = 80000 							# default units
leverage = 50 							# default leverage

#By strategy

#MA
shortQueue = Queue.Queue()				# set up short queue
longQueue = Queue.Queue()				# set up long queue
lastTopMA = ""							# "short" or "long" whatever the top MA was the last tick

#Bollinger
timeSinceOpen = 0
closeDictionary = {"buy": "sell", "sell": "buy"}
takeProfitArray = {"buy": 1, "sell": -1}
sleepPlus = 0



class Execution(object):
	def __init__(self, domain, access_token, account_id):
		self.domain = domain
		self.access_token = access_token
		self.account_id = account_id
		self.conn = self.obtain_connection()

	def obtain_connection(self):
		return httplib.HTTPSConnection(self.domain)

	def execute_order(self, event):
		headers = {
			"Content-Type": "application/x-www-form-urlencoded",
			"Authorization": "Bearer " + self.access_token
		}
		params = urllib.urlencode({
			"instrument" : event.instrument,
			"units" : event.units,
			"type" : event.order_type,
			"side" : event.side,
			"trailingStop": event.trailingStop,
			"takeProfit": event.takeProfit
		})
		self.conn.request(
			"POST",
			"/v1/accounts/%s/orders" % str(self.account_id),
			params, headers
		)
		response = json.loads(self.conn.getresponse().read())
		print response
		return response

class tradeEvent:
	def __init__(self, instrument, units, side, trailingStop, takeProfit):
		self.instrument = instrument
		self.units = units
		self.order_type = "market"
		self.side = side
		self.trailingStop = trailingStop
		self.takeProfit = takeProfit

class restConnect(object):
	def __init__(self, domain, token, id, instrument, granularity):
		self.domain = domain
		self.access_token = token
		self.account_id = id
		self.instrument = instrument
		self.granularity = granularity
		self.cur_bid = None
		self.cur_ask = None

	def prices(self, period):
		conn = httplib.HTTPSConnection(self.domain)
		url = ''.join(["/v1/candles?count=", str(period + 1), "&instrument=", self.instrument, "&granularity=", str(self.granularity), "&candleFormat=midpoint"])
		conn.request("GET",url)
		resp = json.loads(conn.getresponse().read())
		candles = resp['candles']
		return candles

	def positions(self):
		conn = httplib.HTTPSConnection(self.domain)
		headers = {
			"Content-Type": "application/x-www-form-urlencoded",
			"Authorization": "Bearer " + self.access_token
		}
		params = urllib.urlencode({
			"instrument" : instrument
		})
		conn.request(
			"GET",
			"/v1/accounts/%s/positions" % str(self.account_id),
			params, headers
		)
		response = json.loads(conn.getresponse().read())
		positions = {"buy":[],"sell":[]}
		for x in response['positions']:
			y = x['side']
			positions[y].append(x)
		return positions

	def avg(self, candles):
		priceArray = map(lambda x: x['openMid'], candles)
		priceAvg = np.average(priceArray)
		return priceAvg

	def sd(self, candles):
		priceArray = map(lambda x: x['openMid'], candles)
		priceSd = np.std(priceArray)
		return priceSd

class Strategy:
	def __init__(self, prices, pricePeriod, lastPrice):
		self.candles = prices.prices(pricePeriod)
		self.positions = prices.positions()
		self.sd = prices.sd(self.candles)
		self.avgPrice = prices.avg(candles)
		self.doubleSd = 2 * sd
		self.takeProfitIncrement = 0.0010
		lastPrice = candles[len(candles)-1]['closeMid']	
		
	def bollinger(self):

		print positions

		if (lastPrice > (avgPrice + doublesd)):
			signal = "sell"
			trailingStop = 5
		elif (lastPrice < (avgPrice - doublesd)):
			signal = "buy"
			trailingStop = 5


class backTest:
	def __init__(self, filename, resamplePeriod):
		self.filename = filename
		self.resamplePeriod = resamplePeriod
		df = pandas.read_csv(self.filename, parse_dates={'DateTime'}, index_col='DateTime', names=['Tid', 'Dealable', 'Pair', 'DateTime', 'Buy', 'Sell'], header=1, date_parser=self.parse)
		print df
		#grouped_data = df.resample('15Min', how='ohlc')
		#print grouped_data

	def parse(self, datetime):
		for fmt in ('%Y-%m-%d %H:%M:%S.%f000000', '%Y-%m-%d %H:%M:%S'):
			try:
				return pandas.datetime.strptime(datetime, fmt)
			except ValueError:
				pass
		raise ValueError('no valid date format found')


if __name__ == "__main__":

	backTest = backTest("historical/EUR_USD_Week1.csv","1Min")
	print backTest
	exit()

	while True:

		signal = ""

		prices = restConnect(API_DOMAIN,ACCESS_TOKEN,ACCOUNT_ID,instrument,"M1")

		positions = prices.positions()
		print positions

		candles = prices.prices(20)
		avgPrice = prices.avg(candles)
		sd = prices.sd(candles)
		doublesd = 2 * sd
		lastPrice = candles[len(candles)-1]['closeMid']
		takeProfitIncrement = 0.0010

		"""strategy = Strategy(candles)
		signal = strategy.bollinger(prices)"""
		print "Last price: ", str(lastPrice)
		print "Average price: ", str(avgPrice)
		print "Double SD: ", str(doublesd)
		print "Current distance from Double SD (topside): ", str(lastPrice - (avgPrice + doublesd))
		print "Current distance from Double SD (bottomsize): ", str(lastPrice - (avgPrice - doublesd))

		if (lastPrice > (avgPrice + doublesd)):
			signal = "sell"
			trailingStop = 5
		elif (lastPrice < (avgPrice - doublesd)):
			signal = "buy"
			trailingStop = 5

		# execute whatever signals there are
		if signal:
			if (not positions[signal]):
				takeProfitFull = lastPrice + (takeProfitIncrement * takeProfitArray[signal])
				event = tradeEvent(instrument, units, signal, trailingStop, takeProfitFull)
				execution = Execution(API_DOMAIN, ACCESS_TOKEN, ACCOUNT_ID)
				response = execution.execute_order(event)
		else:
			print ""	#no signal

		time.sleep(1)