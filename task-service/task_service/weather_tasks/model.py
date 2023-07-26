from enum import Enum, auto
from typing import Optional

from pydantic import BaseModel


class TaskStatus(Enum):
    PENDING = auto()
    COMPLETED = auto()


class WeatherTask(BaseModel):
    location: str
    status: TaskStatus
    response: Optional[bytes]

    @staticmethod
    def new(location: str):
        return WeatherTask(
            location=location,
            status=TaskStatus.PENDING,
            response=None,
        )

    def to_bytes(self) -> bytes:
        return self.model_dump_json().encode("utf-8")
