import time
import threading
from typing import Callable
from gpiozero import Button
from event_bus import EventBus, EventType, State

BUTTON_PIN = 3
LONG_PRESS_TIME = 1
DEBOUNCE_S = 0.05


class ButtonController:
    def __init__(self, event_bus: EventBus, get_state: Callable[[], State]):
        self._event_bus = event_bus
        self._get_state = get_state
        self._press_time: float | None = None
        self._long_press_fired = False
        self._long_press_timer: threading.Timer | None = None
        self._lock = threading.Lock()
        self._button = Button(BUTTON_PIN, pull_up=True, bounce_time=DEBOUNCE_S)

    def start(self):
        # gpiozero's "pressed"/"released" callbacks are inverted relative to
        # our wiring, so swap them to match the physical button.
        self._button.when_pressed = self._on_release
        self._button.when_released = self._on_press

    def stop(self):
        self._button.when_pressed = None
        self._button.when_released = None
        with self._lock:
            self._cancel_long_press_timer_locked()
            self._press_time = None

    def _on_press(self):
        print("button down")
        with self._lock:
            self._press_time = time.monotonic()
            self._long_press_fired = False
            self._cancel_long_press_timer_locked()

            if self._get_state() != State.RECORDING:
                # Not recording: start immediately on press, no hold required.
                self._press_time = None
                print("short press (immediate)")
                self._event_bus.emit(EventType.BUTTON_SHORT_PRESS)
                return

            # Recording: arm a timer so we can stop as soon as the hold
            # threshold is reached, without waiting for the release.
            self._long_press_timer = threading.Timer(
                LONG_PRESS_TIME, self._on_long_press_timeout
            )
            self._long_press_timer.daemon = True
            self._long_press_timer.start()

    def _on_release(self):
        print("button up")
        with self._lock:
            self._cancel_long_press_timer_locked()
            if self._press_time is None:
                # Either we already emitted a short press immediately on
                # press-down (not-recording case) or the long-press timer
                # has already fired -- nothing left to do.
                return
            hold_duration = time.monotonic() - self._press_time
            self._press_time = None
            if self._long_press_fired:
                return
            print(f"short press ({hold_duration:.2f}s)")
            self._event_bus.emit(EventType.BUTTON_SHORT_PRESS)

    def _on_long_press_timeout(self):
        with self._lock:
            if self._press_time is None:
                # Button was released (or state reset) before the timer ran.
                return
            self._long_press_fired = True
            self._press_time = None
            self._long_press_timer = None
            print(f"long press ({LONG_PRESS_TIME:.2f}s)")
            self._event_bus.emit(EventType.BUTTON_LONG_PRESS)

    def _cancel_long_press_timer_locked(self):
        timer = self._long_press_timer
        if timer is not None:
            timer.cancel()
            self._long_press_timer = None

    def cleanup(self):
        self.stop()
        self._button.close()
