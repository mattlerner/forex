import pandas
import matplotlib
import matplotlib.pyplot as plt
import sys

arrayLine = {"sell":"r","buy":"g"}

# read and print pickle
df = pandas.read_pickle("results.pkl")
print df.to_string()

#graph
startingRow = sys.argv[1]
endingRow = sys.argv[2]

j = df[int(startingRow):int(endingRow)]
fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(j['price'])
ax.plot(j['upperBand'])
ax.plot(j['lowerBand'])
ax.plot(j['movingAverage'])

for index, row in j.iterrows():
	if row['orderType'] is not '':
		plt.axvline(x=index, linewidth=1, color=arrayLine[row['orderType']])
plt.show()
