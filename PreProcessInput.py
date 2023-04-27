import cv2
import time
import os
import numpy as np
import pandas as panda

initialState = None
motionTrackList = [None, None]
motionTime = []
dataFrame = panda.DataFrame(columns=["Initial", "Final"])


def mse(img1, img2):
    h, w = img1.shape
    diff = cv2.subtract(img1, img2)
    err = np.sum(diff ** 2)
    mse = err / (float(h * w))
    return mse, diff


def video_to_frames(input_loc, output_loc, output_differ_path):
    shots_frames_path = './output/Ready_Player_One_rgb/shots'
    global initialState, motionTrackList, dataFrame
    try:
        os.makedirs(output_loc, exist_ok=True)
        os.makedirs(output_differ_path, exist_ok=True)
        os.makedirs(shots_frames_path, exist_ok=True)
    except OSError:
        print("failed to create directory")
        return

    # Log the time
    time_start = time.time()
    # Start capturing the feed
    video = cv2.VideoCapture(input_loc)
    # Find the number of frames
    video_length = int(video.get(cv2.CAP_PROP_FRAME_COUNT)) - 1
    print("Frames:", video_length)
    count = 0
    previous_frame = None
    shots = []

    while video.isOpened():
        check, frame = video.read()
        gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_frame = cv2.GaussianBlur(gray_image, (21, 21), 0)

        if initialState is None:
            initialState = gray_frame

        if previous_frame is None:
            previous_frame = gray_frame

        if len(shots) == 0:
            shots.append(previous_frame)

        error, new_differ = mse(previous_frame, gray_frame)
        if error > 22.5:
            if abs(error - mse(shots[-1], previous_frame)[0]) > 20:
                shots.append(gray_frame)
                # comment this to avoid writing the frames
                cv2.imwrite(shots_frames_path + "/%#05d.jpg" % (count + 1), gray_frame)

        cv2.imwrite(output_loc + "/%#05d.jpg" % (count + 1), frame)
        cv2.imwrite(output_differ_path + "/%#05d.jpg" % (count + 1), new_differ)

        # cv2.imshow("The image captured in the Gray Frame is shown below: ", gray_frame)
        # cv2.imshow("Difference between the  inital static frame and the current frame: ", new_differ)

        count = count + 1
        previous_frame = gray_frame

        if count > (video_length - 1):
            time_end = time.time()
            print("Done extracting frames.\n%d frames extracted" % count)
            print("It took %d seconds for conversion." % (time_end - time_start))
            break

    video.release()
    cv2.destroyAllWindows()
