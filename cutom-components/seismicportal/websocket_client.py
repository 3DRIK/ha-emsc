import asyncio
import json
import websockets
from .const import WS_URL

class SeismicWebSocket:

    def __init__(self, callback):
        self.callback = callback

    async def connect(self):

        async with websockets.connect(WS_URL) as ws:

            while True:
                msg = await ws.recv()
                data = json.loads(msg)

                if data.get("action") == "create":
                    await self.callback(data["data"])
