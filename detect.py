#!/usr/bin/env python3
from gpiozero import MotionSensor, LED
from picamera import PiCamera
from datetime import datetime
from time import sleep, time

pir    = MotionSensor(4)
camera = PiCamera()
led    = LED(17)

while True:
    pir.wait_for_motion()
    filename = datetime.now().strftime('%Y-%m-%d_%H.%M.%S.h264')
    print(filename, end='\r', flush=True)
    led.on()
    camera.start_recording(filename)
    sleep(30) # Record for 30 secs
    camera.stop_recording()
    led.off()
    print(' '*len(filename), end='\r', flush=True)
