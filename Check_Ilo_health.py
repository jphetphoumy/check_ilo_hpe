#!/usr/bin/python3

import ssl
import urllib.request 
import urllib.parse
import argparse
import sys
import json

def Post_Request(ip,user,passwd):
	url = 'https://{}/redfish/v1/SessionService/Sessions/'.format(ip)
	data = {
		"UserName" : "monitor",
		"Password" : "monitoring_shinken"
	}
	data = json.dumps(data).encode('utf-8')
	context = ssl._create_unverified_context()
	req = urllib.request.Request(url,data)
	req.get_method = lambda: "POST"
	req.add_header('Content-Type','application/json')
	try:
		res = urllib.request.urlopen(req, context=context)
		header = res.info()
		response = res.read().decode('utf-8')
		return header, response
	except urllib.request.HTTPError as e:
		print(e.read())

def Get_Request(ip,header):
	url = 'https://{}/redfish/v1/SessionService/Sessions/'.format(ip)	
	context = ssl._create_unverified_context()
	headers={'Content-Type' : 'application/json','X-Auth-Token' : header}
	req = urllib.request.Request(url, headers=headers)
	req.get_method = lambda: "GET"
	try:
		res = urllib.request.urlopen(req, context=context)
		header = res.info()
		response = res.read().decode('utf-8')
		return header, response
	except urllib.request.HTTPError as e:
		print(e.read())

def Logout_Request(ip,header,identifiant):
	url = 'https://{}/redfish/v1/SessionService/Sessions/{}/'.format(ip,identifiant)	
	context = ssl._create_unverified_context()
	headers={'Content-Type' : 'application/json','X-Auth-Token' : header}
	req = urllib.request.Request(url, headers=headers)
	req.get_method = lambda: "DELETE"
	try:
		res = urllib.request.urlopen(req, context=context)
		header = res.info()
		response = res.read().decode('utf-8')
		return header, response
	except urllib.request.HTTPError as e:
		print(e.read())

def Chassis_Request(ip,header):
	url = 'https://{}/redfish/v1/Chassis/1/Thermal/'.format(ip)	
	context = ssl._create_unverified_context()
	headers={'Content-Type' : 'application/json','X-Auth-Token' : header}
	req = urllib.request.Request(url, headers=headers)
	req.get_method = lambda: "GET"
	try:
		res = urllib.request.urlopen(req, context=context)
		header = res.info()
		response = res.read().decode('utf-8')
		return header, response
	except urllib.request.HTTPError as e:
		print(e.read())


class redfish():
    def __init__(self, username, password,ip,debug = False):
        """
        Init redfish
        """

        self.username = username
        self.password = password
        self.ip = ip
        self.debug = debug
        self.token = ""
        self.id = ""
    def auth(self):
        """
        function to authenticate to the api
        """
        # Debuging 
        
        response = Post_Request(self.ip,self.username, self.password)
        self.token = response[0].get('X-Auth-Token')
        self.location = {'Location' : response[0].get('Location')}
        self.id = response[0].get('Location').split('/')[-2]
        if self.debug:
       	    print("Sending login : \n\t>{0}\npassword : \n\t>{1} \nto the server \n\t>{2}".format(self.username, self.password,self.ip))
            print("Raw response from the server {}".format(self.ip))
            parsed = json.loads(response[1])
            print(json.dumps(parsed,indent=4, sort_keys=True))
            print(response[0])
            print(self.token)
            print(self.location)
            print(response[0].get('Location').split('/')[-2])
            # Set token x-auth

    def get_chassis(self,FanNumber):
        response = Chassis_Request(self.ip, self.token) 
        if not self.debug:
            # SHOW ALL SESSION
            parsed = json.loads(response[1])['Fans'][FanNumber]
            print("There is not such Fan {}".format(FanNumber))
            spd_fan = parsed['CurrentReading']
            if spd_fan <90:	
                state = "OK"
                print(parsed['FanName'],spd_fan,state)
                sys.exit(0)
            #print(json.dumps(parsed,indent=4, sort_keys=True))
    def logout(self):
        """
        Logout 
        """
        response = Get_Request(self.ip, self.token) 
        response_Logout = Logout_Request(self.ip, self.token, self.id)
        if self.debug:
            # SHOW ALL SESSION
            parsed = json.loads(response[1])
            print(json.dumps(parsed,indent=4, sort_keys=True))

            # LOGOUT CURRENT SESSION 
            print("Logout {}".format(self.id))
            parsed1 = json.loads(response_Logout[1])
            print(json.dumps(parsed1,indent=4, sort_keys=True))
    def get_FanSpd(self,FanNumber):
        """
        Get Speed of the ILO Fan
        """
        
        response = Chassis_Request(self.ip, self.token) 
        if not self.debug:
            # SHOW ALL SESSION
            try:
                parsed = json.loads(response[1])['Fans'][FanNumber]
                spd_fan = parsed['CurrentReading']
                #spd_fan = 0
                if spd_fan <90 and spd_fan != 0:	
                    state = "OK"
                    print(parsed['FanName'],spd_fan,state)
                    sys.exit(0)
                elif spd_fan >=85:
                    state = "WARNING"
                    print(parsed['FanName'],spd_fan,state)
                elif spd_fan == 0 or spd_fan == 90:
                    state = "CRITICAL"
                    print(parsed['FanName'],spd_fan,state)

            except IndexError:
                   print("There is not such Fan {}".format(FanNumber+1))
     
    def get_hdware_Temperature(self):
        """
        Get Temperature of ILO Hardware
        """
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
        redfish.get_FanSpd(int(args.checkFan)-1)
        redfish.logout()
