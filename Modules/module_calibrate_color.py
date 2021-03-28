import numpy as np
import cv2 as cv
import time
from configparser import ConfigParser


class CalibrationColor:
    def __init__(self, object):
        cam = cv.VideoCapture(0)
        if cam.isOpened():
            cam.set(cv.CAP_PROP_FRAME_WIDTH, 640)
            cam.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
            width = cam.get(cv.CAP_PROP_FRAME_WIDTH)  # float
            height = cam.get(cv.CAP_PROP_FRAME_HEIGHT)  # float
            # print(cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT) # 3, 4
        cv.namedWindow("Image")
        while True:
            ret, frame = cam.read()
            if not ret:
                print("failed to grab frame")
                break
            cv.imshow("Image", frame)
            k = cv.waitKey(1)
            if k % 256 == 27:
                # ESC pressed
                print("Escape hit, closing...")
                break
            elif k % 256 == 32:
                # SPACE pressed
                img_name = "image.png"
                cv.imwrite(img_name, frame)
                print("Image Written!")
                break
        cam.release()
        img = cv.imread('image.png', cv.IMREAD_COLOR)
        img = cv.medianBlur(img, 5)
        # Convert BGR to HSV
        config_object = ConfigParser()
        config_object.read("config.ini")
        if object == 'robot':
            robot_color = config_object["ROBOT_COLOR"]
            uh = int(robot_color['upperh'])
            us = int(robot_color['uppers'])
            uv = int(robot_color['upperv'])
            lh = int(robot_color['lowerh'])
            ls = int(robot_color['lowers'])
            lv = int(robot_color['lowerv'])
        elif object == 'obstacle':
            obstacle_color = config_object["OBSTACLE_COLOR"]
            uh = int(obstacle_color['upperh'])
            us = int(obstacle_color['uppers'])
            uv = int(obstacle_color['upperv'])
            lh = int(obstacle_color['lowerh'])
            ls = int(obstacle_color['lowers'])
            lv = int(obstacle_color['lowerv'])
        hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
        lower_hsv = np.array([lh, ls, lv])
        upper_hsv = np.array([uh, us, uv])
        # Threshold the HSV image to get only blue colors
        mask = cv.inRange(hsv, lower_hsv, upper_hsv)
        window_name = "HSV Calibrator"
        cv.namedWindow(window_name)

        def nothing(x):
            print("Trackbar value: " + str(x))
            pass

        # create trackbars for Upper HSV
        cv.createTrackbar('UpperH', window_name, 0, 255, nothing)
        cv.setTrackbarPos('UpperH', window_name, uh)

        cv.createTrackbar('UpperS', window_name, 0, 255, nothing)
        cv.setTrackbarPos('UpperS', window_name, us)

        cv.createTrackbar('UpperV', window_name, 0, 255, nothing)
        cv.setTrackbarPos('UpperV', window_name, uv)

        # create trackbars for Lower HSV
        cv.createTrackbar('LowerH', window_name, 0, 255, nothing)
        cv.setTrackbarPos('LowerH', window_name, lh)

        cv.createTrackbar('LowerS', window_name, 0, 255, nothing)
        cv.setTrackbarPos('LowerS', window_name, ls)

        cv.createTrackbar('LowerV', window_name, 0, 255, nothing)
        cv.setTrackbarPos('LowerV', window_name, lv)

        font = cv.FONT_HERSHEY_SIMPLEX

        while (1):
            # Threshold the HSV image to get only blue colors
            mask = cv.inRange(hsv, lower_hsv, upper_hsv)
            cv.putText(mask, 'Lower HSV: [' + str(lh) + ',' + str(ls) + ',' + str(lv) + ']', (10, 30), font, 0.5,
                   (200, 255, 155), 1, cv.LINE_AA)
            cv.putText(mask, 'Upper HSV: [' + str(uh) + ',' + str(us) + ',' + str(uv) + ']', (10, 60), font, 0.5,
                   (200, 255, 155), 1, cv.LINE_AA)
            cv.imshow(window_name, mask)
            k = cv.waitKey(1) & 0xFF
            if k == 27:
                break
            # get current positions of Upper HSV trackbars
            uh = cv.getTrackbarPos('UpperH', window_name)
            us = cv.getTrackbarPos('UpperS', window_name)
            uv = cv.getTrackbarPos('UpperV', window_name)
            upper_blue = np.array([uh, us, uv])
            # get current positions of Lower HSCV trackbars
            lh = cv.getTrackbarPos('LowerH', window_name)
            ls = cv.getTrackbarPos('LowerS', window_name)
            lv = cv.getTrackbarPos('LowerV', window_name)
            upper_hsv = np.array([uh, us, uv])
            lower_hsv = np.array([lh, ls, lv])
            time.sleep(.1)
            if cv.waitKey(1) & 0xFF == ord('q'):
                break
        # Get the configparser object
        if object == 'robot':
            robot_color = config_object["ROBOT_COLOR"]
            robot_color['upperh'] = str(uh)
            robot_color['uppers'] = str(us)
            robot_color['upperv'] = str(uv)
            robot_color['lowerh'] = str(lh)
            robot_color['lowers'] = str(ls)
            robot_color['lowerv'] = str(lv)
        elif object == 'obstacle':
            obstacle_color = config_object["OBSTACLE_COLOR"]
            obstacle_color['upperh'] = str(uh)
            obstacle_color['uppers'] = str(us)
            obstacle_color['upperv'] = str(uv)
            obstacle_color['lowerh'] = str(lh)
            obstacle_color['lowers'] = str(ls)
            obstacle_color['lowerv'] = str(lv)
        # Write the above sections to config.ini file
        with open('config.ini', 'w') as conf:
            config_object.write(conf)
        cv.destroyAllWindows()
