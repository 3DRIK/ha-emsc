import asyncio
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.core import HomeAssistant
from geopy.distance import geodesic
from .websocket_client import SeismicWebSocket
from .const import CONF_LAT, CONF_LON, CONF_RADIUS, CONF_MAG

class SeismicCoordinator(DataUpdateCoordinator):

    def __init__(self, hass: HomeAssistant, config):

        super().__init__(hass, None, name="SeismicPortal")

        self.lat = config[CONF_LAT]
        self.lon = config[CONF_LON]
        self.radius = config[CONF_RADIUS]
        self.min_mag = config[CONF_MAG]

        self.data = None

    async def async_start(self):

        ws = SeismicWebSocket(self.process_event)

        self.hass.loop.create_task(ws.connect())

    async def process_event(self, event):

        mag = float(event["properties"]["mag"])
        lat = float(event["geometry"]["coordinates"][1])
        lon = float(event["geometry"]["coordinates"][0])

        distance = geodesic((self.lat, self.lon), (lat, lon)).km

        if mag >= self.min_mag and distance <= self.radius:

            self.data = {
                "magnitude": mag,
                "location": event["properties"]["flynn_region"],
                "time": event["properties"]["time"]
            }

            self.async_set_updated_data(self.data)
