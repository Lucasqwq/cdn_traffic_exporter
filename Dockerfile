FROM python:3.11-slim

ENV TZ=Asia/Taipei

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /app

COPY . .

RUN python3 -m pip install -r requirements.txt

EXPOSE 18563

CMD ["python3", "cdn_traffic_exporter.py"]
