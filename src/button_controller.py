import time
import threading
import RPi.GPIO as GPIO
from event_bus import EventBus, EventType

BUTTON_PIN = 3
LONG_PRESS_TIME = 1.0
DEBOUNCE_MS = 50


class ButtonController:
    def __init__(self, event_bus: EventBus):
        self._event_bus = event_bus
        self._press_time: float | None = None
        self._lock = threading.Lock()

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(BUTTON_PIN, GPIO.IN, GPIO.PUD_UP)

    def start(self):
        GPIO.add_event_detect(
            BUTTON_PIN, GPIO.BOTH,
            callback=self._on_edge,
            bouncetime=DEBOUNCE_MS,
        )

    def stop(self):
        GPIO.remove_event_detect(BUTTON_PIN)

    def _on_edge(self, channel: int):
        pressed = GPIO.input(BUTTON_PIN)
        with self._lock:
            if pressed:
                self._press_time = time.monotonic()
            elif self._press_time is not None:
                hold_duration = time.monotonic() - self._press_time
                self._press_time = None
                if hold_duration >= LONG_PRESS_TIME:
                    self._event_bus.emit(EventType.BUTTON_LONG_PRESS)
                else:
                    self._event_bus.emit(EventType.BUTTON_SHORT_PRESS)

    def cleanup(self):
        self.stop()
        GPIO.cleanup()
