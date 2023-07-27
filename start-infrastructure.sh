#!/usr/bin/env bash

docker run -d -p 5672:5672 -p 15672:15672 --name dpr-rabbitmq rabbitmq:3-management-alpine