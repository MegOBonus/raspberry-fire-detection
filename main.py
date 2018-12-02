import tkinter
import cv2
import PIL.Image
import PIL.ImageTk
import socket
import pickle
import numpy as np
import struct

from pydub import AudioSegment
from pydub.playback import play


class Interface:
    def __init__(self):
        self.alert_sound = AudioSegment.from_wav('./assets/alert.wav')
        self.host = ''
        self.port = 8486

    def play_alert(self):
        play(self.alert_sound)

    def add_img(self, name):
        window = tkinter.Tk()
        window.title(name)

        cv_img = cv2.cvtColor(cv2.imread(name), cv2.COLOR_BGR2RGB)
        height, width, no_channels = cv_img.shape
        canvas = tkinter.Canvas(window, width=width, height=height)
        photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(cv_img))
        canvas.create_image(0, 0, image=photo, anchor=tkinter.NW)
        canvas.pack()
        self.play_alert()

        window.mainloop()

    def run_socket_server(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.host, self.port))
        s.listen(10)
        print('Server started')

        conn, addr = s.accept()

        data = b""
        payload_size = struct.calcsize(">L")


        while True:
            while len(data) < payload_size:
                print("Recv: {}".format(len(data)))
                data += conn.recv(4096)

            print("Done Recv: {}".format(len(data)))
            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack(">L", packed_msg_size)[0]
            print("msg_size: {}".format(msg_size))
            while len(data) < msg_size:
                data += conn.recv(4096)
            frame_data = data[:msg_size]
            data = data[msg_size:]

            frame = pickle.loads(
                frame_data, fix_imports=True, encoding="bytes")
            frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
            image_name = "img{}.jpg".format(addr[0])
            cv2.imwrite(image_name, frame)
            self.add_img(image_name)
            cv2.waitKey(1)


if __name__ == "__main__":

    interface = Interface()

    interface.run_socket_server()
