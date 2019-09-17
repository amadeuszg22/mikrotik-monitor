#!/usr/bin/python
import i2c_lcd
import requests
import time
import librouteros
from librouteros.login import login_plain, login_token
from librouteros import connect



	
#result = api(cmd='/interface/print', stats=True)
#for a in result:
#	print (a)
#	if a.get("default-name") == "ether1":
#		print (a.get("default-name"))
#		print (((a.get("tx-byte")/1024)/1024))
#		print (((a.get("rx-byte")/1024)/1024))

def feed(value,mo):
	if mo == "tx":
		try:
			url ="https://io.adafruit.com/api/v2/Ama_g/feeds/ether1-tx/data.json"
			headers = {'X-AIO-Key': '98d75633ba0440bebfe5840eedb09847','Content-Type': 'application/json'}
			data = '{"value": "'+str(value)+'"}'
			r = requests.post(url, data=data, headers=headers)
			results = r.json()
			print(results)
		except (ConnectionError):
			print ('Timeout')
	if mo == "rx":
		try:
			url ="https://io.adafruit.com/api/v2/Ama_g/feeds/ether1-rx/data.json"
			headers = {'X-AIO-Key': '98d75633ba0440bebfe5840eedb09847','Content-Type': 'application/json'}
			data = '{"value": "'+str(value)+'"}'
			r = requests.post(url, data=data, headers=headers)
			results = r.json()
			print(results)
		except (ConnectionError):
			print ('Timeout')
	if mo == "cpu":
		try:
			url ="https://io.adafruit.com/api/v2/Ama_g/feeds/r01-cpu/data.json"
			headers = {'X-AIO-Key': '98d75633ba0440bebfe5840eedb09847','Content-Type': 'application/json'}
			data = '{"value": "'+str(value)+'"}'
			r = requests.post(url, data=data, headers=headers)
			results = r.json()
			print(results)
		except (ConnectionError):
			print ('Timeout')
				
try:
	method = (login_plain, )
	api = connect(username='admin', password='Zaq220991', host='192.168.0.1', login_methods=method)
	while True:
		params = {'interface':'ether1','once':True}
		result = api(cmd='/interface/monitor-traffic', **params)
		for a in result:
			print ("RX",((a.get("rx-bits-per-second")/1024)))
			print ("TX",((a.get("tx-bits-per-second")/1024)))
			t=round((float(a.get("tx-bits-per-second")/1024)/1024),3)
			r=round((float(a.get("rx-bits-per-second")/1024)/1024),3)
			feed(t,"rx")
			feed(r,"tx")
			i2c_lcd.lcd_string("Traffic Monitor",i2c_lcd.LCD_LINE_1)
			i2c_lcd.lcd_string("................",i2c_lcd.LCD_LINE_2)
			time.sleep(1)
			i2c_lcd.clear()
			i2c_lcd.lcd_string("Download:"+str(r)+"Mbps",i2c_lcd.LCD_LINE_1)
			i2c_lcd.lcd_string("Upload:"+str(t)+"Mbps",i2c_lcd.LCD_LINE_2)
			#time.sleep(60)
			params = {'cpu-load'}
			result = api(cmd='/system/resource/print')
		for a in result:
			print ("CPU Load:",a.get("cpu-load"),"%")
			feed(a.get("cpu-load"),"cpu")
			time.sleep(60)
except (librouteros.exceptions.ConnectionError):
	print ('Timeout')