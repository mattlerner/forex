import requests
import json

class StreamingForexPrices(object):
	def __init__(self, domain, access_token, account_id, instruments):
		self.domain = domain
		self.access_token = access_token
		self.account_id = account_id
		self.instruments = instruments
		self.cur_bid = None
		self.cur_ask = None

	def connect_to_stream(self):
		try:
			s = requests.Session()
			url = "https://" + self.domain + "/v1/prices"
			headers = {'Authorization' : 'Bearer ' + self.access_token}
			params = {'instruments' : self.instruments, 'accountId' : self.account_id}
			req = requests.Request('GET', url, headers=headers, params=params)
			pre = req.prepare()
			resp = s.send(pre, stream=True, verify=False)
			return resp
		except Exception as e:
			s.close()
			print "Caught exception when connecting to stream\n" + str(e)

	def doStream(self):
		try:
			response = self.connect_to_stream()
		except Exception as e:
			print "Exception! -- " + str(e)
		if response.status_code != 200:
			return
		for line in response.iter_lines(1):
			if line:
				try:
					msg = json.loads(line)
					return msg
				except Exception as e:
					print "Caught exception when converting message into json\n" + str(e)
					return
				if msg.has_key("instrument") or msg.has_key("tick"):
					instrument = msg["tick"]["instrument"]
					time = msg["tick"]["time"]
					bid = msg["tick"]["bid"]
					ask = msg["tick"]["ask"]
					self.cur_bid = bid
					self.cur_ask = ask
				#elif msg.has_key("heartbeat"):
				#	return msg["heartbeat"]
					"""self.price_queue.put(msg["heartbeat"])
					qsize = self.price_queue.qsize()
					print list(self.price_queue.queue)
					use reduce here to add across the list then divide by qsize
					#ex: avg = reduce(lambda x, y: x + y, list(newq.queue)) / newq.qsize()"""