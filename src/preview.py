from picamera2 import Picamera2, Preview
from libcamera import controls

def display_preview():
    # Create a Picamera2 instance
    picam2 = Picamera2()

    # Configure the camera with autofocus enabled
    preview_config = picam2.create_preview_configuration(controls={"FrameRate": 60})
    picam2.configure(preview_config)

    # Set autofocus mode
    picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})


    # Start the camera preview with a built-in preview window
    picam2.start_preview(Preview.QTGL)

    # Start the camera
    picam2.start()

    try:
        # Run indefinitely until interrupted
        input("Press Enter to exit...\n")
    except KeyboardInterrupt:
        pass
    finally:
        # Stop the camera and release resources
        picam2.stop_preview()
        picam2.stop()

if __name__ == "__main__":
    display_preview()