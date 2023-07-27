import json
import logging
from dataclasses import dataclass
from pathlib import Path

import httpx
from dapr.clients import DaprClient
from fastapi import FastAPI
from lxml import etree

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI()
app.openapi()["info"]["title"] = "Weather Service"
app.state.logger = logger


@app.get("/dapr/subscribe")
async def subscribe():
    app.state.logger.info("Subscribing to pubsub")
    return [
        {
            "pubsubname": "pubsub",
            "topic": "weather",
            "route": "weather",
        }
    ]


@dataclass
class Event:
    location: str


@app.post("/weather")
async def weather(raw_event: dict):
    app.state.logger.info(f"Received weather event: {raw_event}")
    event = Event(**json.loads(raw_event["data"]))
    return await handle_location(event.location)


async def handle_location(location: str):
    temperature, phenomenon = get_weather(location)
    if temperature is None:
        return

    result = {
        "location": location,
        "temperature": temperature,
        "phenomenon": phenomenon,
    }

    with DaprClient() as client:
        response = client.publish_event(
            pubsub_name="pubsub",
            topic_name="weather-result",
            data=json.dumps(result),
        )
        logger.info(f"Published weather result: {response}")


def get_weather(location: str):
    weather_path = Path("weather.xml")

    if not weather_path.exists():
        xml = fetch_weather()
        weather_path.write_text(xml)
        xml = xml.encode()
    else:
        xml = weather_path.read_bytes()

    for name, temperature, phenomenon in parse_weather(xml):
        if location.lower() in name.lower():
            return temperature, phenomenon


def fetch_weather() -> str:
    api_url = "https://www.ilmateenistus.ee/ilma_andmed/xml/observations.php"
    response = httpx.get(api_url)
    response.raise_for_status()
    xml = response.text
    return xml


def parse_weather(xml: bytes):
    """
    Sample XML response:

    <observations timestamp="1690406026">
      <station>
      <name>Kuressaare linn</name>
      <wmocode/>
      <longitude>22.48944444411111</longitude>
      <latitude>58.26416666666667</latitude>
      <phenomenon/>
      <visibility/>
      <precipitations/>
      <airpressure/>
      <relativehumidity>87</relativehumidity>
      <airtemperature>13.7</airtemperature>
      <winddirection/>
      <windspeed/>
      <windspeedmax/>
      <waterlevel/>
      <waterlevel_eh2000/>
      <watertemperature/>
      <uvindex/>
      <sunshineduration/>
      <globalradiation/>
      </station>
      ...
    </observations>
    """

    root = etree.fromstring(xml)
    stations = root.xpath("//station")
    for station in stations:
        name = station.xpath("name")[0].text
        temperature = station.xpath("airtemperature")[0].text
        phenomenon = station.xpath("phenomenon")[0].text
        yield name, temperature, phenomenon


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8010, log_level="info")
