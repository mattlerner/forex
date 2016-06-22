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
from backtest import Backtest, groupResample, parse
from events import tradeEvent
from strategy import Strategy

#GLOBALS
signal = ""
openPositions = {"buy": 0, "sell":0}

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
closeDictionary = {"buy": "sell", "sell": "buy"}
takeProfitArray = {"buy": 1, "sell": -1}
sleepPlus = 0

#Backtest
backtestSettings = {
	"capital": 10000,
	"tradeAmount": 2000,
	"units": 80000,
	"positions": {"buy": 0, "sell": 0},
	"stopLoss": 0,
	"takeProfit": 0,
	"leverage":50
}

priceQueue = Queue.Queue()

# backtest
if __name__ == "__main__":

	#Convert data to pickle
	#backTest = Backtest("historical/EUR_USD_Week3.csv",backtestSettings,leverage,closeDictionary,backtestSettings['positions'])
	#output = backTest.resample("1Min")
	#exit()

	#Group resample to pickle
	#groupResample(2016, 1, 2, "1Min", "EUR_USD")
	#exit()

	# price array
	#backtest =  Backtest("historical/EUR_USD_Week3.csv_1Min-OHLC.pkl",backtestSettings,leverage,closeDictionary,backtestSettings['positions'])
	backtest =  Backtest("historical/EUR_USD_2016_1_through_2.pkl",backtestSettings,leverage,closeDictionary,backtestSettings['positions'])
	prices = backtest.readPickle()
	strategy = Strategy(prices, backtestSettings["positions"], priceQueue)
	queuePeriod = 50

	# loop through prices
	i = 0
	for index, row in prices:
		print row
		if np.isnan(row['Buy']) or np.isnan(row['Sell']):
			continue
		priceQueue = strategy.doQueue(priceQueue,queuePeriod,row)	# add current price to queue, along with stats
		signal = strategy.bollinger(row, priceQueue, backtestSettings, backtest.checkOpen(), backtest.account)	# check for buy/sell signals
		if backtest.checkOpen():	# check for stoploss / takeprofit signals
			signal = backtest.checkPrice(row, backtest.checkOpen())	# also adjust open positions
		if (signal["signal"] and i >= queuePeriod):	# execute signals
			print signal
			backtest.executeTrade(signal["signal"], row, signal["stopLoss"], signal["takeProfit"], backtestSettings["leverage"], closeDictionary)
			time.sleep(0.02)
		i = i+1
		print backtest.account
		print backtest.backtest['positions']
		time.sleep(0.001)