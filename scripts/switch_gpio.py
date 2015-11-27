import atexit
from time import sleep
import RPi.GPIO as GPIO
import pingo

atexit.register(GPIO.cleanup)
GPIO.setwarnings(False)

board = pingo.detect.get_board()
led_pin = board.pins[13]
led_pin.mode = pingo.OUT

btn_pin = board.pins[7]
btn_pin.mode = pingo.IN

print(btn_pin.state)

while(btn_pin.state == "LOW"):
    led_pin.hi()
    sleep(1)
    led_pin.lo()
    sleep(1)

print(btn_pin.state)

board.cleanup()
 
