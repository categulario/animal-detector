#!/usr/bin/env python3
from gpiozero import MotionSensor, LED
from picamera import PiCamera
from datetime import datetime
from time import sleep, time
from pushover import send_notification
import subprocess

pir    = MotionSensor(4)
camera = PiCamera()
led    = LED(17)

print('Waiting for some aminal...', flush=True)

while True:
    pir.wait_for_motion()
    filename = datetime.now().strftime('%Y-%m-%d_%H.%M.%S')
    print('Recording {}'.format(filename), flush=True)

    led.on()
    camera.start_recording('videos/{}.h264'.format(filename))
    sleep(30) # Record for 30 secs
    camera.stop_recording()
    led.off()

    print('Encoding {}'.format(filename), flush=True)
    # Wrap the file into mp4 so i can view it
    subprocess.check_call(['MP4Box', '-add', 'videos/{}.h264'.format(filename), 'videos/{}.mp4'.format(filename)])

    print('Notify about {}'.format(filename), flush=True)
    send_notification(
        title = 'New video recorded',
        message = 'Your raspberry has recorded a new video',
        url = 'http://192.168.1.72/animal-detector/{}.mp4'.format(filename),
        url_title = 'Go to the video',
    )
