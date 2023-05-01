import numpy as np
import cv2
import os
import matplotlib.pyplot as plt
from scipy.signal import find_peaks


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


def mse(img1, img2):
    diff = cv2.subtract(img1, img2)
    err = np.sum(diff ** 2)
    mse = err / (float(height * width))
    return mse


def detect_shots(input_path):
    mse_list = []

    with open(input_path, 'rb') as f:
        data = np.fromfile(f, dtype=np.uint8, count=height*width*3)
        img = data.reshape((height, width, 3))
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        prev = img

        while True:

            data = np.fromfile(f, dtype=np.uint8, count=height*width*3)
            if data.size < height*width*3:
                break

            img = data.reshape((height, width, 3))
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            curr = img
            mse_list.append(mse(curr, prev))
            prev = curr

        plt.subplot(2, 1, 1)
        plt.plot(mse_list)

        mse_list = subtract_moving_average(mse_list, 10)
        max_value = max(mse_list)
        mse_list = [float(i)/max_value for i in mse_list]
        peaks, properties = find_peaks(
            mse_list, height=0.15, prominence=0.1, distance=18)

        # print(peaks)
        # print(properties)

        # for i in range(len(peaks)):
        #     print("Frame number: {}, height: {}, prominence: {}".format(
        #         peaks[i], properties['peak_heights'][i], properties['prominences'][i]))

        # plt.figure(1)
        # plt.subplot(2, 1, 2)
        # plt.plot(peaks, [mse_list[i] for i in peaks], "xr")
        # plt.plot(mse_list)
        # plt.show()

        return peaks


input_path = './input/The_Long_Dark_rgb/InputVideo.rgb'
output_path = './output/The_Long_Dark_rgb/frames'
# save_all_frames(input_path, output_path)

shots = detect_shots(input_path)
print(shots)


# plt.figure(2)
# plt.plot(mse_list2)
# plt.title('Predicted diff')


# # Load two frames
#     prev_frame = cv2.imread('./output/Ready_Player_One_rgb/frames/00001.jpg')
#     curr_frame = cv2.imread('./output/Ready_Player_One_rgb/frames/00002.jpg')

# Read the two frames from image files
# frame1 = cv2.imread('./output/Ready_Player_One_rgb/frames/00252.jpg')
# frame2 = cv2.imread('./output/Ready_Player_One_rgb/frames/00253.jpg')

# # Convert to grayscale
# prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
# curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)

# # Perform motion estimation using Lucas-Kanade algorithm
# lk_params = dict(winSize=(15, 15),
#                  maxLevel=2,
#                  criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
# prev_pts = cv2.goodFeaturesToTrack(prev_gray, mask=None, maxCorners=100, qualityLevel=0.3, minDistance=7)
# curr_pts, status, error = cv2.calcOpticalFlowPyrLK(prev_gray, curr_gray, prev_pts, None, **lk_params)

# # Draw motion vectors on the current frame
# mask = np.zeros_like(curr_frame)
# mask = mask.astype('uint8')

# for i, (prev, curr) in enumerate(zip(prev_pts, curr_pts)):
#     a, b = prev.ravel()
#     c, d = curr.ravel()
#     mask = cv2.arrowedLine(mask, (int(a), int(b)), (int(c), int(d)), (0, 255, 0), 2)
#     curr_frame = cv2.circle(curr_frame, (int(c), int(d)), 3, (0, 0, 255), -1)

# output = cv2.add(curr_frame, mask)
# cv2.imshow("output", output)
# cv2.waitKey(0)

# # Read the two frames from image files
# frame1 = cv2.imread('./output/Ready_Player_One_rgb/frames/03951.jpg')
# frame2 = cv2.imread('./output/Ready_Player_One_rgb/frames/03952.jpg')

# # Convert frames to grayscale
# gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
# gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

# # Compute optical flow using Farneback method
# flow = cv2.calcOpticalFlowFarneback(
#     gray1, gray2, None, 0.5, 5, 25, 100, 7, 1.5, 0)

# # Compute predicted frame from previous frame and flow vectors
# h, w = gray1.shape[:2]
# flow_map = np.zeros_like(flow)
# flow_map[..., 0] = flow[..., 0] + np.arange(w)
# flow_map[..., 1] = flow[..., 1] + np.arange(h)[:, np.newaxis]
# pred_gray2 = cv2.remap(gray1, flow_map, None, cv2.INTER_LINEAR)

# # Compute difference between predicted and actual frames
# diff = cv2.absdiff(gray2, gray1)
# pdiff = cv2.absdiff(gray2, pred_gray2)

# # Display the original frames and difference image
# cv2.imshow('frame1', frame1)
# cv2.imshow('frame2', frame2)
# cv2.imshow('diff', diff)
# cv2.imshow('pdiff', pdiff)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# # Read the two frames from image files
# frame1 = cv2.imread('./output/Ready_Player_One_rgb/frames/00001.jpg')
# frame2 = cv2.imread('./output/Ready_Player_One_rgb/frames/00002.jpg')

# # Convert frames to YCrCb color space
# ycc1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2YCrCb)
# ycc2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2YCrCb)

# # Split the YCrCb channels into separate images
# y1, cr1, cb1 = cv2.split(ycc1)
# y2, cr2, cb2 = cv2.split(ycc2)

# # Compute optical flow using Farneback method on Y channel
# flow = cv2.calcOpticalFlowFarneback(y1, y2, None, 0.5, 3, 15, 3, 5, 1.2, 0)

# # Compute predicted frame from previous frame and flow vectors
# h, w = y1.shape[:2]
# flow_map = np.zeros_like(flow)
# flow_map[..., 0] = flow[..., 0] + np.arange(w)
# flow_map[..., 1] = flow[..., 1] + np.arange(h)[:, np.newaxis]
# pred_y2 = cv2.remap(y1, flow_map, None, cv2.INTER_LINEAR)
# pred_cr2 = cv2.remap(cr1, flow_map, None, cv2.INTER_LINEAR)
# pred_cb2 = cv2.remap(cb1, flow_map, None, cv2.INTER_LINEAR)

# # Merge the predicted YCrCb channels back into a single image
# pred_ycc2 = cv2.merge([pred_y2, pred_cr2, pred_cb2])

# # Convert the predicted frame back to BGR color space
# pred_frame2 = cv2.cvtColor(pred_ycc2, cv2.COLOR_YCrCb2BGR)

# # Compute difference between predicted and actual frames
# diff = cv2.absdiff(frame2, frame1)
# pdiff = cv2.absdiff(frame2, pred_frame2)

# # Display the original frames and difference image
# cv2.imshow('frame1', frame1)
# cv2.imshow('frame2', frame2)
# cv2.imshow('diff', diff)
# cv2.imshow('pdiff', pdiff)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# https://learnopencv.com/optical-flow-in-opencv/#dense-optical-flow
