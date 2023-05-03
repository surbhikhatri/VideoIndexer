import numpy as np
import cv2
import os
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from skimage import metrics


# Define the fixed size of the image frame
height = 270
width = 480


def save_all_frames(input_path, output_path):
    try:
        os.makedirs(output_path, exist_ok=True)
    except OSError:
        print("failed to create directory")
        return

    count = 1
    with open(input_path, 'rb') as f:
        while True:

            data = np.fromfile(f, dtype=np.uint8, count=height*width*3)
            if data.size < height*width*3:
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
            avg = sum(signal[:i+1]) / (i+1)
        else:
            # Use a trailing moving average once we have enough samples
            avg = sum(signal[i-window_size+1:i+1]) / window_size
        moving_avg.append(avg)
    detrended_signal = [signal[i] - moving_avg[i] for i in range(len(signal))]
    return detrended_signal


def detect_shots(input_path):
    ssim_list = []
    print("Shot Detection")

    with open(input_path, 'rb') as f:
        print("Processing frame number: 1")
        data = np.fromfile(f, dtype=np.uint8, count=height*width*3)
        img = data.reshape((height, width, 3))
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        prev2 = img

        print("Processing frame number: 2")
        data = np.fromfile(f, dtype=np.uint8, count=height*width*3)
        img = data.reshape((height, width, 3))
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        prev = img

        count = 2
        while True:

            data = np.fromfile(f, dtype=np.uint8, count=height*width*3)
            if data.size < height*width*3:
                break

            count += 1
            print("Processing frame number: {}".format(count))
            img = data.reshape((height, width, 3))
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            curr = img
            ssim_score = metrics.structural_similarity(
                curr, prev2, multichannel=True, channel_axis=2)
            ssim_list.append(1-ssim_score)
            prev2 = prev
            prev = curr

        # plt.subplot(2, 1, 1)
        # plt.plot(ssim_list)

        ssim_list = subtract_moving_average(ssim_list, 10)
        peaks, properties = find_peaks(
            ssim_list, height=0.15, prominence=0.1, distance=18)

        # print(peaks)
        # print(properties)

        # for i in range(len(peaks)):
        #     print("Frame number: {}, height: {}, prominence: {}".format(
        #         peaks[i], properties['peak_heights'][i], properties['prominences'][i]))

        # plt.figure(1)
        # plt.subplot(2, 1, 2)
        # plt.plot(peaks, [ssim_list[i] for i in peaks], "xr")
        # plt.plot(ssim_list)
        # plt.show()

        # The frame numbers we return as shot boundaries should be
        # the first frame of the next shot
        shots = [x + 3 for x in peaks]
        return shots, count
