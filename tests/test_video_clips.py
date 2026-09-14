import importlib


def load_module():
    return importlib.import_module(
        "replay_corner_analyzer.video_clips"
    )


def test_align_second_half_clip_to_video():
    module = load_module()

    manifest = [
        {
            "event_id": "corner-1",
            "minute": 51,
            "second": 40,
            "period": 2,
            "timestamp": "00:06:40.000",
            "event_time_seconds": 3100,
            "clip_start_seconds": 3095,
            "clip_end_seconds": 3115,
        }
    ]

    aligned = module.align_manifest_to_video(
        manifest,
        first_half_kickoff=120,
        second_half_kickoff=3440,
    )

    clip = aligned[0]

    assert clip["video_event_time_seconds"] == 3840
    assert clip["video_clip_start_seconds"] == 3835
    assert clip["video_clip_end_seconds"] == 3855


def test_align_first_half_clip_to_video():
    module = load_module()

    manifest = [
        {
            "event_id": "corner-1",
            "minute": 10,
            "second": 40,
            "period": 1,
            "timestamp": "00:10:40.000",
            "event_time_seconds": 640,
            "clip_start_seconds": 635,
            "clip_end_seconds": 655,
        }
    ]

    aligned = module.align_manifest_to_video(
        manifest,
        first_half_kickoff=120,
        second_half_kickoff=3440,
    )

    clip = aligned[0]

    assert clip["video_event_time_seconds"] == 760
    assert clip["video_clip_start_seconds"] == 755
    assert clip["video_clip_end_seconds"] == 775


def test_build_ffmpeg_command_uses_aligned_times():
    module = load_module()

    command = module.build_ffmpeg_command(
        ffmpeg_bin="ffmpeg",
        video_path="match.mp4",
        output_path="clip.mp4",
        start_seconds=3835,
        end_seconds=3855,
    )

    assert command[0] == "ffmpeg"
    assert "3835.000" in command
    assert "20.000" in command
    assert command[-1] == "clip.mp4"
