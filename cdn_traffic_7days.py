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

    def fetch_cdn_data(self, cdn_name, domains_for_url, start_date_str, end_date_str):
        """
        Main method to fetch data based on cdn type, 
        and the data has already been standariztion in the return value.
        """
        if cdn_name.startswith("vai"):
            return self._fetch_vai_data(cdn_name, domains_for_url, start_date_str, end_date_str)
        elif cdn_name.startswith("ite"):
            return self._fetch_ite_data(cdn_name, domains_for_url, start_date_str, end_date_str)
        elif cdn_name.startswith("asia"):
            return self._fetch_asia_data(cdn_name, domains_for_url, start_date_str, end_date_str)
        elif cdn_name.startswith("cdnetworks"):
            return self._fetch_cdnetworks_data(cdn_name, domains_for_url, start_date_str, end_date_str)
        elif cdn_name.startswith("maoyun"):
            return self._fetch_maoyun_data(cdn_name, domains_for_url, start_date_str, end_date_str)
        elif cdn_name.startswith("huawei"):
            return self._fetch_huawei_data(cdn_name, domains_for_url, start_date_str, end_date_str)
        elif cdn_name.startswith("tencent"):
            return self._fetch_tencent_data(cdn_name, domains_for_url, start_date_str, end_date_str)
        else:
            logger.error(f"Unsupported CDN: {cdn_name}")
            return None

    # Existing CDN handlers
    def _fetch_vai_data(self, cdn_name, domains_for_url, start_date_str, end_date_str):
        API_KEY = config.VAI_API_KEY
        API_SECRET = config.VAI_API_SECRET
        headers = {
            "api-key": API_KEY,
            "api-secret": API_SECRET,
            "Content-Type": "application/json"
            }
        url = f"https://cdn.bccdn.com/monitor/usage?cate=site&type=traffic&start={start_date_str}&end={end_date_str}&res={domains_for_url}"
        response = requests.get(url, headers=headers)
        data = response.json()['data']
        return data[:-1] if data else []

    def _fetch_ite_data(self, cdn_name, domains_for_url, start_date_str, end_date_str):
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
        return data[:-1] if data else []

    def _fetch_asia_data(self, cdn_name, domains_for_url, start_date_str, end_date_str):
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
            return data[1:-1] if data else []
        return None

    def _fetch_cdnetworks_data(self, cdn_name, domains_for_url, start_date_str, end_date_str):
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
                    flow = f"{float(flow_entry.find('flow').text)*1_048_576:.2f}"
                    flow_data.append({'date': timestamp, 'value': flow})
                return flow_data[:-1] if flow_data else []
        return Client.main()

    def _fetch_maoyun_data(self, cdn_name, domains_for_url, start_date_str, end_date_str):
        # Replace with actual API call
        logger.info(f"Fetching maoyun data for {cdn_name} - placeholder")
        return None

    def _fetch_huawei_data(self, cdn_name, domains_for_url, start_date_str, end_date_str):
        full_start_date_str = start_date_str + " 00:00:00"         
        date_start_obj = datetime.datetime.strptime(full_start_date_str,"%Y-%m-%d %H:%M:%S") # turn into datetime object
        unix_start_timestamp = int(date_start_obj.timestamp() * 1000)                        # turn into unix timestamp

        end_date_obj = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")  # turn into datetime object,and the output shows %Y-%m-%d 00:00:00
        adjusted_end_date = end_date_obj - datetime.timedelta(days=1)        # "%Y-%m-%d -1 %H:%M:%S"
        unix_end_timestamp = int(adjusted_end_date.timestamp() * 1000)       # turn into unix timestamp
        
        
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
            request.interval = 86400
            response = client.show_domain_stats(request)
            flux_values = response.result['flux']
            
            data = []
            current_date = date_start_obj
            for flux in flux_values:
                date_str = current_date.strftime("%Y-%m-%d")
                data.append({'date': date_str, 'value': flux})
                current_date += datetime.timedelta(days=1)
                
            return data
            
        except exceptions.ClientRequestException as e:
            print(e.status_code)
            print(e.request_id)
            print(e.error_code)
            print(e.error_msg)

    def _fetch_tencent_data(self, cdn_name, domains_for_url, start_date_str, end_date_str):
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
                "Period": 86400,
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
            timestamps = datapoints[0]["Timestamps"]
            values = datapoints[0]["Values"]

            # Convert timestamps to date strings in UTC+8 and create the list of dictionaries
            result = [
                {
                    'date': datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d'),
                    'value': value
                }
                for timestamp, value in zip(timestamps, values)
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
        #This time scope should exactly be in 8 days,or the vai and ite would show hours data rather than day data
        end_date = datetime.datetime.now() - datetime.timedelta(days=-1)
        start_date = datetime.datetime.now() - datetime.timedelta(days=7)
        end_date_str = end_date.strftime('%Y-%m-%d')
        start_date_str = start_date.strftime('%Y-%m-%d')

        cdn_groups = [
            {"cdn": "vai_h5", "domains": ["h5.2v8k.live"]},
            {"cdn": "vai_91_channel", "domains": ["apt.er65.ltd", "apt.xwc1.live","apt.7a8w.ltd","apt.ol27.live","apt.i8zi.life"]},
            {"cdn": "vai_xindaxiang_channel", "domains": ["apt.7ark.ltd","apt.1zib.site"]},
            {"cdn": "ite_91_channel", "domains": ["apt.regh.ltd","apt.yu9r.ltd"]},
            {"cdn": "ite_xindaxiang_channel", "domains": ["apt.2qj4.live"]},
            {"cdn": "asia_shell", "domains": ["all"]},
            {"cdn": "cdnetworks_91_channel", "domains": ["apt.ccgff.com"]},
            {"cdn": "cdnetworks_91_share", "domains": ["apt.yjxyjt.com","apt.x15022.com","apt.gggccb.com"]},
            {"cdn": "cdnetworks_xindaxiang_channel", "domains": ["apt.kakjk.com"]},
            {"cdn": "cdnetworks_xindaxiang_share", "domains": ["apt.isoxqms.com","apt.pinestargold.com"]}, 
            {"cdn": "huawei_media", "domains": ["all"]},  
            {"cdn": "tencent_media", "domains": ["cos-traffic"]},
            # {"cdn": "maoyun_media", "domains": ["all"]}, 
        ]

        for group in cdn_groups:
            traffic_list = []
            cdn_name = group["cdn"]
            domains_for_url = "%20".join(group["domains"])
            domains_for_metrics = ",".join(group["domains"])

            try:
                usage_data = self.fetch_cdn_data(cdn_name, domains_for_url, start_date_str, end_date_str)
                if usage_data:
                    traffic_list.append([cdn_name, domains_for_metrics])
                    for entry in usage_data:
                        date = entry['date']
                        value = entry['value']
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
    exporter_port = 18562
    start_http_server(exporter_port)
    logger.info(f"Exporter server started on port {exporter_port}")

    while True:
        collector.fetch_metrics()
        time.sleep(15)

if __name__ == "__main__":
    main()
