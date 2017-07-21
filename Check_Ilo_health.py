#!/usr/bin/python

import ssl
import urllib2 
import argparse
import sys
import json
from HTTPMethod import HTTPMethod

class redfish():
	def __init__(self, username, password,ip,debug = False):
		"""
		Init redfish
		"""

		self.username = username
		self.password = password
		self.ip = ip
		self.http_method = HTTPMethod(self.ip)
		self.debug = debug
	def auth(self):
		"""
		function to authenticate to the api
		"""
		data = {
			"UserName" : self.username,
			"Password" : self.password
		}
		header, res = self.http_method.post("/SessionService/Sessions/",data)
		if self.debug:

			print(res,header)
		else:
			pass
	def logout(self):
		header, res = self.http_method.delete("/SessionService/Sessions/")
		if self.debug:
			print(res,header)
		else:
			pass

	def get_FanSpd(self,FanNumber):
		"""
		Get Speed of the ILO Fan
		"""
		header, res = self.http_method.get("/Chassis/1/Thermal/")	
		try:
			#print(res)
			Fans = json.loads(str(res))['Fans']
			FanName = Fans[FanNumber]['FanName']
			spd_fan = Fans[FanNumber]['CurrentReading']
			if spd_fan <90 and spd_fan !=0:
				state = "OK"
				print("{} is at {} % state is {}".format(FanName,spd_fan,state))
				self.logout()
				sys.exit(0)
			elif spd_fan >=85:
				state = "WARNING"
				print("{} is at {} % state is {}".format(FanName,spd_fan,state))
				self.logout()
				sys.exit(1)
			elif spd_fan == 0 or spd_fan >=90:
				state = "CRITICAL"
				print("{} is at {} % state is {}".format(FanName,spd_fan,state))
				self.logout()
				sys.exit(2)
			else:
				state = "UNKNOWN"
				print("{} is at {} % state is {}".format(FanName,spd_fan,state))
				self.logout()
				sys.exit(3)

			self.logout()
		except IndexError:
			print("There is not such Fan {}".format(FanNumber+1))

	def get_Temperature(self,TempNumber):
			"""
			Get Speed of the ILO Fan
			"""
			header, res = self.http_method.get("/Chassis/1/Thermal/")	
			try:
				#print(res)
				Temp = json.loads(str(res))['Temperatures']
				TempName = Temp[TempNumber]['Name']
				TempDeg = Temp[TempNumber]['CurrentReading']	
				TempNonCrit = Temp[TempNumber]['LowerThresholdNonCritical']
				TempCrit = Temp[TempNumber]['LowerThresholdCritical']
				if TempCrit == 0:
					TempCrit = 90
				else:
					pass
				if TempDeg < TempNonCrit:
					state = "OK"
					print("{} is at {}C state is {}".format(TempName,TempDeg,state))
					self.logout()
					sys.exit(0)
				elif TempDeg >= TempCrit:
					state = "CRITICAL"
					print("{} is at {}C state is {}".format(TempName,TempDeg,state))
					self.logout()
					sys.exit(2)
				elif TempDeg >= TempNonCrit:
					state = "WARNING"
					print("{} is at {}C state is {}".format(TempName,TempDeg,state))
					self.logout()
					sys.exit(1)
				
				else:
					state = "UNKNOWN"
					print("{} is at {}C state is {}".format(TempName,TempDeg,state))
					self.logout()
					sys.exit(3)

				self.logout()
			except IndexError:
				print("There is not such Thing {}".format(FanNumber+1))
if __name__ == "__main__":
	
	#Create argument
	parser = argparse.ArgumentParser(description="Check Ilo Health",epilog="usage: check_ilo_health.py -u root -p password -H 192.168.1.1 -chkFan 0")
	parser.add_argument('--username','-u',help="username who can access to ILO")
	parser.add_argument('--password','-p',help="password of your ILO Account")
	parser.add_argument('--host','-H',help="Ip of your server")
	parser.add_argument('--checkFan','-chkFan',help="Check speed of the fan number x")
	parser.add_argument('--CheckTemperature','-ChkTemp',help="Check Temperature of hardware")
	parser.add_argument('--debug','-D',help="Debug mode",dest="debug",action="store_true")
	
	#Check if argument is specified if not print print help

	if len(sys.argv)==1:
		parser.print_help()
	else:
		args = parser.parse_args()
	
	#Init redfish
	USERNAME = args.username
	PASSWORD = args.password
	HOST = args.host
	DEBUG = args.debug
	redfish = redfish(USERNAME, PASSWORD, HOST, DEBUG)
	redfish.auth()
	if args.checkFan:
		redfish.get_FanSpd(int(args.checkFan)-1)
	if args.CheckTemperature:
		redfish.get_Temperature(int(args.CheckTemperature)-1)
