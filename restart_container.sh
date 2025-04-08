#!/bin/bash
# get latest domain
cd /opt/prometheus/cdn_traffic_exporter && /usr/bin/python3 get_cdn_domain.py

# restart to clear old metrics cache
cd /opt/prometheus
/usr/bin/docker stop cdn_traffic_exporter
/usr/bin/docker rm cdn_traffic_exporter
/usr/bin/docker rmi prometheus-cdn_traffic_exporter
/usr/local/bin/docker-compose up -d cdn_traffic_exporter

# setting crontab to run this shell script
# restart cdn_traffic_exporter for clearing the old date metrics,also update the domain in the domains.txt
# 1 0 * * * cd /opt/prometheus/cdn_traffic_exporter && /bin/bash restart_container.sh > /tmp/restart_container.log 2>&1
