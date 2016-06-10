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

instrument = "EUR_USD" 					# what instrument are we trading?
longPeriod = 50							# what is the period of our long moving average?
shortPeriod = 5							# what is the period of our short moving average?
closeInterval = 300
shortQueue = Queue.Queue()				# set up short queue
longQueue = Queue.Queue()				# set up long queue
stopLoss = 0.01 						# default stoploss ticks
units = 80000 							# default units
leverage = 50 							# default leverage
openPositions = {"buy": 0, "sell":0}					
nextSignal = []							# this will hold signals - ONE AT A TIME
lastTopMA = ""							# "short" or "long" whatever the top MA was the last tick
signal = ""
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


if __name__ == "__main__":

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

				if (response["tradesClosed"]):
					if (response["price"] < openPositions[signal]):
						sleepPlus = 300
				else:
					openPositions[signal] = response["price"]
		else:
			print ""	#no signal

		time.sleep(1+sleepPlus)
		sleepPlus = 0

"""
if __name__ == "__main__":

	prices = restConnect(API_DOMAIN,ACCESS_TOKEN,ACCOUNT_ID,instrument,"M1")
	print prices.sdDist(20)
	exit()

	while True:

		signal = ""

		prices = restConnect(API_DOMAIN,ACCESS_TOKEN,ACCOUNT_ID,instrument,"M1")

		#begin cutout

		shortMA = prices.avg(5)
		longMA = prices.avg(50)

		# what is the current MA situation?
		if (shortMA > longMA):
			currentTopMA = "short"
		elif (longMA > shortMA):
			currentTopMA = "long"
		else:
			currentTopMA = "equal"

		print "Short MA: " + str(shortMA)
		print "Long MA: " + str(longMA)
		print "Current Top MA: " + currentTopMA
		print "Last Top MA: " + lastTopMA + "\n"

		if (not openPosition):
			if (currentTopMA == "short" and lastTopMA == "long"):
				signal = "buy"
				openPosition = signal
			elif (currentTopMA == "long" and lastTopMA == "short"):
				signal = "sell"
				openPosition = signal
			else:
				signal = ""
		else:
			print "Time since open: " + str(timeSinceOpen) + "\n"
			timeSinceOpen += 1
			if (timeSinceOpen >= closeInterval):
				signal = closeDictionary[openPosition]
				timeSinceOpen = 0
				openPosition = ""
			else:
				signal = ""

		#end cutout

		# execute whatever signals there are
		if signal:
			event = tradeEvent(instrument, units, signal)
			execution = Execution(API_DOMAIN, ACCESS_TOKEN, ACCOUNT_ID)
			response = execution.execute_order(event)
			print response
		else:
			print ""	#no signal

		# set at the end of the loop: what was the MA situation at the last loop run?
		lastTopMA = currentTopMA #DON'T FORGET THIS

		time.sleep(1)
		"""