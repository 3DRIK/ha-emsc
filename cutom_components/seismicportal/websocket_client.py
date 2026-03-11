import json
import math
import logging
import asyncio
import websockets

from .const import WS_URL

_LOGGER = logging.getLogger(__name__)


class SeismicListener:

    def __init__(self, hass, lat, lon, radius_km, min_magnitude):

        self.hass = hass
        self.center_lat = lat
        self.center_lon = lon
        self.radius_km = radius_km
        self.min_mag = min_magnitude

        self.seen_ids = set()

    def distance_km(self, lat1, lon1, lat2, lon2):

        r = 6371

        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)

        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(dlon / 2) ** 2
        )

        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return r * c

    async def start(self):

        while True:

            try:

                async with websockets.connect(WS_URL) as ws:

                    _LOGGER.info("Connected to EMSC websocket")

                    while True:

                        msg = await ws.recv()
                        data = json.loads(msg)

                        if "data" not in data:
                            continue

                        event = data["data"]

                        event_id = event.get("unid")

                        if event_id in self.seen_ids:
                            continue

                        self.seen_ids.add(event_id)

                        lat = float(event["lat"])
                        lon = float(event["lon"])
                        mag = float(event["mag"])

                        if mag < self.min_mag:
                            continue

                        dist = self.distance_km(
                            self.center_lat,
                            self.center_lon,
                            lat,
                            lon
                        )

                        if dist > self.radius_km:
                            continue

                        payload = {
                            "magnitude": mag,
                            "distance_km": round(dist, 1),
                            "region": event.get("flynn_region"),
                            "lat": lat,
                            "lon": lon,
                            "time": event.get("time")
                        }

                        self.hass.bus.async_fire(
                            "seismicportal_earthquake",
                            payload
                        )

            except Exception as e:

                _LOGGER.error("Websocket error: %s", e)

                await asyncio.sleep(10)
