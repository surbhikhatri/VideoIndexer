# VideoIndexer

Course Project for CSCI 576 - Multimedia Systems Design

A tool to automatically detect shots, sub-shots and scenes in a given video file.
Includes a video player that list the scenes / shots and can be used to seek to each scene / shot.

Shot detection is based on Structural Similarity Index (SSIM) between consecutive frames. SSIM values peak at shot boundaries. We use some signal processing techniques
to identify the required peaks.

Shots are grouped into scenes based on the color distribution in the frames. We use
Bhattacharyya distance as a measure to compare color histograms at shot boundaries.
A simple threshold is used to identify scene boundaries.

Longer shots are sometimes broken down into sub-shots based on audio. We process
the audio segment for each shot in one second windows and compute the difference in
average amplitude of the audio. We then use signal processing techniques to detect
the required peaks which define instances which divide a shot into multiple sub-shots.

Demo Gif  

![](https://github.com/surbhikhatri/VideoIndexer/blob/main/demo.gif)
