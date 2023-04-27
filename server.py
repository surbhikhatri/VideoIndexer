from PreProcessInput import video_to_frames

if __name__ == "__main__":
    input_path = './../input/Ready_Player_One_rgb/InputVideo.mp4'
    output_path = './output/Ready_Player_One_rgb/actual'
    output_differ_path = './output/Ready_Player_One_rgb/differ'
    video_to_frames(input_path, output_path, output_differ_path)
