# -*- coding: utf-8 -*-
import socket
import threading
import os
from dotenv import load_dotenv
import cv2
import imutils
import math
from Modules import module_calibrate_camera

load_dotenv(verbose=True)

HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))
DEVICE_NUMBER = int(os.getenv("DEVICE_NUMBER"))


class ClientThread(threading.Thread):
    def __init__(self, clientAddress, clientsocket):
        threading.Thread.__init__(self)
        self.csocket = clientsocket
        self.caddress = clientAddress
        print("New Robot connection added: ", clientAddress)

    def run(self):
        # self.csocket.send(bytes("Hi, This is from Server..",'utf-8'))
        msg = ''
        cap = init_vision_system(DEVICE_NUMBER)
        while True:
            _, frame = cap.read()
            cv2.imshow("Cenario", frame)
            data = self.csocket.recv(2048)
            if data:
                msg = data.decode()
                if msg == 'bye':
                    break
                print("from client", msg)
                self.csocket.send(bytes(msg, 'UTF-8'))
        print("Client at ", self.caddress, " disconnected...")


def init_system():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    print("Server started")
    print("Waiting for Robot request..")
    while True:
        server.listen(1)
        clientsock, clientAddress = server.accept()
        newthread = ClientThread(clientAddress, clientsock)
        newthread.start()


def init_vision_system(device_number):
    cap = cv2.VideoCapture(device_number)
    if cap.isOpened():
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)  # float
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)  # float
        # print(cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT) # 3, 4
        print('width, height:', width, height)
        fps = cap.get(cv2.CAP_PROP_FPS)
        print('fps:', fps)  # float
        # print(cv2.CAP_PROP_FPS) # 5
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        print('frames count:', frame_count)  # float
        # print(cv2.CAP_PROP_FRAME_COUNT) # 7
        return cap
    else:
        print('Error on open video device', device_number)

def print_menuCentral():  ## Your menu design here
    print(24 * "-", "CENTRAL CONTROL SYSTEM", 24 * "-")
    print("1. START CENTRAL CONTROL")
    print("2. CAMERA CALIBRATION")
    print("3. EXIT")
    print(71 * "-")


def main():
    while 1:
        print_menuCentral()
        try:
            choice = int(input("Enter your choice [1-3]:"))
        except ValueError:
            print("Not an integer! Try again.")
            continue
        if choice == 1:
            print(">> Starting Centrel Control")
            init_system()
        if choice == 2:
            print(">> Starting Calibration Camera")
            module_calibrate_camera.CalibrationCamera()
        elif choice == 3:
            print(">> Exit")
            quit()
        else:
            print("Wrong option selection. Enter any key to try again..")


if __name__ == '__main__':
    main()