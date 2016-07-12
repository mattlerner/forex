import pandas
import csv
import numpy
import datetime


# resamble tick data
def resample(resamplePeriod, df):
	grouped_data = df.resample(resamplePeriod).ohlc()#.mean()
	return grouped_data

# Dataframe to store time and price information
# Convert RateDateTime to datetime format and make it the index of the dataframe
allTicks = pandas.DataFrame(columns=('RateDateTime','RateAsk','RateBid','Avg'), dtype=float)
allTicks['RateDateTime'] = pandas.to_datetime(allTicks['RateDateTime'])
allTicks = allTicks.set_index('RateDateTime')

resampled = pandas.DataFrame()

timeFrame = 50

# main function
if __name__ == "__main__":

	# read in tick data
	f = open("historical/EUR_USD_2015_1-Week1.csv",'r')

	try:
		reader = csv.reader(f)							# CSV reader
		varNames = next(reader)							# this array is the first CSV row, e.h. varnames
		for row in reader:

			currentDict = dict(zip(varNames,row)) 		# declare dictionary of keys and values

			# remove columns we DGAF about
			del currentDict['cDealable']
			del currentDict['CurrencyPair']
			del currentDict['lTid']

			# next two rows are a hack. figure out why these are objects and not floats
			currentDict['RateAsk'] = float(currentDict['RateAsk'])
			currentDict['RateBid'] = float(currentDict['RateBid'])
			currentDict['Avg'] = (float(currentDict['RateAsk']) + float(currentDict['RateBid'])) / 2
			currentSeries = pandas.Series(data=currentDict)
			currentSeries['RateDateTime'] = pandas.to_datetime(currentSeries['RateDateTime'])

			allTicks.loc[currentSeries['RateDateTime']] = currentSeries	# add current row to allTicks dataframe


			timeFrameTime = currentSeries['RateDateTime'] - datetime.timedelta(minutes=timeFrame)
			allTicks = allTicks[allTicks.index > timeFrameTime]

			print allTicks.index

			#resampled = resample("1Min",allTicks)
	finally:
		f.close()
	print allTicks.values