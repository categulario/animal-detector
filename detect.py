#!/usr/bin/env python3
from gpiozero import MotionSensor, LED
from picamera import PiCamera
from datetime import datetime
from time import sleep, time
from pushover import send_notification
from utils import connection_available, call
import argparse
import settings
import logging
import signal
import sys
import os

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
        logging.info('Recording {}'.format(filename))

        led.on()
        camera.start_recording('videos/{}.h264'.format(filename))
        sleep(30) # Record for 30 secs
        camera.stop_recording()
        led.off()

        logging.info('Encoding {}'.format(filename))
        # Wrap the file into mp4 so i can view it
        call('MP4Box -add videos/{0}.h264 videos/{0}.mp4'.format(filename))

        if settings.DROPBOX_ENABLE and connection_available():
            logging.info('Uploading video to dropbox')
            # Upload the video to dropbox
            call('dropbox_uploader.sh upload videos/{0}.mp4 records/{0}.mp4'.format(filename))

            output = call('dropbox_uploader.sh share records/{0}.mp4'.format(filename))
            link = output.split(' ')[3]
        else:
            link = None

        if settings.PUSHOVER_ENABLE and connection_available():
            logging.info('Notify about {}'.format(filename))
            send_notification(
                title = 'New video recorded',
                message = 'Your raspberry has recorded a new video',
                url = link if link else 'http://categulario.tk/estepicursor.gif',
                url_title = 'Go to the video',
            )

    os.remove('detect.pid')
    logging.info("Babay!")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='runs the detector process')

    parser.add_argument('--pid', type=argparse.FileType('w'), help='the file to write the pidfile', default='detect.pid')
    parser.add_argument('--logfile', type=argparse.FileType('a'), help='where to log', default=sys.stdout)
    parser.add_argument('--log', help="log level", default=logging.INFO)

    args = parser.parse_args()

    logging.basicConfig(
        stream=args.logfile,
        level=args.log,
        format='%(asctime)s:%(name)s:%(levelname)s %(message)s',
    )

    logging.info('Waiting for some aminal...')

    args.pid.write(str(os.getpid()))

    # Setup some io
    pir    = MotionSensor(4)
    camera = PiCamera()
    led    = LED(23)

    killer = GracefulKiller()
    main(killer)
