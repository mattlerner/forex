import pandas
import csv
import numpy

def parse(datetime):
	for fmt in ('%Y-%m-%d %H:%M:%S.%f000000', '%Y-%m-%d %H:%M:%S'):
		try:
			return pandas.datetime.strptime(datetime, fmt)
		except ValueError:
			pass
	raise ValueError('no valid date format found')

# resamble tick data
def resample(resamplePeriod, df):
	grouped_data = df.resample(resamplePeriod).ohlc()#.mean()
	return grouped_data

# Dataframe to store time and price information
# Convert RateDateTime to datetime format and make it the index of the dataframe
allTicks = pandas.DataFrame(columns=('RateDateTime','RateAsk','RateBid','Avg'), dtype=float)
allTicks['RateDateTime'] = pandas.to_datetime(allTicks['RateDateTime'])
allTicks = allTicks.set_index('RateDateTime')

print allTicks.columns

resampled = pandas.DataFrame()

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

			if len(allTicks) > 100:
				resampled = resample("1Min",allTicks)
	finally:
		f.close()
	print allTicks.values