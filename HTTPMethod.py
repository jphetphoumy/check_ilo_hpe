#!/usr/bin/python3

import urllib.request
class HTTPMethod():
	def __init__(self,ip):
		self.url = 'https://{}/redfish/v1/'.format(ip)
	def MakeRequest(self,req):
		context = ssl._create_unverified_context()
		try:
			res = urllib.request.urlopen(req,context=context)
			header = res.info()
			response = res.read().decode('utf-8')
			return header,response
		except urllib.request.HTTPError as e:
			print(e.read())
	def post(self,data,url):
		url = self.url + url
		data = json.dumps(data).encode('utf-8')
		req = urllib.request.Request(url,data)
		req.get_method = lambda: "POST"
		req.add_header('Content-Type','application/json')
		return self.MakeRequest(req)		
	def get(self,headers):
		req = urllib.request.Request(url,headers=headers)
		req.get_method = lambda: "GET"
		req.add_header('Content-Type','application/json')
		return self.MakeRequest(req)		
if  __name__ == "__main__":
	http_methode = HTTPMethod("10.10.10.10")
	print(http_methode.url)
