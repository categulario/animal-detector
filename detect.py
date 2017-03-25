#!/usr/bin/env python3
from gpiozero import MotionSensor, LED
from picamera import PiCamera
from datetime import datetime
from time import sleep, time
from pushover import send_notification
from utils import connection_available, call
import settings
import signal
import os

# Setup some io
pir    = MotionSensor(4)
camera = PiCamera()
led    = LED(23)

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
        call('MP4Box -add videos/{0}.h264 videos/{0}.mp4'.format(filename))

        if settings.DROPBOX_ENABLE and connection_available():
            print('Uploading video to dropbox', flush=True)
            # Upload the video to dropbox
            call('dropbox_uploader.sh upload videos/{0}.mp4 records/{0}.mp4'.format(filename))

            output = call('dropbox_uploader.sh share records/{0}.mp4'.format(filename))
            link = output.split(' ')[3]
        else:
            link = None

        if settings.PUSHOVER_ENABLE and connection_available():
            print('Notify about {}'.format(filename), flush=True)
            send_notification(
                title = 'New video recorded',
                message = 'Your raspberry has recorded a new video',
                url = link if link else 'http://categulario.tk/estepicursor.gif',
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
