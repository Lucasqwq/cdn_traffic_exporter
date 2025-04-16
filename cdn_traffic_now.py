#!/usr/bin/python3
from prometheus_client import start_http_server, Gauge, Counter, Info
import config
import xml.etree.ElementTree as ET
import requests
import time
import datetime
import logging
import sys
import json
import os
import signal
import hashlib

#for cdnetwork
sys.path.append("/opt/prometheus/cdn_traffic_exporter/cdnetworks") #for testing outside the conatainer
# sys.path.append("/app/cdnetworks")
from auth.AkSkAuth import AkSkAuth
from model.AkSkConfig import AkSkConfig
from api.models.models import *

#for huawei
from huaweicloudsdkcore.auth.credentials import GlobalCredentials
from huaweicloudsdkcdn.v2.region.cdn_region import CdnRegion
from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkcdn.v2 import *

#for tencent
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.monitor.v20180724 import monitor_client, models
        
log_dir = "/data/logs/cdn_traffic_exporter"
log_file = os.path.join(log_dir, "exporter.log")

os.makedirs(log_dir, exist_ok=True)
if not os.path.exists(log_file):
    with open(log_file, 'w'): pass

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)  # For journalctl-output
    ]
)
logger = logging.getLogger(__name__)

logging.getLogger('requests').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

# Function to parse domains.txt
def load_domains_from_file(file_path='domains.txt'):
    domains_dict = {}
    current_section = None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line:  # Skip empty lines
                    continue
                if line.startswith('[') and line.endswith(']'):  # Section header
                    current_section = line[1:-1]  # Remove [ and ]
                    domains_dict[current_section] = []
                elif current_section:  # Domain line
                    domains_dict[current_section].append(line)
                    
    except FileNotFoundError:
        logger.error(f"File {file_path} not found. Using default domains.")
        return {}
    
    except Exception as e:
        logger.error(f"Error reading {file_path}: {str(e)}")
        return {}
    
    return domains_dict

