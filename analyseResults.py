import pandas
import matplotlib
import matplotlib.pyplot as plt
import sys

# read and print pickle
df = pandas.read_pickle("results.pkl")
print df.to_string()

#graph
startingRow = sys.argv[1]
endingRow = sys.argv[2]

j = df[100:200]
fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(j['price'])
ax.plot(j['upperBand'])
ax.plot(j['lowerBand'])
plt.show()


#plt.axvline(x=i, linewidth=1, color=self.arrayLine[side])