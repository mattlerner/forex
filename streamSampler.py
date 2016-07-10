import pandas
import csv

allTicks = pandas.DataFrame(columns=('RateDateTime','RateAsk','RateBid'))

if __name__ == "__main__":
	f = open("historical/EUR_USD_2015_1-Week1.csv",'r')
	try:
		reader = csv.reader(f)
		varNames = next(reader)
		for row in reader:
			currentDict = dict(zip(varNames,row))

			del currentDict['cDealable']
			del currentDict['CurrencyPair']
			del currentDict['lTid']

			print currentDict
			allTicks.loc[len(allTicks)] = currentDict
	finally:
		f.close()
	print allTicks.values

def parse(self, datetime):
	for fmt in ('%Y-%m-%d %H:%M:%S.%f000000', '%Y-%m-%d %H:%M:%S'):
		try:
			return pandas.datetime.strptime(datetime, fmt)
		except ValueError:
			pass
	raise ValueError('no valid date format found')

# resamble tick data
def resample(self, resamplePeriod, df):
	df = pandas.read_csv(self.filename, parse_dates={'DateTime'}, index_col='DateTime', names=['Tid', 'Dealable', 'Pair', 'DateTime', 'Buy', 'Sell'], header=1, date_parser=self.parse)

	del df['Tid'] 
	del df['Dealable']
	del df['Pair']

	grouped_data = df.resample(resamplePeriod).mean()
	response = grouped_data.to_pickle(self.filename+'_'+resamplePeriod+'-OHLC.pkl')
	return response