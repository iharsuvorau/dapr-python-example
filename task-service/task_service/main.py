import json
import logging

from dapr.clients import DaprClient
from fastapi import FastAPI, HTTPException

from task_service.weather_tasks.model import TaskStatus, WeatherResult
from task_service.weather_tasks.repository import WeatherTaskRepository

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

repository = WeatherTaskRepository()


def lifespan(app: FastAPI):
    yield
    app.state.logger.info("Closing repository")
    repository.close()


app = FastAPI(lifespan=lifespan)
app.openapi()["info"]["title"] = "Weather Task Service"
app.state.logger = logger


@app.get("/weather/{location}")
async def get_task(location: str):
    return repository.get_task(location.lower())


@app.post("/weather/{location}")
async def create_task(location: str):
    location = location.lower()
    existing_task = repository.get_task(location)
    if existing_task is not None:
        return existing_task

    create_task_response = repository.create_task(location)

    with DaprClient() as client:
        publish_response = client.publish_event(
            pubsub_name="pubsub",
            topic_name="weather",
            data=json.dumps({"location": location}),
        )

    return {
        "create_task_response": create_task_response,
        "publish_response": publish_response,
    }


@app.delete("/weather/{location}")
async def delete_task(location: str):
    location = location.lower()

    if repository.get_task(location) is None:
        raise HTTPException(status_code=404, detail="Task not found")

    delete_task_response = repository.delete_task(location)

    return {
        "response": delete_task_response,
    }


@app.get("/dapr/subscribe")
async def subscribe():
    app.state.logger.info("Subscribing to pubsub")
    return [
        {
            "pubsubname": "pubsub",
            "topic": "weather-result",
            "route": "weather-result",
        }
    ]


@app.post("/weather-result")
async def weather_result(raw_event: dict):
    app.state.logger.info(f"Received weather result event: {raw_event}")
    result = WeatherResult(**json.loads(raw_event["data"]))
    repository.update_task(result.location, TaskStatus.COMPLETED, result)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
