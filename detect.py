#!/usr/bin/env python3
from gpiozero import MotionSensor, LED
from picamera import PiCamera
from datetime import datetime
from time import sleep, time
from pushover import send_notification
import subprocess
import settings
import signal
import os

# Setup some io
pir    = MotionSensor(4)
camera = PiCamera()
led    = LED(17)

class GracefulKiller:
  kill_now = False
  def __init__(self):
    signal.signal(signal.SIGINT, self.exit_gracefully)
    signal.signal(signal.SIGTERM, self.exit_gracefully)

  def exit_gracefully(self,signum, frame):
    self.kill_now = True

def main(killer):
    while True:
        if killer.kill_now:
            break
        pir.wait_for_motion(1)
        if not pir.motion_detected:
            # no motion, the wait process stopped by timeout
            continue
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
        if settings.PUSHOVER_ENABLE:
            send_notification(
                title = 'New video recorded',
                message = 'Your raspberry has recorded a new video',
                url = 'http://192.168.1.72/animal-detector/{}.mp4'.format(filename),
                url_title = 'Go to the video',
            )

    os.remove('detect.pid')
    print("Babay!")

if __name__ == '__main__':
    print('Waiting for some aminal...', flush=True)
    with open('detect.pid', 'w') as pidfile:
        pidfile.write(str(os.getpid()))

    killer = GracefulKiller()
    main(killer)
