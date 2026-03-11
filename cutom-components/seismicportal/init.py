from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import SeismicCoordinator

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):

    coordinator = SeismicCoordinator(hass, entry.data)

    await coordinator.async_start()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    return True
