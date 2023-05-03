import cv2
import numpy as np
from scipy.signal import find_peaks
from skimage import metrics

from shot_detect import subtract_moving_average

height = 270
width = 480


def detect_subshots(frames, start_frame):
    ssim_list = []
    print("Subshot Detection")

    data = frames[0]
    img = data.reshape((height, width, 3))
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    prev2 = img

    print("Processing frame number:", start_frame)
    data = frames[1]
    img = data.reshape((height, width, 3))
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    prev = img

    count = 2
    for frame in frames:
        data = frame
        if data.size < height*width*3:
            break
        count += 1
        img = data.reshape((height, width, 3))
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        curr = img
        ssim_score = metrics.structural_similarity(
            curr, prev2, multichannel=True, channel_axis=2)
        ssim_list.append(1-ssim_score)
        prev2 = prev
        prev = curr

    ssim_list = subtract_moving_average(ssim_list, 10)
    peaks, properties = find_peaks(
        ssim_list, height=0.095, prominence=0.1, distance=18)

    shots = []
    for x in peaks:
        if abs(x > 100) and abs(len(frames) - x) > 100:
            shots.append(x + start_frame + 3)

    return shots, count + start_frame


def detect_subshots_wrapper(input_path, scenes):
    frame_size = height * width * 3
    file_data = np.memmap(input_path, dtype=np.uint8, mode='r')

    for scene in scenes:
        for shot_number in range(0, len(scene)):
            shot = scene[shot_number]

            # filter based on shot duration
            if shot.end_frame - shot.start_frame > 500:
                images = []
                for frame_number in range(shot.start_frame, shot.end_frame + 1):
                    start_index = frame_number * frame_size
                    img_data = file_data[start_index:start_index + frame_size].tobytes()
                    img = np.frombuffer(img_data, dtype=np.uint8)
                    if img.size == 0:
                        break
                    img = img.reshape((height, width, 3))
                    images.append(img)
                subshots, count = detect_subshots(images, shot.start_frame)
                shot.subshots = subshots
    return scenes
