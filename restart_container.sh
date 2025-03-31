#!/bin/bash
cd /opt/prometheus
/usr/bin/docker stop cdn_traffic_exporter
/usr/bin/docker rm cdn_traffic_exporter
/usr/local/bin/docker-compose up -d cdn_traffic_exporter
