from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):

    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([SeismicSensor(coordinator)])


class SeismicSensor(CoordinatorEntity, SensorEntity):

    _attr_name = "Earthquake"
    _attr_native_unit_of_measurement = "M"

    def __init__(self, coordinator):
        super().__init__(coordinator)

    @property
    def native_value(self):
        if self.coordinator.data:
            return self.coordinator.data["magnitude"]

    @property
    def extra_state_attributes(self):
        if not self.coordinator.data:
            return {}

        return {
            "location": self.coordinator.data["location"],
            "time": self.coordinator.data["time"]
        }
