#!/usr/bin/env bash

docker run -d -p 5672:5672 -p 15672:15672 --name dapr-rabbitmq rabbitmq:3-management-alpine
docker run -d -p 8080:8080 --name dapr-prometheus -v $(pwd)/prometheus.yaml:/etc/prometheus/prometheus.yaml prom/prometheus --config.file=/etc/prometheus/prometheus.yaml --web.listen-address=:8080