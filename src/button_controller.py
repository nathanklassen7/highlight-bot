import time
import threading
from gpiozero import Button
from event_bus import EventBus, EventType

BUTTON_PIN = 3
LONG_PRESS_TIME = 1.0
DEBOUNCE_S = 0.05


class ButtonController:
    def __init__(self, event_bus: EventBus):
        self._event_bus = event_bus
        self._press_time: float | None = None
        self._lock = threading.Lock()
        self._button = Button(BUTTON_PIN, pull_up=True, bounce_time=DEBOUNCE_S)

    def start(self):
        self._button.when_pressed = self._on_release
        self._button.when_released = self._on_press

    def stop(self):
        self._button.when_pressed = None
        self._button.when_released = None

    def _on_press(self):
        print("button down")
        with self._lock:
            self._press_time = time.monotonic()

    def _on_release(self):
        print("button up")
        with self._lock:
            if self._press_time is not None:
                hold_duration = time.monotonic() - self._press_time
                self._press_time = None
                if hold_duration >= LONG_PRESS_TIME:
                    print(f"long press ({hold_duration:.2f}s)")
                    self._event_bus.emit(EventType.BUTTON_LONG_PRESS)
                else:
                    print(f"short press ({hold_duration:.2f}s)")
                    self._event_bus.emit(EventType.BUTTON_SHORT_PRESS)

    def cleanup(self):
        self.stop()
        self._button.close()
