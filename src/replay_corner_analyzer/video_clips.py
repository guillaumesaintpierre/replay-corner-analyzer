"""Align match events to broadcast video and generate clips with FFmpeg."""

import re
import shutil
import subprocess
from pathlib import Path

import pandas as pd


def _timestamp_seconds(timestamp: str) -> float:
    """Convert a period-relative timestamp to seconds."""
    return float(
        pd.to_timedelta(timestamp).total_seconds()
    )


def align_manifest_to_video(
    manifest: list[dict],
    *,
    first_half_kickoff: float,
    second_half_kickoff: float,
) -> list[dict]:
    """
    Convert StatsBomb period-relative timestamps into video timestamps.

    first_half_kickoff and second_half_kickoff are seconds from the
    beginning of the video file.
    """
    aligned = []

    for original in manifest:
        clip = dict(original)

        period = int(clip["period"])
        timestamp = clip["timestamp"]

        period_seconds = _timestamp_seconds(
            timestamp
        )

        if period == 1:
            kickoff = float(
                first_half_kickoff
            )

        elif period == 2:
            kickoff = float(
                second_half_kickoff
            )

        else:
            raise ValueError(
                "Only periods 1 and 2 are currently "
                f"supported, got period={period}"
            )

        pre_roll = (
            float(clip["event_time_seconds"])
            - float(clip["clip_start_seconds"])
        )

        post_roll = (
            float(clip["clip_end_seconds"])
            - float(clip["event_time_seconds"])
        )

        video_event = (
            kickoff + period_seconds
        )

        video_start = max(
            0.0,
            video_event - pre_roll,
        )

        video_end = (
            video_event + post_roll
        )

        clip["period_time_seconds"] = (
            period_seconds
        )

        clip["video_event_time_seconds"] = (
            video_event
        )

        clip["video_clip_start_seconds"] = (
            video_start
        )

        clip["video_clip_end_seconds"] = (
            video_end
        )

        aligned.append(clip)

    return aligned


def build_ffmpeg_command(
    *,
    ffmpeg_bin: str,
    video_path,
    output_path,
    start_seconds: float,
    end_seconds: float,
) -> list[str]:
    """Build a precise FFmpeg clip command."""
    duration = (
        float(end_seconds)
        - float(start_seconds)
    )

    if duration <= 0:
        raise ValueError(
            "Clip duration must be positive."
        )

    return [
        str(ffmpeg_bin),
        "-y",
        "-ss",
        f"{float(start_seconds):.3f}",
        "-i",
        str(video_path),
        "-t",
        f"{duration:.3f}",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "23",
        "-c:a",
        "aac",
        "-movflags",
        "+faststart",
        str(output_path),
    ]


def _safe_name(text: str) -> str:
    text = text.lower()

    text = re.sub(
        r"[^a-z0-9]+",
        "-",
        text,
    )

    return text.strip("-")


def create_video_clips(
    manifest: list[dict],
    *,
    video_path,
    clips_dir,
) -> list[Path]:
    """Generate MP4 clips from an aligned manifest."""
    video_path = Path(video_path)

    if not video_path.exists():
        raise FileNotFoundError(
            f"Video file not found: {video_path}"
        )

    ffmpeg_bin = shutil.which(
        "ffmpeg"
    )

    if ffmpeg_bin is None:
        raise RuntimeError(
            "FFmpeg is not installed or is not "
            "available in PATH."
        )

    clips_dir = Path(clips_dir)

    clips_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_files = []

    for number, clip in enumerate(
        manifest,
        start=1,
    ):
        minute = int(
            clip["minute"]
        )

        second = int(
            clip["second"]
        )

        team = _safe_name(
            str(clip["team"])
        )

        filename = (
            f"clip_{number:03d}_"
            f"{minute:02d}-{second:02d}_"
            f"{team}.mp4"
        )

        output_path = (
            clips_dir / filename
        )

        command = build_ffmpeg_command(
            ffmpeg_bin=ffmpeg_bin,
            video_path=video_path,
            output_path=output_path,
            start_seconds=clip[
                "video_clip_start_seconds"
            ],
            end_seconds=clip[
                "video_clip_end_seconds"
            ],
        )

        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
        )

        if process.returncode != 0:
            raise RuntimeError(
                "FFmpeg failed while creating "
                f"{output_path}:\n"
                f"{process.stderr[-2000:]}"
            )

        output_files.append(
            output_path
        )

    return output_files
