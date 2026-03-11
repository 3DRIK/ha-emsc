from .websocket_client import SeismicListener

async def async_setup_entry(hass, entry):

    config = entry.data

    listener = SeismicListener(
        hass,
        config["latitude"],
        config["longitude"],
        config["radius"],
        config["min_magnitude"]
    )

    hass.loop.create_task(listener.start())

    return True
