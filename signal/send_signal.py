import asyncio
import json
import logging
from urllib.parse import urlparse
import websockets


logger = logging.getLogger("command_injection_client")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


class SignalClient:
    def __init__(self, room, client_id=None, host=None):
        if client_id is None and host is None and isinstance(room, str):
            parsed = urlparse(room)
            if parsed.scheme in {"ws","wss"}:
                parts = [part for part in parsed.path.split("/") if part]
                if len(parts) >= 3 and parts[0] == "ws":
                    self.room = parts[1]
                    self.client_id = parts[2]
                    self.host = parsed.netloc
                    self.url = room
                    self.websocket = None
                    self.message_handlers = []
                    self.message_handler = None
                    return

        if client_id is None or host is None:
            raise TypeError(
                "Signal requires either a websocket URL or room/client_id/host"
            )

        self.room = room
        self.client_id = client_id
        self.host = host

        parsed = urlparse(host)
        if parsed.scheme in {"http","https","ws","wss"}:
            scheme = "wss" if parsed.scheme == "https" else "ws"
            netloc = parsed.netloc or parsed.path
            self.url = f"{scheme}://{netloc}/ws/{room}/{client_id}"
        else:
            self.url = f"ws://{host}/ws/{room}/{client_id}"

        self.websocket = None
        self.message_handlers = []
        self.message_handler = None

    async def connect(self):
        logger.info("Connecting to signaling server at %s", self.url)
        self.websocket = await websockets.connect(
            self.url
        )

        logger.info("Connected to signaling server at %s", self.url)

        asyncio.create_task(
            self.listen()
        )

    def add_message_handler(self, message_handler):
        self.message_handlers.append(message_handler)

    async def listen(self):
        logger.exception(f"Signal listener failed")

    async def handle_message(self, message):
        pass

    async def send(self, type_, target=None, data=None):
        if isinstance(type_, dict):
            packet = dict(type_)
            packet.setdefault("sender", self.client_id)
        else:
            packet = {
                "type": type_,
                "sender": self.client_id,
                "target": target,
                "data": data
            }

        logger.debug(f"Sending signaling packet: {packet}")
        await self.websocket.send(json.dumps(packet))

    async def close(self):
        if self.websocket:
            await self.websocket.close()















