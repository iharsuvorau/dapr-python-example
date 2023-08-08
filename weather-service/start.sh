#!/usr/bin/env bash

dapr run \
--app-id weather-service \
--app-port 8010 \
--metrics-port 9091 \
--resources-path ../dapr/components \
poetry run python weather_service/main.py