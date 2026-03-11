from homeassistant.components.sensor import SensorEntity
from homeassistant.core import callback

from .const import DOMAIN, EVENT_EARTHQUAKE


async def async_setup_entry(hass, entry, async_add_entities):

    sensor = EarthquakeSensor(hass)

    async_add_entities([sensor])


class EarthquakeSensor(SensorEntity):

    _attr_name = "Earthquake"
    _attr_native_unit_of_measurement = "M"

    def __init__(self, hass):

        self.hass = hass
        self._state = None
        self._attrs = {}

    async def async_added_to_hass(self):

        @callback
        def handle_event(event):

            data = event.data

            self._state = data["magnitude"]

            self._attrs = {
                "distance_km": data["distance_km"],
                "region": data["region"],
                "lat": data["lat"],
                "lon": data["lon"],
                "time": data["time"]
            }

            self.async_write_ha_state()

        self.hass.bus.async_listen(
            EVENT_EARTHQUAKE,
            handle_event
        )

    @property
    def native_value(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attrs
