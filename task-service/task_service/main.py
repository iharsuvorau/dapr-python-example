import logging
from dataclasses import dataclass
from typing import Optional

from fastapi import APIRouter, FastAPI

from task_service.weather_tasks.model import WeatherTask
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


router = APIRouter(prefix="/weather")


@dataclass
class WeatherResponse:
    location: str
    data: Optional[WeatherTask]


@router.get("/{location}")
async def get_task(location: str):
    task = repository.get_task(location.lower())
    return WeatherResponse(location=location, data=task)


@router.post("/")
async def create_task(location: str):
    location = location.lower()
    existing_task = repository.get_task(location)
    if existing_task is not None:
        return WeatherResponse(location=location, data=existing_task)
    return repository.create_task(location)


app.include_router(router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
