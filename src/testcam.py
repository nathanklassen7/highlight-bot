from picamera2 import Picamera2, Preview

def activate_camera():
    picam2 = Picamera2()
    camera_config = picam2.create_video_configuration({"size": (1536, 864), "format": "RGB888"})
    # camera_config = picam2.create_video_configuration()
    picam2.configure(camera_config)
    picam2.start_preview(Preview.NULL)
    picam2.set_controls({"ExposureTime":10000})
    picam2.start()
    return picam2