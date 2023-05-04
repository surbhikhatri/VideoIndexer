import librosa
import numpy as np
from scipy.signal import find_peaks


def detect_subshots_v2(start_frame, end_frame, fps, audio_path):

    print('Detecting subshots between frame number: {} and frame number: {}'.format(
        start_frame, end_frame))
    y, sampling_rate = librosa.load(audio_path, sr=None)

    # Calculate start and end timestamp of the shot in seconds
    start_time = float(start_frame)/float(fps)
    end_time = float(end_frame)/float(fps)

    # Compute the starting and ending samples in the audio based on the timestamps
    start_sample = int(start_time * sampling_rate)
    end_sample = int(end_time * sampling_rate)

    audio_segment = y[start_sample:end_sample]

    # Define window size in seconds
    window_size = 1

    samples_per_window = int(window_size * sampling_rate)
    num_windows = int(np.ceil(len(audio_segment) / samples_per_window))

    # Compute the average amplitude for each window
    amplitudes = []
    for i in range(num_windows):
        window_start = i * samples_per_window
        window_end = min((i + 1) * samples_per_window, len(audio_segment))
        window = audio_segment[window_start:window_end]
        amplitude = np.mean(np.abs(window))
        amplitudes.append(amplitude)

    # Compute the difference in amplitude between subsequent windows
    diffs = np.diff(amplitudes)

    # We need to find the peaks in the diffs array.
    # In order to make sure that do not find a peak very close
    # to the start or end of the signal, we introduce high samples
    # (of value 1) at index 1 and len - 1. The peak detection
    # algorithm should pick these up as peaks which we ignore
    # and the distance parameter ensures the required
    # distance between the peaks
    ndiffs = np.insert(diffs, 1, 0.1)
    ndiffs = np.insert(ndiffs, len(ndiffs)-1, 1)
    # print(len(ndiffs))
    # print(ndiffs)

    # We need peaks to be at least 3 seconds apart
    distance = int(float(3) / float(window_size))
    peaks, properties = find_peaks(ndiffs, height=0.004, distance=distance)
    # print(peaks)

    # Ignore the first and the last peaks to get the actual peaks.
    # We also subtract 1, because when we added a peak in the beginning,
    # we would have offset the indices by 1.
    actual_peaks = peaks[1:len(peaks) - 1]
    actual_peaks = [x - 1 for x in actual_peaks]
    # print(actual_peaks)

    subshot_frames = []
    for p in actual_peaks:
        frame_timestamp = start_time + (p * window_size)
        frame_number = int(fps * frame_timestamp)
        subshot_frames.append(frame_number)

    return subshot_frames


def populate_subshots(audio_path, scenes, fps):
    for scene in scenes:
        for shot in scene:
            # filter based on shot duration
            if shot.end_frame - shot.start_frame >= 180:
                subshots = detect_subshots_v2(
                    shot.start_frame, shot.end_frame, fps, audio_path)
                shot.subshots = subshots
    return scenes
