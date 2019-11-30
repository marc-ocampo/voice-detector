This section contains default files for training and testing the application.

`files/train` contains the voice models for training the application.

`files/test` contains the voice models for testing the application.

* `files/test/hello5.wav` is from the same person in `files/train/hello[1-4].wav` (for repeatability)

* `files/test/hello-other.wav` is from a different person using the same key phrases

* `files/test/noise/*wav` contains sound files with varied ratio of informtaion from `files/train/hello1.wav` and white noise (to test the algorithm's robustness against noise)