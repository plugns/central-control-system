import cv2
import matplotlib as plt
import numpy as np
import imutils


def undistortFrame(frame, mtx, dist, verbose=False):
    """
    Undistort a frame given camera matrix and distortion coefficients.
    :param frame: input frame
    :param mtx: camera matrix
    :param dist: distortion coefficients
    :param verbose: if True, show frame before/after distortion correction
    :return: undistorted frame
    """
    frame_undistorted = cv2.undistort(frame, mtx, dist, newCameraMatrix=mtx)

    if verbose:
        fig, ax = plt.subplots(nrows=1, ncols=2)
        ax[0].imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        ax[1].imshow(cv2.cvtColor(frame_undistorted, cv2.COLOR_BGR2RGB))
        plt.show()

    return frame_undistorted


def robotDetecting(frame, config_object):
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    uh = int(config_object['upperh'])
    us = int(config_object['uppers'])
    uv = int(config_object['upperv'])
    lh = int(config_object['lowerh'])
    ls = int(config_object['lowers'])
    lv = int(config_object['lowerv'])
    low_green = np.array([lh, ls, lv])
    high_green = np.array([uh, us, uv])
    green_mask = cv2.inRange(hsv_frame, low_green, high_green)
    frame_robot = cv2.bitwise_and(frame, frame, mask=green_mask)
    frame_gray_robot = cv2.cvtColor(frame_robot, cv2.COLOR_BGR2GRAY)
    # convert image to grayscale image
    blurred = cv2.GaussianBlur(frame_gray_robot, (5, 5), 0)
    thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]
    # find contours in the thresholded image
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cX_robot = 0
    cY_robot = 0
    # loop over the contours
    for c in cnts:
        # compute the center of the contour
        M = cv2.moments(c)
        if M["m00"] > 0:
            cX_robot = int(M["m10"] / M["m00"])
            cY_robot = int(M["m01"] / M["m00"])
            # draw the contour and center of the shape on the image
            cv2.drawContours(frame_robot, [c], -1, (0, 255, 0), 2)
            cv2.circle(frame_robot, (cX_robot, cY_robot), 8, (255, 255, 255), -1)
            cv2.putText(frame_robot, "Robot", (cX_robot - 20, cY_robot - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        # show the image
        # plt.imshow(img_green)
        # plt.show()
    cv2.imshow("Robot", frame_robot)
    print("Robot -> X: ", cX_robot, " Y: ", cY_robot)
    # left, right, top , button
    robot_position = {
        'center': (cX_robot, cY_robot),
        'top': (cX_robot, cY_robot + 10),
        'button': (cX_robot, cY_robot - 10),
        'left': (cX_robot - 6, cY_robot),
        'right': (cX_robot + 6, cY_robot),
    }
    return robot_position


def obstacleDetecting(frame, config_object):
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    uh = int(config_object['upperh'])
    us = int(config_object['uppers'])
    uv = int(config_object['upperv'])
    lh = int(config_object['lowerh'])
    ls = int(config_object['lowers'])
    lv = int(config_object['lowerv'])
    low_red = np.array([lh, ls, lv])
    high_red = np.array([uh, us, uv])
    red_mask = cv2.inRange(hsv_frame, low_red, high_red)
    frame_obstacle = cv2.bitwise_and(frame, frame, mask=red_mask)
    frame_gray_obstacle = cv2.cvtColor(frame_obstacle, cv2.COLOR_BGR2GRAY)
    # convert image to grayscale image
    blurred = cv2.GaussianBlur(frame_gray_obstacle, (5, 5), 0)
    thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]
    # find contours in the thresholded image
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cX_obstacle = 0
    cY_obstacle = 0
    # left, right, top , button
    # loop over the contours
    for c in cnts:
        # compute the center of the contour
        M = cv2.moments(c)
        if M["m00"] > 0:
            cX_obstacle = int(M["m10"] / M["m00"])
            cY_obstacle = int(M["m01"] / M["m00"])
            # draw the contour and center of the shape on the image
            cv2.drawContours(frame_obstacle, [c], -1, (0, 255, 0), 2)
            cv2.circle(frame_obstacle, (cX_obstacle, cY_obstacle), 8, (255, 255, 255), -1)
            cv2.putText(frame_obstacle, "Obstacle", (cX_obstacle - 20, cY_obstacle - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        # show the image
        # plt.imshow(img_green)
        # plt.show()
    cv2.imshow("Obstacle", frame_obstacle)
    print("Obstacle -> X: ", cX_obstacle, " Y: ", cY_obstacle)
    obstacle_position = {
        'center': (cX_obstacle, cY_obstacle),
        'top': (cX_obstacle, cY_obstacle + 5),
        'button': (cX_obstacle, cY_obstacle - 5),
        'left': (cX_obstacle - 5, cY_obstacle),
        'right': (cX_obstacle + 5, cY_obstacle),
    }
    # left, right, top , button
    return obstacle_position


def arucoDetecting(frame):
    arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
    arucoParams = cv2.aruco.DetectorParameters_create()
    # detect ArUco markers in the input frame
    (corners, ids, rejected) = cv2.aruco.detectMarkers(frame, arucoDict, parameters=arucoParams)
    scenery_points = {
        2: (0, 0),
        3: (0, 0),
        4: (0, 0),
        5: (0, 0)
    };
    #robot_points = {
    #    0: (0, 0)
    #}
    if len(corners) > 0:
        # flatten the ArUco IDs list
        ids = ids.flatten()
        # loop over the detected ArUCo corners
        for (markerCorner, markerID) in zip(corners, ids):
            # extract the marker corners (which are always returned
            # in top-left, top-right, bottom-right, and bottom-left
            # order)
            corners = markerCorner.reshape((4, 2))
            (topLeft, topRight, bottomRight, bottomLeft) = corners
            # convert each of the (x, y)-coordinate pairs to integers
            topRight = (int(topRight[0]), int(topRight[1]))
            bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
            bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
            topLeft = (int(topLeft[0]), int(topLeft[1]))
            # print(f'topRight {topRight} - topLeft {topLeft}')
            # draw the bounding box of the ArUCo detection
            cv2.line(frame, topLeft, topRight, (0, 255, 0), 2)
            cv2.line(frame, topRight, bottomRight, (0, 255, 0), 2)
            cv2.line(frame, bottomRight, bottomLeft, (0, 255, 0), 2)
            cv2.line(frame, bottomLeft, topLeft, (0, 255, 0), 2)
            # compute and draw the center (x, y)-coordinates of the
            # ArUco marker
            cX = int((topLeft[0] + bottomRight[0]) / 2.0)
            cY = int((topLeft[1] + bottomRight[1]) / 2.0)
            cv2.circle(frame, (cX, cY), 4, (0, 0, 255), -1)

            # draw the ArUco marker ID on the frame
            cv2.putText(frame, str(markerID),
                    (topLeft[0], topLeft[1] - 15),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 255, 0), 2)
            #if markerID == 0:
            #    robot_points[0] = (cX, cY)
           # else:
            scenery_points[markerID] = (cX, cY)
            # show the output frame
        print("Scenery ", scenery_points)
        #print("Robot ", robot_points)
        if scenery_points[2][0] > 0 and scenery_points[2][1] > 0 and scenery_points[3][0] > 0 and scenery_points[3][1] > 0:
            cv2.line(frame, scenery_points[2], scenery_points[3], (0, 255, 0), 2)
        if scenery_points[3][0] > 0 and scenery_points[3][1] > 0 and scenery_points[4][0] > 0 and scenery_points[4][0] > 0:
            cv2.line(frame, scenery_points[3], scenery_points[4], (0, 255, 0), 2)
        if scenery_points[4][0] > 0 and scenery_points[4][1] > 0 and scenery_points[5][0] > 0 and scenery_points[5][0] > 0:
            cv2.line(frame, scenery_points[4], scenery_points[5], (0, 255, 0), 2)
        if scenery_points[5][0] > 0 and scenery_points[5][1] > 0 and scenery_points[2][0] > 0 and scenery_points[2][0] > 0:
            cv2.line(frame, scenery_points[5], scenery_points[2], (0, 255, 0), 2)
    cv2.imshow("Cenario", frame)
    return scenery_points


