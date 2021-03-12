# -*- coding: utf-8 -*-

import socket
import threading
import os
from dotenv import load_dotenv
from Modules import calibrate_camera

load_dotenv(verbose=True)

HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))


class ClientThread(threading.Thread):
    def __init__(self, clientAddress, clientsocket):
        threading.Thread.__init__(self)
        self.csocket = clientsocket
        print("New connection added: ", clientAddress)
        print("Connection from : ", clientAddress)

    def run(self):
        # self.csocket.send(bytes("Hi, This is from Server..",'utf-8'))
        msg = ''
        while True:
            data = self.csocket.recv(2048)
            if data:
                msg = data.decode()
                if msg == 'bye':
                    break
                print("from client", msg)
                self.csocket.send(bytes(msg, 'UTF-8'))
        # print("Client at ", clientAddress, " disconnected...")


def init_system():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    print("Server started")
    print("Waiting for client request..")
    while True:
        server.listen(1)
        clientsock, clientAddress = server.accept()
        newthread = ClientThread(clientAddress, clientsock)
        newthread.start()


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
            calibrate_camera.CalibrationCamera()
        elif choice == 3:
            print(">> Exit")
            quit()
        else:
            print("Wrong option selection. Enter any key to try again..")


if __name__ == '__main__':
    main()