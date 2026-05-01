import logging
import os
import threading
import time

from clip_db import init_db
from consts import CLIP_DIRECTORY, SNAPSHOT_DIRECTORY
from event_bus import EventBus
from bluetooth_shutter_controller import BluetoothShutterController
from button_controller import ButtonController
from led_controller import LedController
from recording_manager import RecordingManager
from state_machine import StateMachine
from web_server import init_web_server

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(name)s %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    time.sleep(1)
    os.makedirs(CLIP_DIRECTORY, exist_ok=True)
    os.makedirs(SNAPSHOT_DIRECTORY, exist_ok=True)
    init_db()

    event_bus = EventBus()
    led = LedController()
    recording = RecordingManager(event_bus)
    button = ButtonController(event_bus)
    bt_shutter = BluetoothShutterController(event_bus)
    sm = StateMachine(event_bus, led, recording)

    disable_slack = os.environ.get('DISABLE_SLACK') == '1'
    travel_mode = os.environ.get('TRAVEL_MODE') == '1'

    if disable_slack or travel_mode:
        logger.info("Starting web server only (no Slack)")
    else:
        from server import init_server
        threading.Thread(target=init_server, args=(event_bus, sm), daemon=True).start()

    threading.Thread(target=init_web_server, args=(event_bus, sm), daemon=True).start()

    button.start()
    bt_shutter.start()
    led.start()

    try:
        sm.run()
    except KeyboardInterrupt:
        pass
    finally:
        recording.stop()
        button.cleanup()
        bt_shutter.cleanup()
        led.stop()


if __name__ == '__main__':
    main()
