import os
import cv2
import numpy as np


def save_all_frames(input_path, output_path, height, width):
    try:
        os.makedirs(output_path, exist_ok=True)
    except OSError:
        print("failed to create directory")
        return

    count = 1
    with open(input_path, 'rb') as f:
        while True:

            data = np.fromfile(f, dtype=np.uint8, count=height * width * 3)
            if data.size < height * width * 3:
                return

            img = data.reshape((height, width, 3))
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

            # Save as a JPEG file
            ret = cv2.imwrite(output_path + "/%#05d.jpg" % count, img)
            if (not ret):
                print("Error saving frame number: {}".format(count))
                return
            count += 1


def subtract_moving_average(signal, window_size=10):
    moving_avg = []
    for i in range(len(signal)):
        if i < window_size:
            # Use a centered moving average until we have enough samples
            avg = sum(signal[: i + 1]) / (i + 1)
        else:
            # Use a trailing moving average once we have enough samples
            avg = sum(signal[i - window_size + 1: i + 1]) / window_size
        moving_avg.append(avg)
    detrended_signal = [signal[i] - moving_avg[i] for i in range(len(signal))]
    return detrended_signal


def print_scenes(scenes):
    print("\n\nScene - Shot - Subshots \n\n")
    scene_no = 1
    for scene in scenes:
        print("Scene {}\n".format(scene_no))
        shot_no = 1
        for shot in scene:
            print("Shot: {}, start: {}, end: {}, length: {}".format(
                shot_no, shot.start_frame, shot.end_frame, shot.end_frame - shot.start_frame))
            subshot_no = 1
            for subshot in shot.subshots:
                print("    Subshot: {}, frame: {}".format(subshot_no, subshot))
                subshot_no += 1
            shot_no += 1
        scene_no += 1
        print("\n")
