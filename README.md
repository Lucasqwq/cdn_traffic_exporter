# CDN Traffic Metrics Exporter

- 此專案是一個使用 `prometheus_client` 模組撰寫的流量表 Metrics Exporter。  
- 透過各家 CDN 廠商的 API 取得特定域名的流量資料，並將其轉換為 Prometheus 可用的 Metrics Value,再串接到 Grafana 的儀表板上，支援直接複製貼上至 Excel流量表。

## 前置需求
- **Python 環境**：基於 `python:3.8.10-slim` Docker 映像檔
- **套件需求**：需安裝 `requirements.txt` 中列出的 Python 套件
- **API 認證**：`config.py` 檔案中包含各家 CDN 廠商的 API 認證資訊
- **網宿 API 安裝包**：`cdnetworks` 資料夾包含網宿的 API SDK包
- **Dockerfile內容:**  
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

## 重啟服務
- 若有更改code  
    這些command是用來清除image,並重新build image使用的,因為沒有掛volume所以改code的時候得清除image再重新啟動  
    ```
    docker stop cdn_traffic_exporter
    docker rm cdn_traffic_exporter
    docker rmi prometheus-cdn_traffic_exporter
    ```
    再到prometheus資料夾下使用
    ```
    docker-compose up -d cdn_traffic_exporter
    ```
    就可以把服務起起來  
    
- 無改動code  
    直接docker restart cdn_traffic_exporter