# CDN Traffic Metrics Exporter

- This project use `prometheus_client` module to expose metric value from cdn_traffic to build a Grafana dashboard.
- Retrieve traffic data for a specific domain through the APIs of various CDN providers, convert it into Metrics Values compatible with Prometheus, and then integrate it into a Grafana dashboard, supporting direct copy-paste into an Excel traffic table.

## Prerequisites  
- **Python Environment**：Basic on `python:3.8.10-slim` Docker image  
- **Packages requirements**：Install `requirements.txt` Python module  
- **API Authentication**：`config.py` The file includes API authentication information from each CDN providers
- **Cdnetworks API packages**：`cdnetworks` The folder includes Cdnetworks API SDK  
- **Dockerfile contents:**  
    ```
    FROM python:3.8.10-slim

    WORKDIR /app

    COPY . .

    RUN python3 -m pip install -r requirements.txt

    EXPOSE 18563

    CMD ["python3", "cdn_traffic_exporter.py"]
    ```  
- **docker-compose service part:**  
    ```
    cdn_traffic_exporter:
      container_name: cdn_traffic_exporter
      build:
        context: ./cdn_traffic_exporter
      ports:
        - "18563:18563"
      networks:
        - monitor
    ```

## Restarting service  
- If you have update on code  
    These command are used to delete and rebuild image,because there are no volume to mount ,so you have to clear the image and rebuild to start the service  
    ```
    docker stop cdn_traffic_exporter
    docker rm cdn_traffic_exporter
    docker rmi prometheus-cdn_traffic_exporter
    ```
    back to prometheus folder
    ```
    docker-compose up -d cdn_traffic_exporter
    ```
    then the service is up  
    
- no update on code  
    docker restart cdn_traffic_exporter
