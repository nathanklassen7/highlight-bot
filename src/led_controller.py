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

RECORD_SEQUENCE_GAP = 0.1
RECORD_SEQUENCE_HOLD = 0.2
RECORD_SEQUENCE_CYCLES = 3


class LedController:
    def __init__(self):
        self._state = State.IDLE
        self._lock = threading.Lock()
        self._running = False
        self._thread: threading.Thread | None = None
        self._transient: str | None = None
        self._record_anchor = time.monotonic()
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
            if state == State.RECORDING and self._state != State.RECORDING:
                self._record_anchor = time.monotonic()
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

    def _all_off(self):
        for led_name in OUTPUT_PIN_MAP:
            self._write(led_name, False)

    def _play_record_start(self):
        """Cascade the LEDs on (write, power, record), hold, then clear."""
        for _ in range(RECORD_SEQUENCE_CYCLES):
            self._all_off()
            for led_name in ("write", "on", "record"):
                time.sleep(RECORD_SEQUENCE_GAP)
                self._write(led_name, True)
            time.sleep(RECORD_SEQUENCE_HOLD)
            self._all_off()
        self._write("on", True)

    def _play_record_stop(self):
        """Mirror of the start cascade: all on, then clear in reverse."""
        for _ in range(RECORD_SEQUENCE_CYCLES):
            for led_name in OUTPUT_PIN_MAP:
                self._write(led_name, True)
            time.sleep(RECORD_SEQUENCE_HOLD)
            for led_name in ("record", "on", "write"):
                self._write(led_name, False)
                time.sleep(RECORD_SEQUENCE_GAP)
        self._write("on", True)

    def _run(self):
        while self._running:
            with self._lock:
                transient = self._transient
                self._transient = None
                state = self._state
                record_anchor = self._record_anchor

            if transient:
                self._play_pattern(transient)
                with self._lock:
                    if self._state == State.RECORDING:
                        self._record_anchor = time.monotonic()
                continue

            if state == State.IDLE:
                self._write("record", False)
                self._write("write", False)
            elif state == State.RECORDING:
                elapsed = time.monotonic() - record_anchor
                if self.timeout_warning:
                    # flash flash pause: on off on off off off
                    phase = int(elapsed / 0.2) % 6
                    flash = phase in (0, 2)
                else:
                    flash = int(elapsed) % 2 == 0
                self._write("record", flash)
                self._write("write", False)
            elif state == State.SAVING:
                self._write("record", False)
                self._write("write", True)

            time.sleep(0.1)

    def _flash_write(self, count: int):
        for _ in range(count):
            self._write("write", False)
            time.sleep(FLASH_SPEED)
            self._write("write", True)
            time.sleep(FLASH_SPEED)
        self._write("write", False)

    def _play_save_success(self):
        """Flash the write LED to confirm a clip was saved."""
        self._flash_write(TRANSITION_FLASH_COUNT)

    def _play_save_error(self):
        """Flash the write LED rapidly to signal a failed save."""
        self._flash_write(ERROR_FLASH_COUNT)

    def _play_pattern(self, pattern: str):
        if pattern == "start":
            self._play_record_start()
        elif pattern == "stop":
            self._play_record_stop()
        elif pattern == "saved":
            self._play_save_success()
        elif pattern == "error":
            self._play_save_error()
