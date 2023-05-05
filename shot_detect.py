import numpy as np
import cv2
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from skimage import metrics

from utils import subtract_moving_average


def detect_shots(input_path, height, width):
    ssim_list = []
    print("Shot Detection")

    with open(input_path, 'rb') as f:
        print("Processing frame number: 1")
        data = np.fromfile(f, dtype=np.uint8, count=height * width * 3)
        img = data.reshape((height, width, 3))
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        prev2 = img

        print("Processing frame number: 2")
        data = np.fromfile(f, dtype=np.uint8, count=height * width * 3)
        img = data.reshape((height, width, 3))
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        prev = img

        count = 2
        while True:
            data = np.fromfile(f, dtype=np.uint8, count=height * width * 3)
            if data.size < height * width * 3:
                break

            count += 1
            print("Processing frame number: {}".format(count))
            img = data.reshape((height, width, 3))
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            curr = img
            ssim_score = metrics.structural_similarity(
                curr, prev2, multichannel=True, channel_axis=2)
            ssim_list.append(1 - ssim_score)
            prev2 = prev
            prev = curr

        ssim_list = subtract_moving_average(ssim_list, 10)
        peaks, properties = find_peaks(
            ssim_list, height=0.15, prominence=0.1, distance=18)

        # The frame numbers we return as shot boundaries should be
        # the first frame of the next shot
        shots = [x + 3 for x in peaks]
        return shots, count
