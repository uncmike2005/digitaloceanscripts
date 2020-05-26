#!/usr/bin/python3

import json
import requests
import argparse
from configparser import ConfigParser
import os 

#Get the API token
config_file = os.path.join(os.path.dirname(__file__), "config-do.cfg")
config = ConfigParser()
config.read(config_file)
api_token = config.get('DigitalOcean', 'do_token')
#print(api_token)

#FORMAT OF THE CONFIG FILE config-do.cfg
#[DigitalOcean]
#do_token = <unquoted API key>


#Add the headers and set the base url
api_url_base = 'https://api.digitalocean.com/v2/'
headers = {'Content-Type': 'application/json',
           'Authorization': 'Bearer {0}'.format(api_token)}

#Arguments
parser = argparse.ArgumentParser()
parser.add_argument("name", help="Name of the Firewall you want to update")
args = parser.parse_args()
name  = args.name


def get_account_info():

    api_url = '{0}account'.format(api_url_base)

    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        return json.loads(response.content.decode('utf-8'))
    else:
        return None

def get_firewalls():
    api_url = '{0}firewalls'.format(api_url_base)
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        return json.loads(response.content.decode('utf-8'))
    else:
        return None

def put_firewall(id, firewall):
    api_url = '{0}firewalls/{1}'.format(api_url_base, id)
    r = requests.put(api_url, headers=headers, data=json.dumps(firewall))
    print(r)
    return None
    
def get_public_ipv4():
    ip = requests.get('https://api.ipify.org').text
    return format(ip)

def get_cf_addresses():
    cf = requests.get('https://www.cloudflare.com/ips-v4').text
    return cf.splitlines()

#Get the current firewall information
firewall_info = get_firewalls()

#The firewall we are looking for
myFirewall = {}

#Search for the firewall
if firewall_info is not None:
#    print("Here's your info: ")
    for k in firewall_info['firewalls']:
        #print(k['id'])
        if k['name'] == name:
            myFirewall = k
        #print(k[0])
else:
    print('[!] Request Failed')

id = myFirewall['id']

#Remove items from the JSON to prep for POST to the DO API
del myFirewall['id']
del myFirewall['status']
del myFirewall['pending_changes']
del myFirewall['created_at']

#Create a new rule to replace the old rules
myRules = []
#newRule = {'protocol': 'tcp', 'ports': '443', 'sources': ''}
cf = get_cf_addresses()
i = 0
print("Cloudflare IP Ranges:")
for ipcidr in cf:
   print(ipcidr)
   thisIPList = []
   thisIPList.append(ipcidr)
   myRules.append({'protocol': 'tcp', 'ports': '443', 'sources': ''})
   myRules[i]['sources'] = {'addresses': thisIPList}
   i += 1

myFirewall['inbound_rules'] = myRules
#print(myFirewall)
put_firewall(id, myFirewall)

