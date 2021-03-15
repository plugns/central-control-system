# -*- coding: utf-8 -*-
import socket
from _thread import *
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


def init_system():
    cap = init_vision_system(DEVICE_NUMBER)
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Ensure that you can restart your server quickly when it terminates
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Set the client socket's TCP "well-known port" number
    sock.bind(('', PORT))
    # Set the number of clients waiting for connection that can be queued
    sock.listen(5)
    try:
        while True:
            robot_name = ''
            newSocket, address = sock.accept()
            print("Connected from ", address)
            receivedData = newSocket.recv(1024).decode('utf-8')
            if not receivedData:
                break
            robot_name = receivedData
            print("Robot Connected: ", receivedData)
            newSocket.send("OK".encode('utf-8'))
            loop = True
            while loop:
                _, frame = cap.read()
                cv2.imshow("Cenario", frame)
                receivedData = newSocket.recv(1024).decode('utf-8')
                print(">>Receive Data : ", receivedData)
                if receivedData == "exit":
                    print(">>Disconnected from", address)
                    newSocket.close()
                    loop = False
    finally:
        sock.close()


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