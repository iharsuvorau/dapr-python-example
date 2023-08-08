# Using Dapr in Python applications

This example repository shows how to use Dapr in Python applications.

The idea is to have a task service that queries the weather service for the weather in a given location.

Communication between two services is decoupled using a message queue (RabbitMQ). Redis is used to cache the state of the task service.

To use the input binding component, a cron job is introduced that calls the weather service every 5 seconds to prefetch weather data for Estonia.

```mermaid
graph LR
    subgraph Queue
        weather_request[Weather Request Topic]
        weather_result[Weather Result Topic]
    end

    subgraph Cache
        Redis
    end

    subgraph Task Service
        fastapi[FastAPI]

        subgraph Dapr[Dapr]
            metrics[Prometheus Metrics]
        end
    end

    subgraph Weather Service
        fastapi2[FastAPI]
        
        subgraph Dapr2[Dapr]
            metrics2[Prometheus Metrics]
        end
    end

    prometheus[Prometheus] --> metrics
    prometheus[Prometheus] --> metrics2

    cron[Cron Input Binding]

    request([HTTP Request]) --> fastapi
    fastapi -- publishes to --> weather_request
    fastapi -- saves in --> Redis
    fastapi -- subscribes to --> weather_result

    fastapi2 -- subscribes to --> weather_request
    fastapi2 -- publishes to --> weather_result
    cron -- calls --> fastapi2
    cron -- every 5 seconds --> cron
    fastapi2 -- prefetches weather --> fastapi2


```

## Getting Started

Initialize Dapr and start the infrastructure:

```shell
dapr init
./start-infrastructure.sh # starts additional components, e.g. RabbitMQ
```

In a new terminal, run the first service:

```shell
cd task-service && ./start.sh 
```

In another terminal, run the second service:

```shell
cd ../weather-service && ./start.sh
```

Query the task service:

```shell
curl http://localhost:8000/weather/tartu -X POST
# after a few seconds
curl http://localhost:8000/weather/tartu
```

## Used Dapr building blocks

The following Dapr building blocks are used in this example (more to come):

- [ ] Service invocation
- [x] State management
- [x] Publish & subscribe messaging
- [x] Bindings
- [ ] Actors
- [x] Observability
- [x] Secrets management
- [ ] Configuration
- [ ] Distributed lock
- [ ] Workflow
- [ ] Cryptography
