#!/usr/bin/python

import json
import urllib2
import ssl
import sys
class HTTPMethod():
	def __init__(self,ip):
		self.url = 'https://{}/redfish/v1'.format(ip)
		self.id = ""
		self.token = ""
	def MakeRequest(self,req):
		context = ssl._create_unverified_context()
		try:
			res = urllib2.urlopen(req,context=context)
			header = res.info()
			response = res.read().decode('utf-8')
			return header,response
		except urllib2.HTTPError as e:
			print(e.read())
	def post(self,url,data):
		url = self.url + str(url)
		data = json.dumps(data).encode('utf-8')
		req = urllib2.Request(url,data)
		req.get_method = lambda: "POST"
		req.add_header('Content-Type','application/json')
		header, res = self.MakeRequest(req)
		self.id = header.get('Location').split('/')[-2]
		self.token = header.get('X-Auth-Token')
		res = json.dumps(json.loads(res),indent=4,sort_keys=True)
		return header,res
	def get(self,url):
		url = self.url + str(url)
		headers={
			'Content-Type' : 'application/json','X-Auth-Token' : self.token
		}
		req = urllib2.Request(url,headers=headers)
		req.get_method = lambda: "GET"
		header, res = self.MakeRequest(req)
		res = json.dumps(json.loads(res),indent=4,sort_keys=True)
		return header,res

	def delete(self,url):
		url = self.url + str(url) + str(self.id) + "/"
		headers={
			'Content-Type' : 'application/json','X-Auth-Token' : self.token
		}
		req = urllib2.Request(url,headers=headers)
		req.get_method = lambda: "DELETE"
		header, res = self.MakeRequest(req)
		res = json.dumps(json.loads(res),indent=4,sort_keys=True)
		return header,res

if  __name__ == "__main__":
	http_methode = HTTPMethod(sys.argv[1])
	data = {
		"UserName" : "monitor",
		"Password" : "monitoring_shinken"
	}
	res, header = http_methode.post("/SessionService/Sessions/",data)
	print(res,header)
	res,header = http_methode.get("/Chassis/1/Thermal/")
	print(res,header)
	res, header = http_methode.delete("/SessionService/Sessions/")
	print(res,header)
	
	#print(http_methode.url)
