FROM python:3.8.10-slim

WORKDIR /app

COPY . .

RUN python3 -m pip install -r requirements.txt

EXPOSE 18563

CMD ["python3", "cdn_traffic_exporter.py"]