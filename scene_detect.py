import numpy as np
import cv2
from shot_detect import detect_shots

# Define the fixed size of the image frame
height = 270
width = 480


class Shot:
    def __init__(self, start_frame=None, end_frame=None):
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.subShots = []


def detect_scenes(input_path, shots, total_frames):
    frame_size = height*width*3
    file_data = np.memmap(input_path, dtype=np.uint8, mode='r')

    # x_coords = []
    # y_coords = []

    scenes = []
    curr_scene = []
    curr_shot = Shot()
    curr_shot.start_frame = 1

    for s in shots:
        prev_frame_number = s - 2
        start_index = (prev_frame_number - 1) * frame_size
        img_data = file_data[start_index:start_index+frame_size].tobytes()
        img = np.frombuffer(img_data, dtype=np.uint8)
        img = img.reshape((height, width, 3))
        img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
        prev = img

        next_frame_number = s + 2
        start_index = (next_frame_number - 1) * frame_size
        img_data = file_data[start_index:start_index+frame_size].tobytes()
        img = np.frombuffer(img_data, dtype=np.uint8)
        img = img.reshape((height, width, 3))
        img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
        next = img

        # Calculate the color histograms for each frame
        num_bins = 24
        hist1 = cv2.calcHist([prev], [0, 1, 2], None, [
            num_bins, num_bins, num_bins], [0, 256, 0, 256, 0, 256])
        hist2 = cv2.calcHist([next], [0, 1, 2], None, [
            num_bins, num_bins, num_bins], [0, 256, 0, 256, 0, 256])

        # Normalize the histograms
        hist1 = cv2.normalize(hist1, hist1).flatten()
        hist2 = cv2.normalize(hist2, hist2).flatten()

        # Calculate the Bhattacharyya distance between the histograms
        bhattacharyya_distance = cv2.compareHist(
            hist1, hist2, cv2.HISTCMP_BHATTACHARYYA)

        curr_shot.end_frame = s-1
        curr_scene.append(curr_shot)

        curr_shot = Shot()
        curr_shot.start_frame = s

        if bhattacharyya_distance >= 0.7:
            scenes.append(curr_scene)
            curr_scene = []

        # x_coords.append(s)
        # y_coords.append(bhattacharyya_distance)

    curr_shot.end_frame = total_frames
    curr_scene.append(curr_shot)
    scenes.append(curr_scene)

    del file_data
    return scenes


def print_scenes(scenes):
    scene_no = 1
    for scene in scenes:
        print("Scene {}".format(scene_no))
        shot_no = 1
        for shot in scene:
            print("Shot: {}, start: {}, end: {}".format(
                shot_no, shot.start_frame, shot.end_frame))
            shot_no += 1
        scene_no += 1


input_path = './input/Ready_Player_One_rgb/InputVideo.rgb'
# shots = [163, 253, 421, 509, 898, 1081, 1132, 1180, 1353, 1966, 2333, 2460, 2584, 2718, 3149, 3245, 3264, 3285, 3548, 3621, 3730, 3771, 3810, 3849, 3880, 3991, 4054, 4083, 4130,
#          4233, 4348, 4493, 4725, 4845, 5330, 5600, 5755, 5953, 6141, 6304, 6858, 6970, 7049, 7459, 7592, 7670, 7836, 7877, 7901, 7986, 8019, 8081, 8115, 8179, 8270, 8313, 8370, 8511]
# total_frames = 8682

# input_path = './input/The_Long_Dark_rgb/InputVideo.rgb'
# shots = [184, 314, 447, 621, 799, 933, 1101, 1237, 1322, 1412, 1499, 1587, 1768, 1944, 2027,
#          2116, 2209, 2298, 2387, 2474, 2651, 2827, 3001, 3176, 3411, 3684, 4060, 4287, 4668, 4958, 5653]
# total_frames = 6276

# input_path = './input/The_Great_Gatsby_rgb/InputVideo.rgb'
# shots = [1688, 1820, 1894, 2143, 2722, 2788, 2838, 3080, 3322, 3712, 3805, 3959, 4329, 4383, 4437, 4474, 4553,
#          4607, 4649, 4712, 4742, 4775, 4805, 4865, 4913, 4959, 5009, 5035, 5083, 5108, 5145, 5214, 5259, 5335, 5373]
# total_frames = 5686

shots, total_frames = detect_shots(input_path)

scenes = detect_scenes(input_path, shots, total_frames)
print_scenes(scenes)
