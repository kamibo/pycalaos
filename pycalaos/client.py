import json
import logging
import websockets

from .item import new_item
from .item.common import Event

_LOGGER = logging.getLogger(__name__)

class Room:
    """A room in the Calaos configuration"""

    def __init__(self, name: str, type: str):
        """Initialize the room

        Parameters:
            name (str):
                Name of the room

            type (str):
                Type of the room
        """
        self._name = name
        self._type = type
        self._items = []

    def __repr__(self):
        return f"{self._name} ({self._type}): {len(self._items)} items"

    @property
    def name(self):
        return self._name

    @property
    def type(self):
        return self._type

    @property
    def items(self):
        return self._items

    def _add_item(self, item):
        """Add a new item in the room

        Parameters:
            item (pycalaos.item.Item):
                The item to add

        Return nothing
        """
        self._items.append(item)


class _Conn:
    def __init__(self, uri):
        self._uri = f"{uri}/api"

    async def init(self):
        self._websocket = await websockets.connect(self._uri)

    async def send(self, request):
        await self._websocket.send(json.dumps(request))

    async def recv(self):
        message = await self._websocket.recv()
        return json.loads(message)


class Client:
    """A Calaos client"""

    def __init__(self, uri: str, username: str, password: str):
        """Initialize the client and load the home configuration and state.

        Parameters:
            uri (str):
                URI of the Calaos server (usually, "A.B.C.D")

            username (str):
                Username to connect to the Calaos server

            password (str):
                Password to connect to the Calaos server
        """
        self._uri = "ws://" + uri + ":5454"
        self._username = username
        self._password = password
        self._items = []

    async def init(self):
        self._conn = _Conn(self._uri)
        await self._conn.init()
        return await self.login()

    def __repr__(self):
        return f"Calaos Client with {len(self.rooms)} rooms"

    async def login(self):
        await self._conn.send({"msg": "login", "data":
                               {"cn_user": self._username,
                                "cn_pass": self._password}})
        resp = await self._conn.recv()

        if resp["data"]["success"] != "true":
            _LOGGER.error("Login error")
            return False
        _LOGGER.info("Connected")
        return True

    async def reload_home(self):
        """Reload the complete home configuration, resetting rooms and items

        This could be necessary if the Calaos server is reconfigured with
        Calaos Installer and the client is not restarted).

        Return nothing
        """
        _LOGGER.debug("Getting the whole home")
        await self._conn.send({"msg": "get_home"})

    async def wait(self):
        msg = await self._conn.recv()

        msg_type = msg["msg"]
        msg_data = msg["data"]

        print(f"Recv ===========> {msg_type} / {msg_data}\n")
        if msg_type == "get_home":
            self._handle_get_home(msg_data)
        elif msg_type == "set_state":
            if msg_data["success"] != "true":
                _LOGGER.error("Set state failed")
        elif msg_type == "event":
            return self._handle_event(msg_data)
        else:
            _LOGGER.debug(f"Msg ignored {msg}")

    def _handle_get_home(self, data):
        """Handle the complete home configuration, resetting rooms and items
        Return nothing
        """
        async def state_state_fn(id, value):
            _LOGGER.debug(f"Setting state \"{value}\" for {id}")
            await self._conn.send({"msg": "set_state",
                                   "data": {"id": id, "value": value}})

        _LOGGER.debug("Getting the whole home")
        rooms = []
        items = {}
        items_by_type = {}
        for roomData in data["home"]:
            room = Room(roomData["name"], roomData["type"])
            for itemData in roomData["items"]:
                item = new_item(itemData, room, state_state_fn)
                items[item._id] = item
                try:
                    items_by_type[type(item)].append(item)
                except KeyError:
                    items_by_type[type(item)] = [item]
                room._add_item(item)
            rooms.append(room)
        self._rooms = rooms
        self._items = items
        self._items_by_type = items_by_type

    def _handle_event(self, data):
        try:
            eventData = data["data"]
            itemID = eventData["id"]
            state = eventData["state"]
        except:
            _LOGGER.error(f"Bogus event: {data}")
            return

        try:
            item = self.items[itemID]
        except KeyError:
            _LOGGER.error(f"Poll received event with unknown ID: {data}")
            return

        changed = item.internal_from_event(state)
        if changed:
            _LOGGER.info(f"Internal status changed for {data}")
            return Event(item)

    @property
    def rooms(self):
        return self._rooms

    @property
    def items(self):
        """Items referenced by their IDs (dict of str: pycalaos.item.Item)"""
        return self._items

    @property
    def item_types(self):
        """Complete list of item types currently in use"""
        return list(self._items_by_type.keys())

    def items_by_type(self, type):
        """Return only the items of the given type"""
        try:
            return self._items_by_type[type]
        except KeyError:
            return []
