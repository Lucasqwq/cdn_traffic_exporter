#!/usr/bin/env python3
import sys
sys.path.append('/data/script/')
from packages.monitor.apple import *
from packages.console.console import *
import os
import configparser

# Load configuration
config = configparser.ConfigParser()
config.read(os.path.join('/data/script/config/console', 'app.ini'))

nickname = config.get("app", "nickname")
password = config.get("app", "password")
base_url = config.get("app", "BASE_URL")
chat_host = config.get("app", "CHAT_HOST")
chat_id = config.get("app", "CHAT_ID")

auth_token = load_token()

def get_hosts_urls2(base_url: str = '', auth_token: str = '', host_type: str = '', status: str = 'using', app_code: str = '') -> list:
    url = base_url + "/m_common/host_configs?host_type=" + host_type + "&host_status=" + status + "&app_code=" + app_code + "&limit=500"
    headers = {"X-AUTH-TOKEN": auth_token}
    result = []
    response = requests.get(url, headers=headers).json()
    for item in response["data"]["items"]:
        host = item['host']
        manufacturer = item['manufacturer_desc']
        result.append({'host': host, 'manufacturer': manufacturer})
    return result

# Define mappings
host_type_map = {
    'apk_channel_host': 'channel',
    'apk_share_host': 'share'
}
app_code_map = {
    'wildcard': '91',
    'xindaxiang': 'xindaxiang'
}
manufacturer_map = {
    'itecdn': 'ite',
    'vai': 'vai',
    '網宿': 'cdnetworks',
    '網速': 'cdnetworks',
}

# Initialize a dictionary to store categorized hosts
categorized_hosts = {}

# Define input lists
host_type = ['apk_channel_host', 'apk_share_host']
app_code = ['wildcard', 'xindaxiang']
status = ['using', 'prepared', 'willdelete']

# Populate the categorized_hosts dictionary
for type in host_type:
    for app in app_code:
        for x in status:
            urls = get_hosts_urls2(
                auth_token=auth_token,
                host_type=type,
                base_url=base_url,
                status=x,
                app_code=app
            )
            for entry in urls:
                host = entry['host'].replace('https://','')
                manufacturer = entry['manufacturer'] #廠商備注
                
                # Map to category components
                # Use original if not mapped,then it won't crash with KeyError value.
                host_category = host_type_map.get(type, type)
                app_category = app_code_map.get(app, app)
                manufacturer_category = manufacturer_map.get(manufacturer, manufacturer)  
                
                # Create section name like [vai_91_channel]
                section_name = f"{manufacturer_category}_{app_category}_{host_category}"
                
                # Add host to the appropriate category
                if section_name not in categorized_hosts:
                    categorized_hosts[section_name] = []
                categorized_hosts[section_name].append(host)

# Write results into a txt file for cdn_metrics_exporter.py get domain information
with open('domains.txt', 'w', encoding='utf-8') as file:
    for section , hosts in categorized_hosts.items():
        file.write(f"[{section}]\n")
        for host in hosts:
            file.write(f"{host}\n")
        file.write("\n")
