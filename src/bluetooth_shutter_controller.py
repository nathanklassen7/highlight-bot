import logging
import os
import threading

import evdev
from evdev import ecodes

from event_bus import EventBus, EventType

logger = logging.getLogger(__name__)

# Bluetooth camera-shutter remotes expose two buttons that present as
# standard HID keys. On the AB-Shutter / generic shutter remotes:
#   button 1 -> KEY_VOLUMEUP (115)
#   button 2 -> KEY_ENTER    (28)
SHORT_PRESS_KEY = ecodes.KEY_VOLUMEUP
LONG_PRESS_KEY = ecodes.KEY_ENTER

# evdev key event values
KEY_DOWN = 1
KEY_HOLD = 2
KEY_UP = 0

# How long to wait between attempts to (re)discover the input device.
# The remote may not be connected yet at startup, and bluetooth peers
# often disconnect when idle to save power.
DISCOVERY_RETRY_S = 2.0

# Optional substring (case-insensitive) used to disambiguate from other
# input devices (e.g. an attached keyboard). When unset we accept any
# device whose capability set includes both shutter keys.
DEVICE_NAME_HINT = os.environ.get("BT_SHUTTER_DEVICE_NAME", "")


class BluetoothShutterController:
    def __init__(self, event_bus: EventBus):
        self._event_bus = event_bus
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._device: evdev.InputDevice | None = None

    def start(self):
        if self._thread is not None:
            return
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run,
            name="BluetoothShutterController",
            daemon=True,
        )
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        # Closing the device unblocks the read_loop with an OSError.
        device = self._device
        if device is not None:
            try:
                device.ungrab()
            except Exception:
                pass
            try:
                device.close()
            except Exception:
                pass
        if self._thread is not None:
            self._thread.join(timeout=1.0)
            self._thread = None

    def cleanup(self):
        self.stop()

    def _run(self):
        while not self._stop_event.is_set():
            device = self._find_device()
            if device is None:
                self._stop_event.wait(DISCOVERY_RETRY_S)
                continue

            self._device = device
            logger.info(
                "Bluetooth shutter connected: %s (%s)", device.name, device.path
            )

            # Grab so the OS doesn't also act on volume-up / enter.
            try:
                device.grab()
            except Exception as e:
                logger.warning("Could not grab %s: %s", device.path, e)

            try:
                self._listen(device)
            except OSError as e:
                logger.warning("Bluetooth shutter disconnected: %s", e)
            except Exception:
                logger.exception("Bluetooth shutter listener crashed")
            finally:
                try:
                    device.ungrab()
                except Exception:
                    pass
                try:
                    device.close()
                except Exception:
                    pass
                self._device = None

    def _find_device(self) -> evdev.InputDevice | None:
        try:
            paths = evdev.list_devices()
        except Exception:
            logger.exception("Failed to enumerate input devices")
            return None

        for path in paths:
            try:
                device = evdev.InputDevice(path)
            except Exception:
                continue

            if (
                DEVICE_NAME_HINT
                and DEVICE_NAME_HINT.lower() not in device.name.lower()
            ):
                device.close()
                continue

            keys = set(device.capabilities().get(ecodes.EV_KEY, []))
            if SHORT_PRESS_KEY in keys and LONG_PRESS_KEY in keys:
                return device

            device.close()

        return None

    def _listen(self, device: evdev.InputDevice):
        for event in device.read_loop():
            if self._stop_event.is_set():
                return
            if event.type != ecodes.EV_KEY:
                continue
            # Only fire on the initial key-down; ignore auto-repeat (2)
            # and key-up (0) so a single button tap maps to a single
            # event regardless of how long the user holds it.
            if event.value != KEY_DOWN:
                continue
            self._handle_key(event.code)

    def _handle_key(self, code: int):
        if code == SHORT_PRESS_KEY:
            logger.info("BT shutter: short press (button 1)")
            self._event_bus.emit(EventType.BUTTON_SHORT_PRESS)
        elif code == LONG_PRESS_KEY:
            logger.info("BT shutter: long press (button 2)")
            self._event_bus.emit(EventType.BUTTON_LONG_PRESS)
