from dataclasses import dataclass, field
from enum import Enum, auto
from queue import Queue, Empty


class EventType(Enum):
    BUTTON_SHORT_PRESS = auto()
    BUTTON_LONG_PRESS = auto()
    SLACK_CLIP = auto()
    SLACK_START = auto()
    SLACK_STOP = auto()
    ENCODE_OK = auto()
    ENCODE_FAIL = auto()
    INACTIVITY_TIMEOUT = auto()
    POKE = auto()


class State(Enum):
    IDLE = auto()
    RECORDING = auto()
    SAVING = auto()


@dataclass
class Event:
    type: EventType
    data: dict = field(default_factory=dict)


class EventBus:
    def __init__(self):
        self._queue: Queue[Event] = Queue()

    def emit(self, event_type: EventType, data: dict | None = None):
        self._queue.put(Event(event_type, data or {}))

    def wait(self, timeout: float = 0.1) -> Event | None:
        try:
            return self._queue.get(timeout=timeout)
        except Empty:
            return None
