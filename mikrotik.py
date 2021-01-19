#!/usr/bin/python
#import i2c_lcd
import requests
import time
import librouteros
from librouteros.login import login_plain, login_token
from librouteros import connect
import logging
from datetime import datetime
import configparser
from prometheus_client import start_http_server, Summary,Gauge
import random

time_now = datetime.now()
gen_log = logging
wireless_log = logging
gen_log.basicConfig(filename='/home/machines/log/R01/r01-general.log', filemode='w', format='%(process)d-%(levelname)-s%(message)s')

class config:
	conf=configparser.ConfigParser()
	conf.read('config.ini')
	host=conf.get('r01','host')
	user=conf.get('r01','user')
	password=conf.get('r01','password')
	apikey=conf.get('r01','aio_key')
	tx = Gauge('if_ether_tx', 'eth1 tramsmitted data')
	rx = Gauge('if_ether_rx', 'eth1 received data')
	cpu=Gauge('mt_cpu', 'mikrotik cpu utilization')

	dhcp_l=Gauge('mt_dhcp_lease', 'dhcp leases')
	dhcp_l_a=Gauge('mt_dhcp_lease_active', 'dhcp active leases')
	
	caps_reg_table=Gauge('mt_caps_reg_table', 'Capsman registration table')


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
			headers = {'X-AIO-Key': config.apikey,'Content-Type': 'application/json'}
			data = '{"value": "'+str(value)+'"}'
			r = requests.post(url, data=data, headers=headers)
			results = r.json()
			print(results)
		except (requests.exceptions.ConnectionError):
			print ('Timeout')
	if mo == "rx":
		try:
			url ="https://io.adafruit.com/api/v2/Ama_g/feeds/ether1-rx/data.json"
			headers = {'X-AIO-Key': config.apikey,'Content-Type': 'application/json'}
			data = '{"value": "'+str(value)+'"}'
			r = requests.post(url, data=data, headers=headers)
			results = r.json()
			print(results)
		except (requests.exceptions.ConnectionError):
			print ('Timeout')
	if mo == "cpu":
		try:
			url ="https://io.adafruit.com/api/v2/Ama_g/feeds/r01-cpu/data.json"
			headers = {'X-AIO-Key': config.apikey,'Content-Type': 'application/json'}
			data = '{"value": "'+str(value)+'"}'
			r = requests.post(url, data=data, headers=headers)
			results = r.json()
			print(results)
		except (requests.exceptions.ConnectionError):
			print ('Timeout')
				
def main():
	while True:
		try:
			method = (login_plain, )
			api = connect(username=config.user, password=config.password, host=config.host, login_methods=method)
			params = {'interface':'ether1','once':True}
			result = api(cmd='/interface/monitor-traffic', **params)
			for a in result:
				print ("RX",((a.get("rx-bits-per-second")/1024)))
				print ("TX",((a.get("tx-bits-per-second")/1024)))
				t=round((float(a.get("tx-bits-per-second")/1024)/1024),3)
				r=round((float(a.get("rx-bits-per-second")/1024)/1024),3)
				feed(t,"rx")
				feed(r,"tx")
				config.tx.set(t)
				config.rx.set(r)

			params = {'cpu-load'}
			result = api(cmd='/system/resource/print')
			for a in result:
				print ("CPU Load:",a.get("cpu-load"),"%")
				feed(a.get("cpu-load"),"cpu")
				config.cpu.set(a.get("cpu-load"))
			
			dhcp_lease =api(cmd='/ip/dhcp-server/lease/print')
			dchp_act_lease = 0
			for d in dhcp_lease:
				if d.get("expires-after") is not None:
					#print (a.get("expires-after"))
					dchp_act_lease = dchp_act_lease +1
			print ("dhcp_lease",len(dhcp_lease))
			print ("dhcp_active_lease",dchp_act_lease)
			config.dhcp_l.set(len(dhcp_lease))
			config.dhcp_l_a.set(dchp_act_lease)

			caps_reg =api(cmd='/caps-man/registration-table/print')
			print ("capsman_reg-table",len(caps_reg))
			config.caps_reg_table.set(len(caps_reg))

			fw_conn =api(cmd='/ip/firewall/connection/print')
			print ("Fw connections",len(fw_conn))

			fw_conn_tcp = 0
			for i in fw_conn:
				if i.get("protocol") =="tcp": 
					fw_conn_tcp = fw_conn_tcp +1
			print ("FW conn tcp",fw_conn_tcp)

			fw_conn_udp = 0
			for i in fw_conn:
				if i.get("protocol") =="udp": 
					fw_conn_udp = fw_conn_udp +1
			print ("FW conn udp",fw_conn_udp)

			fw_conn_gre = 0
			for i in fw_conn:
				if i.get("protocol") == "gre": 
					fw_conn_gre = fw_conn_gre +1
			print ("FW conn gre",fw_conn_gre)

			fw_conn_icmp = 0
			for i in fw_conn:
				if i.get("protocol") =="icmp": 
					fw_conn_icmp = fw_conn_icmp +1
			print ("FW conn icmp",fw_conn_icmp)

			fw_conn_igmp = 0
			for i in fw_conn:
				if i.get("protocol") =="igmp": 
					fw_conn_igmp = fw_conn_igmp +1
			print ("FW conn igmp",fw_conn_igmp)

			logging.warning('time={0} ether1tx={1} ether1rx={2} cpu={3} dhcp_lease={4} caps-client={5} dchp_act_lease={6} fw_conn_val={7} fw_conn_tcp={8} fw_conn_udp={9} fw_conn_gre={10} fw_conn_icmp={11} fw_conn_igmp={12}'.format(time_now,t,r,a.get("cpu-load"),len(dhcp_lease),len(caps_reg),dchp_act_lease,len(fw_conn),fw_conn_tcp,fw_conn_udp,fw_conn_gre,fw_conn_icmp,fw_conn_igmp))
			#wireless_log.warning('time={0} caps-client={1}'.format(time_now,len(caps_reg)))
			time.sleep(30)


		
		except (librouteros.exceptions.ConnectionError):
				print ('Timeout')

if __name__=="__main__":
	start_http_server(8000)
	main()