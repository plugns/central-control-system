# -*- coding: utf-8 -*-
import socket
import os
import time
import cv2
import math
import random
import matplotlib.pyplot as plt
from configparser import ConfigParser
from Modules import module_calibrate_camera, module_vision, module_calibrate_color

# Read config.ini file
config_object = ConfigParser()
config_object.read("config.ini")
system = config_object["SYSTEM"]
HOST = str(system['HOST'])
PORT = int(system['PORT'])
DEVICE_NUMBER = int(system['DEVICE_NUMBER'])


def init_system():
    cap = init_vision_system(DEVICE_NUMBER)
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Ensure that you can restart your server quickly when it terminates
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Set the client socket's TCP "well-known port" number
    sock.bind((HOST, PORT))
    # Set the number of clients waiting for connection that can be queued
    sock.listen(5)
    try:
        while True:
            newSocket, address = sock.accept()
            print("Connected from ", address)
            receivedData = newSocket.recv(1024).decode('utf-8')
            if not receivedData:
                break
            robot_name = receivedData
            print("Robot Connected: ", robot_name)
            data = "0;0;0\n"
            newSocket.send(data.encode('utf-8'))
            print("Send Data", data)
            loop = True
            for i in range(10):
                _, frame = cap.read()
            send_commands = False
            while loop:
                _, frame = cap.read()
                robot_position = module_vision.robotDetecting(frame, config_object["ROBOT_COLOR"])
                obstacles_positions = module_vision.obstacleDetecting(frame, config_object["OBSTACLE_COLOR"])
                # Calculando a distância
                xRobot = robot_position['center'][0]
                yRobot = robot_position['center'][1]
                turnLeftRobot = False
                turnRightRobot = False
                for obstacle_position in obstacles_positions:
                    xObstacle = obstacle_position['center'][0]
                    yObstacle = obstacle_position['center'][1]
                    dist_robot_obstacle = math.sqrt((xRobot - xObstacle) ** 2) + \
                                          math.sqrt((yRobot - yObstacle) ** 2)
                    print('A distância entre o robô e o obstáculo é de:', dist_robot_obstacle, 'px')
                    cv2.line(frame, robot_position['center'], obstacle_position['center'], (0, 255, 0), 2)
                    if dist_robot_obstacle < 170 and yRobot > yObstacle:
                        if xRobot <= xObstacle:
                            turnLeftRobot = True
                            turnRightRobot = False
                        else:
                            turnLeftRobot = False
                            turnRightRobot = True
                if send_commands:
                    if (turnLeftRobot or turnRightRobot):
                        if turnLeftRobot:
                            stop(newSocket)
                            print("left")
                            turn_left(newSocket, 5)
                            for i in range(5):
                                _, frame = cap.read()
                            forward(newSocket, 5)
                            for i in range(5):
                                _, frame = cap.read()
                            turn_right(newSocket, 6)
                            for i in range(6):
                                _, frame = cap.read()
                            forward(newSocket, 9)
                            for i in range(9):
                                _, frame = cap.read()
                        elif turnRightRobot:
                            stop(newSocket)
                            print("right")
                            turn_right(newSocket, 5)
                            for i in range(5):
                                _, frame = cap.read()
                            forward(newSocket, 5)
                            for i in range(5):
                                _, frame = cap.read()
                            turn_left(newSocket, 6)
                            for i in range(6):
                                _, frame = cap.read()
                            forward(newSocket, 9)
                            for i in range(9):
                                _, frame = cap.read()
                    else:
                        data = "1;400;400\n"
                        print("forward")
                        newSocket.send(data.encode('utf-8'))
                        print("Send Data", data)
                        receivedData = newSocket.recv(1024).decode('utf-8')
                        print(">>Receive Data : ", receivedData)
                cv2.imshow("Cenario", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
    finally:
        sock.close()


def stop(newSocket):
    data = "0;0;0\n"
    newSocket.send(data.encode('utf-8'))
    print("Send Data", data)
    receivedData = newSocket.recv(1024).decode('utf-8')
    print(">>Receive Data : ", receivedData)


def forward(newSocket, n):
    data = "1;400;400\n"
    for i in range(n):
        newSocket.send(data.encode('utf-8'))
        print("Send Data", data)
        receivedData = newSocket.recv(1024).decode('utf-8')
        print(">>Receive Data : ", receivedData)


def turn_right(newSocket, n):
    data = "3;350;900\n"
    for i in range(n):
        newSocket.send(data.encode('utf-8'))
        print("Send Data", data)
        receivedData = newSocket.recv(1024).decode('utf-8')
        print(">>Receive Data : ", receivedData)


def turn_left(newSocket, n):
    data = "4;900;350\n"
    for i in range(n):
        newSocket.send(data.encode('utf-8'))
        print("Send Data", data)
        receivedData = newSocket.recv(1024).decode('utf-8')
        print(">>Receive Data : ", receivedData)

# x = (robot_position['center'][0], obstacle_position['center'][0])
# y = (robot_position['center'][1], obstacle_position['center'][1])
# plotting the points
# plt.plot(x, y, color='green', linestyle='dashed', linewidth=3, marker='o', markerfacecolor='blue', markersize=12)
# plt.plot(x, y)
# naming the x axis
# plt.xlabel('x - axis')
# naming the y axis
# plt.ylabel('y - axis')
# giving a title to my graph
# plt.title('Distance between the robot and the obstacle')
# function to show the plot
# plt.show()
# (v.rodaDireita, v.rodaEsquerda, direção)

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


def communication_test():
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Ensure that you can restart your server quickly when it terminates
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Set the client socket's TCP "well-known port" number
    sock.bind((HOST, PORT))
    # Set the number of clients waiting for connection that can be queued
    sock.listen(5)
    try:
        while True:
            newSocket, address = sock.accept()
            print("Connected from ", address)
            receivedData = newSocket.recv(1024).decode('utf-8')
            if not receivedData:
                break
            robot_name = receivedData
            print("Robot Connected: ", robot_name)
            newSocket.send("OK".encode('utf-8'))
            for i in range(10):
                d = random.randint(300, 1024)
                e = random.randint(300, 1024)
                print(f"{d};{e};1\n")
                if i % 2:
                    newSocket.send(f"{d};{e};1\n".encode('utf-8'))
                else:
                    newSocket.send(f"{d};{e};2\n".encode('utf-8'))
                receivedData = newSocket.recv(1024).decode('utf-8')
                print(">>Receive Data : ", receivedData)
                time.sleep(5)
            for i in range(5):
                d = 300
                e = random.randint(300, 1024)
                print(f"{d};{e};1\n")
                if i % 2:
                    newSocket.send(f"{d};{e};1\n".encode('utf-8'))
                else:
                    newSocket.send(f"{d};{e};2\n".encode('utf-8'))
                receivedData = newSocket.recv(1024).decode('utf-8')
                print(">>Receive Data : ", receivedData)
                time.sleep(5)
            for i in range(5):
                d = random.randint(300, 1024)
                e = 300
                print(f"{d};{e};1\n")
                if i % 2:
                    newSocket.send(f"{d};{e};1\n".encode('utf-8'))
                else:
                    newSocket.send(f"{d};{e};2\n".encode('utf-8'))
                receivedData = newSocket.recv(1024).decode('utf-8')
                print(">>Receive Data : ", receivedData)
                time.sleep(5)
            sock.close()
    finally:
        sock.close()


def print_menuCentral():
    print(24 * "-", "CENTRAL CONTROL SYSTEM", 24 * "-")
    print("1. START CENTRAL CONTROL")
    print("2. CAMERA CALIBRATION")
    print("3. ROBOT COLOR CALIBRATION")
    print("4. OBSTACLE COLOR CALIBRATION")
    print("5. COMMUNICATION TEST")
    print("6. EXIT")
    print(71 * "-")


def main():
    # dist_robot_obstacle = math.sqrt((308 - 297) ** 2) + math.sqrt((177 - 103) ** 2)
    # catX = 308 - 297
    # catY = 177 - 103
    # print(dist_robot_obstacle)
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
            print(">> Starting Camera Calibration")
            module_calibrate_camera.CalibrationCamera()
        if choice == 3:
            print(">> Starting Robot Color Calibration")
            module_calibrate_color.CalibrationColor('robot')
        if choice == 4:
            print(">> Starting Obstacle Color Calibration")
            module_calibrate_color.CalibrationColor('obstacle')
        if choice == 5:
            print(">> Starting communication test")
            communication_test()
        elif choice == 6:
            print(">> Exit")
            quit()
        else:
            print("Wrong option selection. Enter any key to try again..")


if __name__ == '__main__':
    main()
