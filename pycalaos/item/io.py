from enum import Enum, StrEnum

from .common import Item


class InPlageHoraire(Item):
    def _translate(self, state: str):
        return state == "true"


class InputAnalog(Item):
    def _translate(self, state: str):
        return float(state)


class InputString(Item):
    pass


class InputSwitch(Item):
    def _translate(self, state: str):
        return state == "true"


class InputSwitchLongPressState(Enum):
    NONE = 0
    SHORT = 1
    LONG = 2


class InputSwitchLongPress(Item):
    def _translate(self, state: str):
        return InputSwitchLongPressState(int(state))


class InputSwitchTripleState(Enum):
    NONE = 0
    SINGLE = 1
    DOUBLE = 2
    TRIPLE = 3


class InputSwitchTriple(Item):
    def _translate(self, state: str):
        return InputSwitchTripleState(int(state))


class InputTemp(Item):
    def _translate(self, state: str):
        return float(state)


class InputTime(Item):
    def _translate(self, state: str):
        return state == "true"


class InputTimer(Item):
    def _translate(self, state: str):
        return state == "true"

    async def start(self):
        await self._send("start")

    async def stop(self):
        await self._send("stop")

    async def reset(self, hours, minutes, seconds, milliseconds):
        await self._send(f"{hours}:{minutes}:{seconds}:{milliseconds}")


class InternalBool(Item):
    def _translate(self, state: str):
        return state == "true"

    async def true(self):
        await self._send("true")
        self._state = True

    async def false(self):
        await self._send("false")
        self._state = False

    async def toggle(self):
        await self._send("toggle")

    async def impulse(self, *pattern):
        cmd = "impulse"
        for step in pattern:
            cmd += f" {step}"
        await self._send(cmd)
        print(cmd)


class InternalInt(Item):
    def _translate(self, state: str):
        return int(state)

    async def set(self, value):
        await self._send(f"{value}")
        self._state = value

    async def inc(self, value=0):
        if value == 0:
            await self._send("inc")
        else:
            await self._send(f"inc {value}")

    async def dec(self, value=0):
        if value == 0:
            await self._send("dec")
        else:
            await self._send(f"dec {value}")


class InternalString(Item):
    async def set(self, value):
        await self._send(value)
        self._state = value


class OutputLight(Item):
    def _translate(self, state: str):
        return state == "true"

    async def true(self):
        await self._send("true")
        self._state = True

    async def false(self):
        await self._send("false")
        self._state = False

    async def toggle(self):
        await self._send("toggle")

    async def impulse(self, *pattern):
        cmd = "impulse"
        for step in pattern:
            cmd += f" {step}"
        await self._send(cmd)
        print(cmd)


class OutputLightDimmer(Item):
    def _translate(self, state: str):
        value = int(state)
        if value > 100:
            value = 100
        elif value < 0:
            value = 0
        return value

    async def true(self):
        await self._send("true")

    async def false(self):
        await self._send("false")
        self._state = 0

    async def toggle(self):
        await self._send("toggle")

    async def impulse(self, *pattern):
        cmd = "impulse"
        for step in pattern:
            cmd += f" {step}"
        await self._send(cmd)
        print(cmd)

    async def set_off(self, value):
        if value < 1:
            value = 1
        elif value > 100:
            value = 100
        await self._send(f"set off {value}")
        if self._state != 0:
            self._state = value

    async def set(self, value):
        if value < 1:
            value = 1
        elif value > 100:
            value = 100
        await self._send(f"set {value}")
        self._state = value

    async def up(self, value):
        if value < 1:
            value = 1
        elif value > 100:
            value = 100
        await self._send(f"up {value}")

    async def down(self, value):
        if value < 1:
            value = 1
        elif value > 100:
            value = 100
        await self._send(f"down {value}")

    async def hold_press(self):
        await self._send("hold press")

    async def hold_stop(self):
        await self._send("hold stop")


class OutputShutterAction(StrEnum):
    STATIONARY = ""
    UP = "up"
    DOWN = "down"
    STOP = "stop"
    CALIBRATION = "calibrate"


class OutputShutterSmart(Item):
    def _translate(self, state: str):
        infos = state.split()
        return {"action": OutputShutterAction(infos[0]), "position": int(infos[1])}

    async def stop(self):
        await self._send("stop")

    async def toggle(self):
        await self._send("toggle")

    async def impulse_up(self, duration):
        await self._send(f"impulse up {duration}")

    async def impulse_down(self, duration):
        await self._send(f"impulse down {duration}")

    async def set(self, value):
        if value < 1:
            value = 1
        elif value > 100:
            value = 100
        await self._send(f"set {value}")

    async def up(self, value=0):
        if value == 0:
            await self._send("up")
            return
        else:
            if value < 1:
                value = 1
            elif value > 100:
                value = 100
            await self._send(f"up {value}")

    async def down(self, value=0):
        if value == 0:
            await self._send("down")
            return
        else:
            if value < 1:
                value = 1
            elif value > 100:
                value = 100
            await self._send(f"down {value}")

    async def calibrate(self):
        await self._send("calibrate")


class OutputShutter(Item):
    def _translate(self, state: str):
        return state == "true"

    async def stop(self):
        await self._send("stop")

    async def toggle(self):
        await self._send("toggle")

    async def up(self):
        await self._send("up")

    async def down(self):
        await self._send("down")


class Scenario(Item):
    def _translate(self, state: str):
        return state == "true"

    async def true(self):
        await self._send("true")
        self._state = True

    async def false(self):
        await self._send("false")
        self._state = False
