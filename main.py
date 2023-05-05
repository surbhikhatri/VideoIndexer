import sys
from PyQt5 import QtWidgets

from video_player import VideoPlayer
from shot_detect import detect_shots
from scene_detect import detect_scenes
from subshot_detect_v2 import populate_subshots
from utils import print_scenes


if __name__ == "__main__":

    # Define the parameters of the video
    fps = 30
    height = 270
    width = 480

    if len(sys.argv) == 4:
        input_rgb_path = sys.argv[1]
        input_mp4_path = sys.argv[2]
        input_audio_path = sys.argv[3]

        shots, total_frames = detect_shots(input_rgb_path, height, width)
    else:
        # Hardcoding some defaults for convenience if command line arguments are not provided
        input_rgb_path = './input/Ready_Player_One_rgb/InputVideo.rgb'
        input_mp4_path = './input/Ready_Player_One_rgb/InputVideo.mp4'
        input_audio_path = './input/Ready_Player_One_rgb/InputAudio.wav'
        shots = [163, 253, 421, 509, 898, 1081, 1132, 1180, 1353, 1966, 2333, 2460, 2584, 2718, 3149, 3245, 3264, 3285, 3548, 3621, 3730, 3771, 3810, 3849, 3880, 3991, 4054, 4083,
                 4130, 4233, 4348, 4493, 4725, 4845, 5330, 5600, 5755, 5953, 6141, 6304, 6858, 6970, 7049, 7459, 7592, 7670, 7836, 7877, 7901, 7986, 8019, 8081, 8115, 8179, 8270, 8313, 8370, 8511]
        total_frames = 8682

    scenes = detect_scenes(input_rgb_path, shots, total_frames, height, width)
    scenes = populate_subshots(input_audio_path, scenes, fps)
    print_scenes(scenes)

    app = QtWidgets.QApplication(sys.argv)
    player = VideoPlayer(master=None, scenes=scenes, total_frames=total_frames)
    player.show()
    player.resize(1100, 700)
    player.open_file(input_mp4_path)
    sys.exit(app.exec_())
