import httplib
import json

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