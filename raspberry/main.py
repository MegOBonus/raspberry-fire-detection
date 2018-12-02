
import time
import cv2
import numpy as np
import imutils

from imutils.video import VideoStream

from socket_client import SocketClient


class Detector(object):
    def __init__(self):
        self.video_stream = VideoStream(
            src=0, usePiCamera=True, resolution=(640, 480), framerate=32).start()
        self.fire_cascade = cv2.CascadeClassifier('fire_detection.xml')
        self.host = '192.168.1.223'
        self.port = 8486
        time.sleep(2.0)
        self.timeCheck = time.time()
        self.socket_client = SocketClient()

    def start(self):
        self.socket_client.connect(self.host, self.port)
        print('Connected')
        while True:
            # Get the next frame.
            frame = self.video_stream.read()

            # Show video stream
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            fire = self.fire_cascade.detectMultiScale(frame, 1.2, 5)
            for (x, y, w, h) in fire:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                font = cv2.FONT_HERSHEY_SIMPLEX
                roi_gray = gray[y:y+h, x:x+w]
                roi_color = frame[y:y+h, x:x+w]
                time.sleep(0.2)
                print('Detected')
                cv2.imwrite('sector2.png', frame)
                self.send_frame(frame)
            cv2.imshow('out', frame)
            key = cv2.waitKey(1) & 0xFF

            # if the `q` key was pressed, break from the loop.
            if key == ord("q"):
                break

            self.timeCheck = time.time()

    def send_frame(self, frame):
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        result, frame = cv2.imencode('.jpg', frame, encode_param)
        self.socket_client.send_frame(frame)

    def stop(self):
        cv2.destroyAllWindows()
        self.video_stream.stop()


if __name__ == "__main__":
    detector = Detector()
    detector.start()
