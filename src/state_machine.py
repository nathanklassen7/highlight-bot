import json
import time
from event_bus import Event, EventBus, EventType, State
from led_controller import LedController
from recording_manager import RecordingManager

SETTINGS_FILE = "settings.json"
DEFAULT_INACTIVITY_TIMEOUT = 2 * 60 * 60


class StateMachine:
    def __init__(
        self,
        event_bus: EventBus,
        led: LedController,
        recording: RecordingManager,
    ):
        self._event_bus = event_bus
        self._led = led
        self._recording = recording
        self.state = State.IDLE
        self._last_activity: float = 0
        self.inactivity_timeout: float = self._load_timeout()

        self._transitions: dict[tuple[State, EventType], callable] = {
            (State.IDLE, EventType.BUTTON_SHORT_PRESS): self._idle_to_recording,
            (State.IDLE, EventType.BUTTON_LONG_PRESS): self._idle_to_recording,
            (State.IDLE, EventType.SLACK_START): self._idle_to_recording,

            (State.RECORDING, EventType.BUTTON_SHORT_PRESS): self._recording_to_saving,
            (State.RECORDING, EventType.SLACK_CLIP): self._recording_to_saving,

            (State.RECORDING, EventType.BUTTON_LONG_PRESS): self._recording_to_idle,
            (State.RECORDING, EventType.SLACK_STOP): self._recording_to_idle,
            (State.RECORDING, EventType.INACTIVITY_TIMEOUT): self._recording_to_idle,
            (State.RECORDING, EventType.POKE): self._poke,

            (State.SAVING, EventType.ENCODE_OK): self._saving_done,
            (State.SAVING, EventType.ENCODE_FAIL): self._saving_failed,
        }

    def _load_timeout(self):
        try:
            with open(SETTINGS_FILE) as f:
                return json.load(f)["inactivity_timeout_hours"] * 3600
        except (FileNotFoundError, KeyError, ValueError):
            return DEFAULT_INACTIVITY_TIMEOUT

    def save_timeout(self):
        try:
            with open(SETTINGS_FILE) as f:
                settings = json.load(f)
        except (FileNotFoundError, ValueError):
            settings = {}
        settings["inactivity_timeout_hours"] = self.inactivity_timeout / 3600
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=4)
            f.write("\n")

    def run(self):
        """Main event loop -- blocks the calling thread."""
        while True:
            event = self._event_bus.wait(timeout=0.1)
            if event is None:
                self._check_inactivity_timeout()
                continue

            handler = self._transitions.get((self.state, event.type))
            if handler:
                handler(event)
            else:
                print(f"Ignoring {event.type.name} in state {self.state.name}")

    def _check_inactivity_timeout(self):
        if self.state != State.RECORDING:
            return
        elapsed = time.monotonic() - self._last_activity
        self._led.timeout_warning = elapsed >= self.inactivity_timeout - 300
        if elapsed >= self.inactivity_timeout:
            print("Stopping recording due to inactivity")
            self._event_bus.emit(EventType.INACTIVITY_TIMEOUT)

    def _idle_to_recording(self, event: Event):
        print("Starting recording")
        self._last_activity = time.monotonic()
        self._recording.start()
        self._led.play_transition("start")
        self.state = State.RECORDING
        self._led.set_state(State.RECORDING)

    def _recording_to_saving(self, event: Event):
        print("Saving clip")
        self._last_activity = time.monotonic()
        self._led.timeout_warning = False
        self.state = State.SAVING
        self._led.set_state(State.SAVING)
        self._recording.capture_and_encode()

    def _recording_to_idle(self, event: Event):
        print("Stopping recording")
        self._led.timeout_warning = False
        self._recording.stop()
        self._led.play_transition("stop")
        self.state = State.IDLE
        self._led.set_state(State.IDLE)

    def _saving_done(self, event: Event):
        print("Clip saved successfully")
        self._last_activity = time.monotonic()
        self._led.play_transition("saved")
        self._recording.restart_buffers()
        self.state = State.RECORDING
        self._led.set_state(State.RECORDING)

    def _poke(self, event: Event):
        print("Poke: refreshing buffers")
        self._last_activity = time.monotonic()
        self._led.timeout_warning = False
        self._recording.refresh_buffers()

    def _saving_failed(self, event: Event):
        print("Clip save failed")
        self._led.play_transition("error")
        self._recording.restart_buffers()
        self.state = State.RECORDING
        self._led.set_state(State.RECORDING)
