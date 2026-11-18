"""Replace a video's soundtrack, preserving the encoded video stream."""
import argparse
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import tempfile


def ffmpeg(*arguments):
    result = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostdin", *map(str, arguments)],
        capture_output=True, text=True,
    )
    if result.returncode:
        raise ValueError(result.stderr.strip())
    return result.stderr


def mux(video, audio, output):
    if output.suffix.lower() != ".mp4":
        raise ValueError("Choose an .mp4 output file.")
    if output.exists():
        raise ValueError(f"Output already exists: {output}")
    target = "loudnorm=I=-14:TP=-1.5:LRA=10"
    log = ffmpeg("-i", audio, "-map", "0:a:0", "-af", target + ":print_format=json",
                 "-f", "null", "-")
    report = re.search(r'\{[^{}]*"input_i"[^{}]*\}', log)
    if not report:
        raise ValueError("FFmpeg returned no loudness measurements.")
    data = json.loads(report.group())
    params = {"measured_I": "input_i", "measured_TP": "input_tp",
              "measured_LRA": "input_lra", "measured_thresh": "input_thresh",
              "offset": "target_offset"}
    options = []
    for name, key in params.items():
        value = float(data[key])
        if not math.isfinite(value):
            raise ValueError("Audio too quiet or too short to measure.")
        options.append(f"{name}={value}")
    audio_filter = ":".join([target, *options, "linear=true"])
    with tempfile.TemporaryDirectory(dir=output.parent) as temp:
        rendered = Path(temp) / "render.mp4"
        ffmpeg("-i", video, "-i", audio, "-map", "0:v:0", "-map", "1:a:0",
               "-af", audio_filter, "-c:v", "copy", "-c:a", "aac", "-ar", "48000",
               "-b:a", "320k", "-shortest", "-movflags", "+faststart", rendered)
        output.hardlink_to(rendered)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("video", "audio", "output"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    try:
        mux(args.video, args.audio, args.output)
    except (OSError, ValueError) as error:
        sys.exit(str(error))
