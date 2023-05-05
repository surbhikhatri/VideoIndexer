import numpy as np
import cv2


class Shot:
    def __init__(self, start_frame=None, end_frame=None):
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.subshots = []


def detect_scenes(input_path, shots, total_frames, height, width):
    frame_size = height * width * 3
    file_data = np.memmap(input_path, dtype=np.uint8, mode='r')

    scenes = []
    curr_scene = []
    curr_shot = Shot()
    curr_shot.start_frame = 1

    for s in shots:
        prev_frame_number = s - 2
        start_index = (prev_frame_number - 1) * frame_size
        img_data = file_data[start_index: start_index + frame_size].tobytes()
        img = np.frombuffer(img_data, dtype=np.uint8)
        prev_rgb = img.reshape((height, width, 3))
        prev_hsv = cv2.cvtColor(prev_rgb, cv2.COLOR_RGB2HSV)

        next_frame_number = s + 2
        start_index = (next_frame_number - 1) * frame_size
        img_data = file_data[start_index: start_index + frame_size].tobytes()
        img = np.frombuffer(img_data, dtype=np.uint8)
        next_rgb = img.reshape((height, width, 3))
        next_hsv = cv2.cvtColor(next_rgb, cv2.COLOR_RGB2HSV)

        # Calculate the color histograms for each frame
        hsv_hist1 = cv2.calcHist([prev_hsv], [0, 1, 2], None, [
                                 18, 32, 32], [0, 180, 0, 256, 0, 256])
        hsv_hist2 = cv2.calcHist([next_hsv], [0, 1, 2], None, [
                                 18, 32, 32], [0, 180, 0, 256, 0, 256])

        # Normalize the histograms
        hsv_hist1 = cv2.normalize(hsv_hist1, hsv_hist1).flatten()
        hsv_hist2 = cv2.normalize(hsv_hist2, hsv_hist2).flatten()

        # Calculate the Bhattacharyya distance between the histograms
        bhattacharyya_hsv = cv2.compareHist(
            hsv_hist1, hsv_hist2, cv2.HISTCMP_BHATTACHARYYA)

        curr_shot.end_frame = s - 1
        curr_scene.append(curr_shot)

        curr_shot = Shot(s)

        if bhattacharyya_hsv >= 0.7:
            scenes.append(curr_scene)
            curr_scene = []

    curr_shot.end_frame = total_frames
    curr_scene.append(curr_shot)
    scenes.append(curr_scene)

    del file_data
    return scenes
