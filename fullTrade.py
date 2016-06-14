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
from execution import Execution
from backtest import Backtest
from events import tradeEvent

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
backtest = {
	"capital": 10000,
	"tradeAmount": 2000,
	"units": 80000,
	"positions": {"buy": 0, "sell": 0},
	"stopLoss": 0,
	"takeProfit": 0
}

if __name__ == "__main__":

	#Convert data to pickle
	#backTest = backTest("historical/EUR_USD_Week1.csv")
	#output = backTest.resample("1Min")
	#exit()

	# price array 
	prices = Backtest("historical/EUR_USD_Week1.csv_Tick-OHLC.pkl").readPickle()

	# loop through prices
	for index, row in prices:
		print row
	#get current price
	#check for open order
	#if no open order
		#check strategy open conditions
		#return signal
	#if open order
		#check strategy close conditions
		#return signal
	#execute signal
	#return positions
	#return account



	#Read in pickle
	"""backtest = backTest("historical/EUR_USD_Week1.csv_Tick-OHLC.pkl")
	pickle = backtest.readPickle()
	tradeOpen = 0
	for index, row in pickle.iterrows():
		tradeOpen = backtest.backtest['positions']['buy']+backtest.backtest['positions']['sell']
		if tradeOpen:
			signal = backtest.checkPrice(row, "buy")
			print signal
		elif not tradeOpen:
			signal = "buy"
			print signal
		result = backtest.executeTrade(signal,row,row['Buy']['high']-0.0002,row['Buy']['high']+0.0004)
		print result
		print backtest.positions()
		print backtest.account"""
		# print account
		# print current price
		# check for open positions
			# if there's an open position check to see if it's time to close it -> signal
			# if there's no open position, check to see if it's time to open one -> signal
		# execute signal
		# print execute result if there is one

	"""while True:

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

		event = tradeEvent(instrument, units, signal, trailingStop, takeProfitFull)
		execution = Execution(API_DOMAIN, ACCESS_TOKEN, ACCOUNT_ID)
		response = execution.execute_order(event)"""