import logging
import os
import threading
import time

from consts import CLIP_DIRECTORY
from event_bus import EventBus
from button_controller import ButtonController
from led_controller import LedController
from recording_manager import RecordingManager
from state_machine import StateMachine
from server import init_server
from web_server import init_web_server

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(name)s %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    time.sleep(1)
    os.makedirs(CLIP_DIRECTORY, exist_ok=True)

    event_bus = EventBus()
    led = LedController()
    recording = RecordingManager(event_bus)
    button = ButtonController(event_bus)
    sm = StateMachine(event_bus, led, recording)

    travel_mode = os.environ.get('TRAVEL_MODE') == '1'

    if travel_mode:
        logger.info("Travel mode: starting web server only (no Slack)")
    else:
        threading.Thread(target=init_server, args=(event_bus, sm), daemon=True).start()

    threading.Thread(target=init_web_server, args=(event_bus, sm), daemon=True).start()

    button.start()
    led.start()

    try:
        sm.run()
    except KeyboardInterrupt:
        pass
    finally:
        recording.stop()
        button.cleanup()
        led.stop()


if __name__ == '__main__':
    main()
