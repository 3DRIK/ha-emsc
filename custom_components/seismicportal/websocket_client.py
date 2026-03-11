import asyncio
import json
import math
import logging
import websockets

from .const import WS_URL, EVENT_EARTHQUAKE

_LOGGER = logging.getLogger(__name__)


class SeismicListener:
    """Listener for seismicportal.eu websocket events."""

    def __init__(self, hass, lat, lon, radius_km, min_magnitude):
        self.hass = hass
        self.center_lat = lat
        self.center_lon = lon
        self.radius_km = radius_km
        self.min_mag = min_magnitude

        self.seen_ids = set()

    def distance_km(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two lat/lon points in km (Haversine)."""
        r = 6371  # Earth radius in km
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
        """Start listening to the websocket in an infinite loop."""
        while True:
            try:
                async with websockets.connect(WS_URL) as ws:
                    _LOGGER.info("Connected to SeismicPortal websocket")

                    while True:
                        msg = await ws.recv()
                        data = json.loads(msg)

                        if "data" not in data:
                            continue

                        event = data["data"]

                        # unikátny ID zemetrasenia
                        props = event["properties"]
                        event_id = props["unid"]

                        if event_id in self.seen_ids:
                            continue
                        self.seen_ids.add(event_id)

                        # súradnice z geometry
                        coords = event["geometry"]["coordinates"]
                        lon = float(coords[0])
                        lat = float(coords[1])
                        # depth = float(coords[2])  # voliteľné

                        mag = float(props["mag"])
                        region = props.get("flynn_region")
                        time = props.get("time")

                        # filtruj podľa min_magnitude a radius
                        distance = self.distance_km(self.center_lat, self.center_lon, lat, lon)
                        if mag < self.min_mag or distance > self.radius_km:
                            continue

                        # pošli event do Home Assistant
                        payload = {
                            "magnitude": mag,
                            "distance_km": round(distance, 1),
                            "region": region,
                            "lat": lat,
                            "lon": lon,
                            "time": time,
                        }

                        self.hass.bus.async_fire(EVENT_EARTHQUAKE, payload)

            except Exception as e:
                _LOGGER.error("Websocket error: %s", e)
                await asyncio.sleep(10)  # reconnect po 10s
