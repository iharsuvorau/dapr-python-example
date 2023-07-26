from typing import Optional

from dapr.clients import DaprClient
from dapr.clients.grpc._response import DaprResponse

from task_service.weather_tasks.model import WeatherTask

DAPR_STORE_NAME = "statestore"


class WeatherTaskRepository:
    def __init__(self):
        self._client = DaprClient()

    def get_task(self, location: str) -> Optional[WeatherTask]:
        response = self._client.get_state(
            store_name=DAPR_STORE_NAME,
            key=location,
        )

        if len(response.data) > 0:
            task = WeatherTask.parse_raw(response.data)
            return task

        return None

    def create_task(self, location: str) -> DaprResponse:
        task = WeatherTask.new(location)
        return self._client.save_state(
            store_name=DAPR_STORE_NAME,
            key=location,
            value=task.to_bytes(),
        )

    def update_task(self, location: str, task: WeatherTask) -> DaprResponse:
        return self._client.save_state(
            store_name=DAPR_STORE_NAME,
            key=location,
            value=task,
        )

    def delete_task(self, location: str) -> DaprResponse:
        return self._client.delete_state(
            store_name=DAPR_STORE_NAME,
            key=location,
        )

    def close(self):
        self._client.close()
