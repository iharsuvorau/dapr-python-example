#!/usr/bin/env bash

dapr run \
--app-id task-service \
--app-port 8000 \
--resources-path ../dapr/components \
poetry run python task_service/main.py