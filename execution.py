import httplib
import urllib
import json

class Execution(object):
	def __init__(self, domain, access_token, account_id):
		self.domain = domain
		self.access_token = access_token
		self.account_id = account_id
		self.conn = self.obtain_connection()

	def obtain_connection(self):
		return httplib.HTTPSConnection(self.domain)

	def execute_order(self, event):
		headers = {
			"Content-Type": "application/x-www-form-urlencoded",
			"Authorization": "Bearer " + self.access_token
		}
		params = urllib.urlencode({
			"instrument" : event.instrument,
			"units" : event.units,
			"type" : event.order_type,
			"side" : event.side,
			"stopLoss": event.stopLoss,
			"takeProfit": event.takeProfit#,
			#"price": event.price
		})
		self.conn.request(
			"POST",
			"/v1/accounts/%s/orders" % str(self.account_id),
			params, headers
		)
		response = json.loads(self.conn.getresponse().read())
		return response