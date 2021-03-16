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


def robotDetecting(frame):
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    low_green = np.array([25, 130, 72])
    high_green = np.array([102, 255, 255])
    green_mask = cv2.inRange(hsv_frame, low_green, high_green)
    img_robot = cv2.bitwise_and(frame, frame, mask=green_mask)
    img_gray_robot = cv2.cvtColor(img_robot, cv2.COLOR_BGR2GRAY)
    # convert image to grayscale image
    blurred = cv2.GaussianBlur(img_gray_robot, (5, 5), 0)
    thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]
    # find contours in the thresholded image
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cX_robot = 0
    cY_robot = 0
    robot_position = np.array([0, 0, 0, 0])
    # left, right, top , button
    # loop over the contours
    for c in cnts:
        # compute the center of the contour
        M = cv2.moments(c)
        if M["m00"] > 0:
            cX_robot = int(M["m10"] / M["m00"])
            cY_robot = int(M["m01"] / M["m00"])
            # draw the contour and center of the shape on the image
            cv2.drawContours(img_robot, [c], -1, (0, 255, 0), 2)
            cv2.circle(img_robot, (cX_robot, cY_robot), 8, (255, 255, 255), -1)
            cv2.putText(img_robot, "Robot", (cX_robot - 20, cY_robot - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        # show the image
        #cv2.imshow("Robot", img_robot)
        # plt.imshow(img_green)
        # plt.show()
    print("X: ", cX_robot, " Y: ", cY_robot)
    robot_position[0] = cX_robot + 5
    robot_position[1] = cX_robot + 5
    robot_position[2] = cX_robot + 8
    robot_position[3] = cX_robot + 8


def arucoDetecting(frame):
    arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
    arucoParams = cv2.aruco.DetectorParameters_create()
    # detect ArUco markers in the input frame
    (corners, ids, rejected) = cv2.aruco.detectMarkers(frame, arucoDict, parameters=arucoParams)
    aruco_list = {
        2: (0, 0),
        3: (0, 0),
        4: (0, 0),
        5: (0, 0)
    };

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
            aruco_list[markerID] = (cX, cY)
            # show the output frame
        print(aruco_list)
        if aruco_list[2][0] > 0 and aruco_list[2][1] > 0 and aruco_list[3][0] > 0 and aruco_list[3][1] > 0:
            cv2.line(frame, aruco_list[2], aruco_list[3], (0, 255, 0), 2)
        if aruco_list[3][0] > 0 and aruco_list[3][1] > 0 and aruco_list[4][0] > 0 and aruco_list[4][0] > 0:
            cv2.line(frame, aruco_list[3], aruco_list[4], (0, 255, 0), 2)
        if aruco_list[4][0] > 0 and aruco_list[4][1] > 0 and aruco_list[5][0] > 0 and aruco_list[5][0] > 0:
            cv2.line(frame, aruco_list[4], aruco_list[5], (0, 255, 0), 2)
        if aruco_list[5][0] > 0 and aruco_list[5][1] > 0 and aruco_list[2][0] > 0 and aruco_list[2][0] > 0:
            cv2.line(frame, aruco_list[5], aruco_list[2], (0, 255, 0), 2)
        cv2.imshow("Arena", frame)


