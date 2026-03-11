import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, CONF_LAT, CONF_LON, CONF_RADIUS, CONF_MAG

class SeismicPortalConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1

    async def async_step_user(self, user_input=None):

        if user_input is not None:
            return self.async_create_entry(
                title="Seismic Portal",
                data=user_input
            )

        schema = vol.Schema({
            vol.Required(CONF_LAT): float,
            vol.Required(CONF_LON): float,
            vol.Required(CONF_RADIUS, default=1): int,
            vol.Required(CONF_MAG, default=2.0): float,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema
        )
