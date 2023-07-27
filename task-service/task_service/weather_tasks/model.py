import json
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class TaskStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"

    def __str__(self):
        return self.name

    def default(self, o):
        return o.__dict__


@dataclass
class WeatherResult:
    location: str
    temperature: int
    phenomenon: str

    def __str__(self):
        return json.dumps(self.__dict__)

    @staticmethod
    def empty():
        return WeatherResult(
            location=None,
            temperature=None,
            phenomenon=None,
        )

    def json(self) -> str:
        return json.dumps(self.__dict__, cls=CustomJSONEncoder)


@dataclass
class WeatherTask:
    location: str
    status: TaskStatus
    result: Optional[WeatherResult]

    @staticmethod
    def new(location: str):
        return WeatherTask(
            location=location,
            status=TaskStatus.PENDING,
            result=WeatherResult.empty(),
        )

    def to_bytes(self) -> bytes:
        return self.json().encode("utf-8")

    def json(self) -> str:
        return json.dumps(self.__dict__, cls=CustomJSONEncoder)


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__


class CustomJSONDecoder(json.JSONDecoder):
    def default(self, o):
        return o.__dict__
