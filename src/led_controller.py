import time
import threading
import RPi.GPIO as GPIO
from event_bus import State

OUTPUT_PIN_MAP = {
    "on": 22,
    "record": 23,
    "write": 27,
}

FLASH_SPEED = 0.2
TRANSITION_FLASH_COUNT = 3
ERROR_FLASH_COUNT = 10


class LedController:
    def __init__(self):
        self._state = State.IDLE
        self._lock = threading.Lock()
        self._running = False
        self._thread: threading.Thread | None = None
        self._transient: str | None = None
        self.timeout_warning = False

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        for pin in OUTPUT_PIN_MAP.values():
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)

    def _write(self, led_name: str, on: bool):
        GPIO.output(OUTPUT_PIN_MAP[led_name], GPIO.HIGH if on else GPIO.LOW)

    def set_state(self, state: State):
        with self._lock:
            self._state = state

    def play_transition(self, pattern: str):
        """Play a one-shot pattern: 'start', 'stop', 'saved', or 'error'."""
        with self._lock:
            self._transient = pattern

    def start(self):
        self._running = True
        self._write("on", True)
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
        for pin in OUTPUT_PIN_MAP.values():
            GPIO.output(pin, GPIO.LOW)

    def _run(self):
        while self._running:
            with self._lock:
                transient = self._transient
                self._transient = None
                state = self._state

            if transient:
                self._play_pattern(transient)
                continue

            if state == State.IDLE:
                self._write("record", False)
                self._write("write", False)
            elif state == State.RECORDING:
                if self.timeout_warning:
                    # flash flash pause: on off on off off off
                    phase = int(time.time() / 0.2) % 6
                    flash = phase in (0, 2)
                else:
                    flash = int(time.time()) % 2 == 0
                self._write("record", flash)
                self._write("write", False)
            elif state == State.SAVING:
                self._write("record", False)
                self._write("write", True)

            time.sleep(0.1)

    def _play_pattern(self, pattern: str):
        led = "record" if pattern in ("start", "stop") else "write"
        count = {
            "start": TRANSITION_FLASH_COUNT,
            "stop": TRANSITION_FLASH_COUNT * 2,
            "saved": TRANSITION_FLASH_COUNT,
            "error": ERROR_FLASH_COUNT,
        }.get(pattern, TRANSITION_FLASH_COUNT)

        for _ in range(count):
            self._write(led, False)
            time.sleep(FLASH_SPEED)
            self._write(led, True)
            time.sleep(FLASH_SPEED)
        self._write(led, False)

        if pattern == "start":
            time.sleep(FLASH_SPEED * 2)
