
import time
import RPi.GPIO as GPIO

from output import write_led

if __name__ == '__main__':
    try:
        while True:
            print('test')
            time.sleep(0.1)
    except:
        GPIO.cleanup()

    