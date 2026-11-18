# ChaosLab Mux

Replace the soundtrack of an MP4 while copying its encoded video stream. The tool measures the first audio stream in the supplied soundtrack, then uses those measurements for a second FFmpeg loudnorm pass targeting −14 LUFS integrated and −1.5 dBTP before AAC encoding. Output ends at the shorter input.

Requires Python 3.10 or newer, FFmpeg with loudnorm and AAC support, an MP4-compatible video stream and an output directory that supports hard links. Existing output files are preserved.

    python3 mux.py silent-video.mp4 soundtrack.wav finished.mp4

## Try it with generated media

In a directory containing mux.py, run:

    ffmpeg -f lavfi -i color=c=blue:s=320x180:r=25:d=3 -c:v mpeg4 demo-video.mp4
    ffmpeg -f lavfi -i sine=frequency=440:duration=3 demo-audio.wav
    python3 mux.py demo-video.mp4 demo-audio.wav demo-result.mp4
    ffprobe -v error -show_entries stream=codec_name,codec_type -of compact demo-result.mp4

The result contains an MPEG-4 video stream and an AAC audio stream. A silent soundtrack cannot produce a finite loudness measurement.