class WebsiteMetricsCollector:
    def __init__(self):
        self.website_traffic_value = Gauge(
            'website_traffic_value', #name of the metric
            'Traffic value in gigabytes', #annotation of the metric
            ['date', 'domain', 'cdn'] #the labels that metric have
        )

    def get_asia_token(self): #
        """Using ID and Key tot get asia cdn token"""
        timestamp = int(datetime.datetime.now().timestamp())
        sign_str = hashlib.md5((config.ASIA_API_KEY + config.ASIA_API_SECRET).encode()).hexdigest()
        sign = hashlib.md5((sign_str + str(timestamp)).encode("utf-8")).hexdigest()
        url = "https://cdnportal.myasiacloud.com/api/user/login/token"
        data = json.dumps({'sign': sign, 'time': timestamp, 'uid': '186'})
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, headers=headers, data=data)
        return response.json()["data"]["token"]

    def fetch_cdn_data(self, cdn_name, domains_for_url, user_package):
        """
        Main method to fetch data based on cdn type, 
        and the data has already been standariztion in the return value.
        """
        if cdn_name.startswith("vai"):
            return self._fetch_vai_data(cdn_name, domains_for_url, user_package)
        elif cdn_name.startswith("ite"):
            return self._fetch_ite_data(cdn_name, domains_for_url, user_package)
        elif cdn_name.startswith("asia"):
            return self._fetch_asia_data(cdn_name, domains_for_url, user_package)
        elif cdn_name.startswith("cdnetworks"):
            return self._fetch_cdnetworks_data(cdn_name, domains_for_url, user_package)
        elif cdn_name.startswith("maoyun"):
            return self._fetch_maoyun_data(cdn_name, domains_for_url, user_package)
        elif cdn_name.startswith("huawei"):
            return self._fetch_huawei_data(cdn_name, domains_for_url, user_package)
        elif cdn_name.startswith("tencent"):
            return self._fetch_tencent_data(cdn_name, domains_for_url, user_package)
        else:
            logger.error(f"Unsupported CDN: {cdn_name}")
            return None

    # Existing CDN handlers
    def _fetch_vai_data(self, cdn_name, domains_for_url, user_package):
        #This time scope should exactly be in 8 days,or the vai and ite would show hours data rather than day data
        start_date = datetime.datetime.now() - datetime.timedelta(days=7)
        end_date = datetime.datetime.now() - datetime.timedelta(days=-1)
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        API_KEY = config.VAI_API_KEY
        API_SECRET = config.VAI_API_SECRET
        headers = {
            "api-key": API_KEY,
            "api-secret": API_SECRET,
            "Content-Type": "application/json"
            }
        if user_package != "":
            url = f"https://cdn.bccdn.com/monitor/usage?cate=site&type=traffic&start={start_date_str}&end={end_date_str}&res=&user_package={user_package}"
        else:
            url = f"https://cdn.bccdn.com/monitor/usage?cate=site&type=traffic&start={start_date_str}&end={end_date_str}&res={domains_for_url}"
        response = requests.get(url, headers=headers)
        data = response.json()['data']
        return data[7:] if data else []

    def _fetch_ite_data(self, cdn_name, domains_for_url, user_package):
        #This time scope should exactly be in 8 days,or the vai and ite would show hours data rather than day data
        start_date = datetime.datetime.now() - datetime.timedelta(days=7)
        end_date = datetime.datetime.now() - datetime.timedelta(days=-1)
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        API_KEY = config.ITE_API_KEY
        API_SECRET = config.ITE_API_SECRET
        headers = {
            "api-key": API_KEY,
            "api-secret": API_SECRET,
            "Content-Type": "application/json"
            }
        url = f"https://cdn.itecdn.com/monitor/usage?cate=site&type=traffic&start={start_date_str}&end={end_date_str}&res={domains_for_url}"
        response = requests.get(url, headers=headers)
        data = response.json()['data']
        return data[7:] if data else []

    def _fetch_asia_data(self, cdn_name, domains_for_url, user_package):
        start_date = datetime.datetime.now() - datetime.timedelta(days=1)
        end_date = datetime.datetime.now() - datetime.timedelta(days=-1)
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        json_data = {
            'site': ["tc19-site-11"],
            'start': f"{start_date_str}",
            'end': f"{end_date_str}",
            'sec': 86400, #means the traffic value to be calculate by day
            'domain': ["_all"]
        }
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.get_asia_token()}"
            }
        url = "https://cdnportal.myasiacloud.com/api/dashboard/site"
        response = requests.post(url, headers=headers, json=json_data)
        if response.status_code == 200:
            site_data = response.json()['data']['tc19-site-11']
            # Convert asia date format to be consistent with others
            data = [{'date': datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d'),
                             'value': metrics['flow']}
                            for timestamp, metrics in site_data.items()
                            if float(metrics['flow']) > 0]
            return data[2:] if data else []
        return None

    def _fetch_cdnetworks_data(self, cdn_name, domains_for_url, user_package):
        start_date = datetime.datetime.now()
        end_date = datetime.datetime.now() - datetime.timedelta(days=-1)
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        domain_list = domains_for_url.split("%20")
        
        class Client:
            @staticmethod
            def main():
                queryDomainTotalTrafficRequest = QueryDomainTotalTrafficRequest()
                domainList = DomainList()
                domainList.domain_name = domain_list
                queryDomainTotalTrafficRequest.domain_list = domainList

                aksk_config = AkSkConfig()
                aksk_config.access_key = config.CDNETWORKS_API_KEY
                aksk_config.secret_key = config.CDNETWORKS_API_SECRET
                aksk_config.end_point = "api.cdnetworks.com"
                aksk_config.uri = (
                            f"/api/report/domainflow?"
                            f"dateFrom={start_date_str}T00%3A00%3A00%2B08%3A00&"
                            f"dateTo={end_date_str}T23%3A59%3A59%2B08%3A00&type="
                        )                
                aksk_config.method = "POST"

                # See AkSkAuth class for more methods, you can edit
                response = AkSkAuth.invoke(aksk_config, json.dumps(queryDomainTotalTrafficRequest.to_map()))
                root = ET.fromstring(response)
                flow_data = []
                for flow_entry in root.findall('flow-data'):
                    timestamp = flow_entry.find('timestamp').text
                    flow = f"{float(flow_entry.find('flow').text)*1_000_000:.2f}"
                    flow_data.append({'date': timestamp, 'value': flow})
                return flow_data if flow_data else []
        return Client.main()

    def _fetch_maoyun_data(self, cdn_name, domains_for_url, user_package):
        # Replace with actual API call
        logger.info(f"Fetching maoyun data for {cdn_name} - placeholder")
        return None

    def _fetch_huawei_data(self, cdn_name, domains_for_url, user_package):
        start_date = datetime.datetime.now().replace(hour=0,minute=0,second=0,microsecond=0)
        end_date = datetime.datetime.now().replace(hour=23,minute=59,second=59,microsecond=0)
        unix_start_timestamp = int(start_date.timestamp() * 1000)
        unix_end_timestamp = int(end_date.timestamp() * 1000)
        
        
        ak = config.HUAWEI_API_KEY
        sk = config.HUAWEI_API_SECRET

        credentials = GlobalCredentials(ak, sk)

        client = CdnClient.new_builder() \
            .with_credentials(credentials) \
            .with_region(CdnRegion.value_of("ap-southeast-1")) \
            .build()

        try:
            request = ShowDomainStatsRequest()
            request.action = "detail"               
            request.start_time = unix_start_timestamp #1740585600000 
            request.end_time = unix_end_timestamp #1741190400000
            request.domain_name = "all"
            request.stat_type = "flux"
            request.interval = 3600
            response = client.show_domain_stats(request)
            flux_values = response.result['flux']
            
            data = [{'date': start_date.strftime("%Y-%m-%d"), 'value': sum(flux_values)}]
                
            return data if data else []
            
        except exceptions.ClientRequestException as e:
            print(e.status_code)
            print(e.request_id)
            print(e.error_code)
            print(e.error_msg)

    def _fetch_tencent_data(self, cdn_name, domains_for_url, user_package):     
        end_date = datetime.datetime.now()
        start_date = datetime.datetime.now()
        end_date_str = end_date.strftime('%Y-%m-%d')
        start_date_str = start_date.strftime('%Y-%m-%d')
        
        try:
            # Authentication with Tencent Cloud credentials
            cred = credential.Credential(config.TENCENT_API_KEY, config.TENCENT_API_SECRET)

            # HTTP profile configuration
            httpProfile = HttpProfile()
            httpProfile.endpoint = "monitor.intl.tencentcloudapi.com"

            # Client profile configuration
            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile

            # Initialize the MonitorClient
            client = monitor_client.MonitorClient(cred, "ap-guangzhou", clientProfile)

            # Create a request object
            req = models.GetMonitorDataRequest()
            params = {
                "Namespace": "QCE/COS",
                "MetricName": "InternetTraffic",
                "Period": 3600,
                "StartTime": f"{start_date_str}T00:00:00+08:00",
                "EndTime": f"{end_date_str}T23:59:59+08:00",
                "Instances": [
                    {
                        "Dimensions": [
                            {
                                "Name": "bucket",
                                "Value": "ossfile-1325226513"
                            }
                        ]
                    }
                ]
            }
            req.from_json_string(json.dumps(params))

            # Execute the request and get the response
            resp = client.GetMonitorData(req)

            # Convert response to JSON string and parse it into a dictionary
            data_json = resp.to_json_string()
            data = json.loads(data_json)

            # Debugging: Print the raw parsed data
            #print("Raw API Response:", json.dumps(data, indent=2))

            # Extract DataPoints directly from the root level
            datapoints = data["DataPoints"]

            # Extract timestamps and values from the first DataPoints entry
            values = datapoints[0]["Values"]
            total = 0
            for value in values:
                total = total + value
                
            # Convert timestamps to date strings in UTC+8 and create the list of dictionaries
            result = [
                {
                    'date': start_date_str,
                    'value': sum(values)
                }
            ]

            # Print the result
            print("\nProcessed Data:")
            # print(result)
            return result

        except TencentCloudSDKException as err:
            print("API Error:", err)
        logger.info(f"Fetching tencent data for {cdn_name} - placeholder")
        return None

    def fetch_metrics(self):

        cdn_groups = [
            {"cdn": "vai_h5", "domains": ["all"], "user_package": 9},
            {"cdn": "vai_91_channel", "domains": [""], "user_package": ""},
            {"cdn": "vai_xindaxiang_channel", "domains": [""], "user_package": ""},
            {"cdn": "ite_91_channel", "domains": [""], "user_package": ""},
            {"cdn": "ite_xindaxiang_channel", "domains": [""], "user_package": ""},
            {"cdn": "asia_shell", "domains": ["all"], "user_package": "tc19-site-11"},
            {"cdn": "cdnetworks_91_channel", "domains": [""], "user_package": ""},
            {"cdn": "cdnetworks_91_share", "domains": [""], "user_package": ""},
            {"cdn": "cdnetworks_xindaxiang_channel", "domains": [""], "user_package": ""},
            {"cdn": "cdnetworks_xindaxiang_share", "domains": [""], "user_package": ""}, 
            {"cdn": "huawei_media", "domains": ["all"], "user_package": ""},  
            {"cdn": "tencent_media", "domains": ["cos-traffic"], "user_package": ""},
            # {"cdn": "maoyun_media", "domains": ["all"], "user_package": ""}, 
        ]
        
        # Load domains from domains.txt
        domains_dict = load_domains_from_file()
        
        # Update cdn_groups with domains from domains.txt
        if domains_dict:
            for group in cdn_groups:
                cdn_name = group["cdn"]
                if cdn_name in domains_dict:
                    group["domains"] = domains_dict[cdn_name]
                    logger.info(f"Updated {cdn_name} with domains: {group['domains']}")

        # Add missing groups from domains.txt that aren't in cdn_groups
        # for cdn_name, domains in domains_dict.items():
        #     if not any(group["cdn"] == cdn_name for group in cdn_groups):
        #         cdn_groups.append({"cdn": cdn_name, "domains": domains, "user_package": ""})
        #         logger.info(f"Added new group from domains.txt: {cdn_name} with domains: {domains}")

        for group in cdn_groups:
            traffic_list = []
            cdn_name = group["cdn"]
            user_package = group["user_package"]
            domains_for_url = "%20".join(group["domains"])
            domains_for_metrics = ",".join(group["domains"])

            try:
                usage_data = self.fetch_cdn_data(cdn_name, domains_for_url, user_package)
                if usage_data:
                    traffic_list.append([cdn_name, domains_for_metrics])
                    for entry in usage_data:
                        date = entry['date']
                        value = entry['value']
                        #Each cdn value transformation is different,so should be add to one of the below
                        if cdn_name.startswith(("huawei")):
                            value_in_tb = f"{(float(value) / 1_099_511_627_776):.2f}"
                            self.website_traffic_value.labels(date=date, domain=domains_for_metrics, cdn=cdn_name).set(value_in_tb)
                            traffic_list.append(f"Date: {date}, traffic_value: {value_in_tb} TB")
                        elif cdn_name.startswith(("tencent")):
                            value_in_tb = f"{(float(value) / 1_000_000_000_000):.2f}"
                            self.website_traffic_value.labels(date=date, domain=domains_for_metrics, cdn=cdn_name).set(value_in_tb)
                            traffic_list.append(f"Date: {date}, traffic_value: {value_in_tb} TB")
                        elif cdn_name.startswith(("cdnetworks","asia")):
                            value_in_gb = f"{(float(value) / 1_000_000_000):.2f}"
                            self.website_traffic_value.labels(date=date, domain=domains_for_metrics, cdn=cdn_name).set(value_in_gb)
                            traffic_list.append(f"Date: {date}, traffic_value: {value_in_gb} GB")
                        elif cdn_name.startswith(("vai","ite")):
                            value_in_gb = f"{(float(value) / 1_073_741_824):.2f}"
                            self.website_traffic_value.labels(date=date, domain=domains_for_metrics, cdn=cdn_name).set(value_in_gb)
                            traffic_list.append(f"Date: {date}, traffic_value: {value_in_gb} GB")
                        else:
                            logger.info(f"{cdn_name} should be add to one of the transformation in code")
                    logger.info(f"Response data for {cdn_name}: {json.dumps(traffic_list, indent=2)}")

                else:
                    logger.error(f"No data returned for {cdn_name}")

            except requests.exceptions.RequestException as e:
                logger.error(f"Error fetching data from {cdn_name}: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error for {cdn_name}: {str(e)}")

def signal_handler(sig, frame):
    logger.info("Received shutdown signal, exiting...")
    sys.exit(0)

def main():
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    collector = WebsiteMetricsCollector()
    collector.fetch_metrics()

if __name__ == "__main__":
    main()
