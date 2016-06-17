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
from backtest import Backtest
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

#Backtest
backtestSettings = {
	"capital": 10000,
	"tradeAmount": 2000,
	"units": 80000,
	"positions": {"buy": 0, "sell": 0},
	"stopLoss": 0,
	"takeProfit": 0
}

priceQueue = Queue.Queue()

# backtest
if __name__ == "__main__":

	#Convert data to pickle
	#backTest = Backtest("historical/EUR_USD_Week1.csv",backtestSettings,leverage,closeDictionary)
	#output = backTest.resample("1Min")
	#exit()

	# price array
	backtest =  Backtest("historical/EUR_USD_Week1.csv_1Min-OHLC.pkl",backtestSettings,leverage,closeDictionary)
	prices = backtest.readPickle()
	strategy = Strategy(prices, backtestSettings["positions"], priceQueue)
	queuePeriod = 50
	#bigFig = doFigure()

	# loop through prices
	i = 0
	for index, row in prices:
		#print row
		priceQueue = strategy.doQueue(priceQueue,queuePeriod,row)
		signal = strategy.bollinger(row, priceQueue, backtestSettings)
		if strategy.checkOpen():
			signal = backtest.checkPrice(row, strategy.checkOpen())
		if (signal["signal"] and i >= queuePeriod):
			print signal
			backtest.executeTrade(signal["signal"], row, signal["stopLoss"], signal["takeProfit"], leverage, closeDictionary)
			time.sleep(1)
		i = i+1
		print backtest.account
		print backtest.backtest['positions']