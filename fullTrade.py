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
from plot import doFigure
from execution import Execution
from backtest import Backtest, groupResample
from events import tradeEvent
from strategy import Strategy

# TOGGLES
backtestIndicator = True # are we backtesting?
liveIndicator = False	# are we trading live?

# BACKTEST STARTING VARIABLES
backtestSettings = {
	"capital": 10000,
	"tradeAmount": 2000,
	"stopLoss": 0,
	"takeProfit": 0,
	"leverage":50,
	"lastStopLoss":""
}

# LIVE STARTING VARIABLES
# NOTE: Make sure these match the actual state of the account!
# At some point, pull them from the account where possible
backtestSettings = {
	"capital": 10000,
	"tradeAmount": 2000,
	"stopLoss": 0,
	"takeProfit": 0,
	"leverage":50,
	"lastStopLoss":""
}

backtestPositions =	{"buy": 0, "sell": 0}

# STORE ALL STRATEGY SETTINGS HERE
strategySettings = {
	"queuePeriod":50
}

#GLOBALS
signal = ""

#Things to change
instrument = "EUR_USD" 					# what instrument are we trading?
longPeriod = 50							# what is the period of our long moving average?
shortPeriod = 5							# what is the period of our short moving average?
closeInterval = 300
stopLoss = 0.01 						# default stoploss ticks
leverage = 50 							# default leverage

#By strategy

#MA
shortQueue = Queue.Queue()				# set up short queue
longQueue = Queue.Queue()				# set up long queue
lastTopMA = ""							# "short" or "long" whatever the top MA was the last tick

#Bollinger
timeSinceOpen = 0
takeProfitArray = {"buy": 1, "sell": -1}
sleepPlus = 0

#Declare the queue that will store prices
priceQueue = Queue.Queue()

#For backtest: Instantiate matPlotLib figure
display = doFigure()

if __name__ == "__main__":
	if backtestIndicator:								# conduct backtest
		print " *** BACKTEST *** "
		#CONVERT DATA TO PICKLE
		#backTest = Backtest("historical/EUR_USD_Week3.csv",backtestSettings,leverage,closeDictionary,backtestSettings['positions'])
		#output = backTest.resample("1Min")
		#exit()

		#GROUP RESAMPLE TO PICKLE
		#groupResample(2015, 1, 12, "1Min", "EUR_USD")
		#exit()

		# READ PICKLE INTO DATAFRAME (prices)
		#backtest =  Backtest("historical/EUR_USD_Week3.csv_1Min-OHLC.pkl",backtestSettings,leverage,closeDictionary,backtestSettings['positions'])
		backtest = Backtest("historical/EUR_USD_2016_1_through_2.pkl",backtestSettings,leverage,backtestPositions)
		#backtest =  Backtest("historical/EUR_USD_2015_1_through_12.pkl",backtestSettings,leverage,closeDictionary,backtestSettings['positions'])
		prices = backtest.readPickle()

		# INSTANTIATE STRATEGY
		strategy = Strategy(prices, backtestPositions, priceQueue, backtestSettings)

		# LOOP THROUGH PRICES
		i = 0											# for displaying trades in a scatterplot
		for index, row in prices:

			# SKIP ERRORS IN PICKLE
			if np.isnan(row['Buy']) or np.isnan(row['Sell']):
				continue

			# 0.A: ADD CURRENT PRICE TO QUEUE
			priceQueue = strategy.doQueue(priceQueue,strategySettings["queuePeriod"],row)	# add current price to queue, along with stats

			# 1.A: CHECK IF TRADE IS OPEN
			tradeOpen = strategy.checkOpen()

			# 1.B: CHECK CLOSE CONDITIONS

			# 2.A: STRATEGY:
			signal = strategy.bollinger(row, priceQueue, backtestSettings, backtest.checkOpen(), display, backtest)	# check for buy/sell signals
			if signal and i >= strategySettings["queuePeriod"]:
				print "SIGNAL: ", signal
				backtest.executeTrade(signal["signal"], row, signal["stopLoss"], signal["takeProfit"], backtestSettings["leverage"])
			else:
				pass

			i = i + 1 									# increment loop for scaterplot
			time.sleep(0.001)							# give some time to process
			print backtest.account

	elif liveIndicator:
		print " *** LIVE TRADING ***"					# live trading