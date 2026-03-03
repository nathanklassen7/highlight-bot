from event_bus import Event, EventBus, EventType, State
from led_controller import LedController
from recording_manager import RecordingManager


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

        self._transitions: dict[tuple[State, EventType], callable] = {
            (State.IDLE, EventType.BUTTON_SHORT_PRESS): self._idle_to_recording,
            (State.IDLE, EventType.BUTTON_LONG_PRESS): self._idle_to_recording,
            (State.IDLE, EventType.SLACK_START): self._idle_to_recording,

            (State.RECORDING, EventType.BUTTON_SHORT_PRESS): self._recording_to_saving,
            (State.RECORDING, EventType.SLACK_CLIP): self._recording_to_saving,

            (State.RECORDING, EventType.BUTTON_LONG_PRESS): self._recording_to_idle,
            (State.RECORDING, EventType.SLACK_STOP): self._recording_to_idle,

            (State.SAVING, EventType.ENCODE_OK): self._saving_done,
            (State.SAVING, EventType.ENCODE_FAIL): self._saving_failed,
        }

    def run(self):
        """Main event loop -- blocks the calling thread."""
        while True:
            event = self._event_bus.wait(timeout=0.1)
            if event is None:
                continue

            handler = self._transitions.get((self.state, event.type))
            if handler:
                handler(event)
            else:
                print(f"Ignoring {event.type.name} in state {self.state.name}")

    def _idle_to_recording(self, event: Event):
        print("Starting recording")
        self._recording.start()
        self._led.play_transition("start")
        self.state = State.RECORDING
        self._led.set_state(State.RECORDING)

    def _recording_to_saving(self, event: Event):
        print("Saving clip")
        self.state = State.SAVING
        self._led.set_state(State.SAVING)
        self._recording.capture_and_encode()

    def _recording_to_idle(self, event: Event):
        print("Stopping recording")
        self._recording.stop()
        self._led.play_transition("stop")
        self.state = State.IDLE
        self._led.set_state(State.IDLE)

    def _saving_done(self, event: Event):
        print("Clip saved successfully")
        self._led.play_transition("saved")
        self._recording.restart_buffers()
        self.state = State.RECORDING
        self._led.set_state(State.RECORDING)

    def _saving_failed(self, event: Event):
        print("Clip save failed")
        self._led.play_transition("error")
        self._recording.restart_buffers()
        self.state = State.RECORDING
        self._led.set_state(State.RECORDING)
