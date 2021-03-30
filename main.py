# -*- coding: utf-8 -*-
import os
import time
import cv2
import math
import serial
import matplotlib.pyplot as plt
from configparser import ConfigParser
from Modules import module_calibrate_camera, module_vision, module_calibrate_color

#Read config.ini file
config_object = ConfigParser()
config_object.read("config.ini")
system = config_object["SYSTEM"]
HOST = str(system['HOST'])
PORT = int(system['PORT'])
DEVICE_NUMBER = int(system['DEVICE_NUMBER'])
arduino = serial.Serial(port='/dev/ttyACM0', baudrate=9600, timeout=.1)


def write_read_seriel(data):
    arduino.write(bytes(data, 'UTF-8'))
    time.sleep(0.10)
    data = arduino.readline()
    return data

''
def init_system():
    print("Robot Connected")
    cap = init_vision_system(DEVICE_NUMBER)
    loop = True
    while loop:
        _, frame = cap.read()
        robot_position = module_vision.robotDetecting(frame, config_object["ROBOT_COLOR"])
        obstacle_position = module_vision.obstacleDetecting(frame, config_object["OBSTACLE_COLOR"])
        cv2.line(frame, robot_position['center'], obstacle_position['center'], (0, 255, 0), 2)
        cv2.imshow("Cenario", frame)
        #scenery_points = module_vision.arucoDetecting(frame)
        # Calculando a distância
        dist_robot_obstacle = math.sqrt((robot_position['center'][0] - obstacle_position['center'][0]) ** 2) +\
            math.sqrt((robot_position['center'][1] - obstacle_position['center'][1]) ** 2)
        print('A distância entre esses dois pontos é de:', dist_robot_obstacle, 'px')

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

        if dist_robot_obstacle < 200:
            value = write_read_seriel("0;0;F")
        else:
            value = write_read_seriel("255;255;F")
        print(">>Receive Data : ", value)
        if value == "exit":
            print(">>Disconnected from", address)
            loop = False
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


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
    print("3. ROBOT COLOR CALIBRATION")
    print("4. OBSTACLE COLOR CALIBRATION")
    print("5. EXIT")
    print(71 * "-")


def main():
    #dist_robot_obstacle = math.sqrt((308 - 297) ** 2) + math.sqrt((177 - 103) ** 2)
    #catX = 308 - 297
    #catY = 177 - 103
    #print(dist_robot_obstacle)
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
        elif choice == 5:
            print(">> Exit")
            quit()
        else:
            print("Wrong option selection. Enter any key to try again..")


if __name__ == '__main__':
    main()