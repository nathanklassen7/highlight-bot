import RPi.GPIO as GPIO
import time

INPUT_PIN_MAP = {
    "button": 3,
}

OUTPUT_PIN_MAP = {
    "record": 21,
    "on": 26,
    "write": 20
}

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

for pin in OUTPUT_PIN_MAP:
    GPIO.setup(OUTPUT_PIN_MAP[pin], GPIO.OUT)
    GPIO.output(OUTPUT_PIN_MAP[pin], GPIO.LOW)
    
for pin in INPUT_PIN_MAP:
    GPIO.setup(INPUT_PIN_MAP[pin],GPIO.IN,GPIO.PUD_UP)

def read_button():
    return GPIO.input(INPUT_PIN_MAP['button'])

def write_led(led_name, value):
    GPIO.output(OUTPUT_PIN_MAP[led_name], GPIO.HIGH if value else GPIO.LOW)

SAVED_FLASH_COUNT = 3
FLASH_SPEED = 0.2
def indicate_saved_video():
    for _ in range(SAVED_FLASH_COUNT):
        write_led('write',False)
        time.sleep(FLASH_SPEED)
        write_led('write',True)
        time.sleep(FLASH_SPEED)
    write_led('write',False)
    
ERROR_FLASH_COUNT = 10
def indicate_save_error():
    for _ in range(ERROR_FLASH_COUNT):
        write_led('write',False)
        time.sleep(FLASH_SPEED)
        write_led('write',True)
        time.sleep(FLASH_SPEED)
    write_led('write',False)

def indicate_writing():
    write_led('write',True)
        
def display_recording_status(is_recording):
    if not is_recording:
        write_led('record',False)
        return
        
    flash_value = time.time()//1%2
    write_led('record',bool(flash_value))
    
START_FLASH_COUNT = 3
STOP_FLASH_COUNT = 7        
def indicate_recording_start():
    for _ in range(START_FLASH_COUNT):
        write_led('record',False)
        time.sleep(FLASH_SPEED)
        write_led('record',True)
        time.sleep(FLASH_SPEED)
    write_led('record',False)
    time.sleep(FLASH_SPEED*2)
    
def indicate_recording_stop():
    for _ in range(STOP_FLASH_COUNT):
        write_led('record',False)
        time.sleep(FLASH_SPEED)
        write_led('record',True)
        time.sleep(FLASH_SPEED)
    write_led('record',False)
    
    
        
HOLD_TIME = 0.05
POLL_SPEED = 0.01
def wait_for_press(is_recording):
    while True:
        while not read_button():
            time.sleep(POLL_SPEED)
            display_recording_status(is_recording)

        first_pressed_at = time.time()

        while read_button():
            if time.time() - first_pressed_at > HOLD_TIME:
                return True
            
def wait_for_release(check_for_long = False):
    press_time = time.time()
    while True:
        while read_button():
            time.sleep(POLL_SPEED)
            hold_time = time.time() - press_time
            if hold_time > 2 and check_for_long:
                return "long"
            
        first_released_at = time.time()
        while not read_button():
            if time.time() - first_released_at > HOLD_TIME:
                return "short"
            
def cleanup():
    GPIO.cleanup()