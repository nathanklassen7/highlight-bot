import threading
from event_bus import EventBus, EventType
from audio_utils import (
    capture_audio_data, start_recording_audio,
    stop_recording_audio, timestamp_file,
)
from video_utils import (
    capture_video_data, start_camera, stop_camera,
    start_recording_video, stop_recording_video,
)
from encoding_utils import encode_video
import os


class RecordingManager:
    def __init__(self, event_bus: EventBus):
        self._event_bus = event_bus

    def start(self):
        if os.path.exists(timestamp_file):
            os.remove(timestamp_file)
        start_camera()
        start_recording_video()
        start_recording_audio()

    def stop(self):
        stop_recording_video()
        stop_recording_audio()
        stop_camera()

    def restart_buffers(self):
        """Restart the circular buffers without cycling the camera."""
        start_recording_video()
        start_recording_audio()

    def capture_and_encode(self):
        """Capture current buffers and encode in a background thread.

        Emits ENCODE_OK or ENCODE_FAIL to the event bus when finished.
        """
        video_duration = capture_video_data()
        audio_duration = capture_audio_data()

        if video_duration == 0:
            print("Error capturing video")
            self._event_bus.emit(EventType.ENCODE_FAIL)
            return

        if audio_duration == 0:
            print("Audio capture failed, saving video without audio")

        threading.Thread(
            target=self._encode_worker,
            args=(video_duration, audio_duration),
            daemon=True,
        ).start()

    def _encode_worker(self, video_duration: float, audio_duration: float):
        result = encode_video(video_duration, audio_duration)
        if result == 0:
            print("Converted!")
            self._event_bus.emit(EventType.ENCODE_OK)
        else:
            print("Error converting .h264 file and joining audio")
            self._event_bus.emit(EventType.ENCODE_FAIL)
