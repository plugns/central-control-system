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
        cv2.imshow("Robot", img_robot)
        # plt.imshow(img_green)
        # plt.show()
    print("X: ", cX_robot, " Y: ", cY_robot)
    robot_position[0] = cX_robot + 5
    robot_position[1] = cX_robot + 5
    robot_position[2] = cX_robot + 8
    robot_position[3] = cX_robot + 8


