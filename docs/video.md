# Hardware video decoding and playback — 2026-10-16

Tested on the [same J613 stack](tested-stack.md), with the GPU ceiling still
at 618 MHz. These are generated H.264 test-pattern clips, not browser tests.

## Decoder correctness

The Apple AVD was used through `libva-v4l2_request-avd` on `/dev/video0`.
FFmpeg decoded the same six-second 1280×720/30 fps clip through VA-API and
software, converting both to NV12 before frame checksums. **All 180 frame
checksums matched.** This qualifies that clip's decoded pixels, not every codec.

The operator replayed both normal mpv defaults (VA-API + gpu-next) and
VA-API-copy + OpenGL and reported that both looked good. The installed Asahi
template mentions a green-frame problem on another path; it was not reproduced
in this 720p comparison. Do not force its workaround solely from that comment.

## Presentation performance

The panel was 2560×1664 at 60 Hz and scale 1. Each 1080p run was eight seconds;
the 60 fps clips contain 480 frames and the 30 fps clip contains 240. No audio
was played. Counts below are mpv presentation drops; decoder drops were zero
in every run.

| Mode | Presentation drops |
| --- | ---: |
| 1080p60, defaults, windowed | 28 |
| 1080p60, defaults, windowed repeat | 20 |
| 1080p60, defaults, fullscreen | 123 |
| 1080p60, VA-API-copy + OpenGL, windowed | 203 |
| 1080p60, defaults plus built-in fast profile, windowed | 0 |
| 1080p30, defaults, windowed | 0 |

Unlike the M4 reference's reported geometry result, fullscreen was worse here.
The decoder worked; rendering/presentation and the fixed low GPU ceiling remain
possible constraints. These short, mostly single-run measurements do not isolate
the root cause or establish long-session performance. Window sizes and background
desktop work were not tightly controlled. The default repeat reduces, but does
not eliminate, shader warm-up as an explanation.

## Optional fast preset

The local `~/.config/mpv/mpv.conf` now contains only this named preset:

```ini
[m3-fast]
profile=fast
```

Use `mpv --profile=m3-fast video.mp4`, or use mpv's built-in
`--profile=fast` without installing a named preset. Ordinary playback keeps its
existing defaults. The fast profile uses bilinear scaling and disables dithering,
correct/linear downscaling, sigmoid upscaling and HDR peak computation, so it
trades processing quality for lower rendering cost. HDR was not tested.

Counters can be collected with:

```sh
mpv --script=tools/mpv-audit.lua --term-status-msg='' video.mp4
```

The tool prints `M3_PLAYBACK_RESULT` at end of playback. Review raw mpv output
before sharing: mpv itself can print the media path even though this tool does not.

Protected content, AV1, HEVC, VP9 and sustained 1080p60 playback remain untested here.
Camera and browser capture results are documented separately in [capture.md](capture.md).


## Chromium hardware decoding investigation (2026-10-16)

Chromium 153.0.8010.36-1 still uses **software decoding** for the generated
8-second H.264 baseline 720p30 clip. Normal Omarchy configuration explicitly
disables `AcceleratedVideoDecoder`; its packaged documentation describes green
frames with the Apple VA-API path. We kept that configuration unchanged.

The [exact Arch Linux ARM build recipe](https://github.com/archlinuxarm/PKGBUILDs/blob/3d45100a45e945ac14f0fbb0c6e67c5540f9e6c9/extra/chromium/PKGBUILD)
sets `use_vaapi=false` and `use_v4l2_codec=true`. Enabling VA-API feature names
therefore does not establish a working VA-API decoder in this binary.

An isolated Wayland/ANGLE GL profile explicitly enabling
`AcceleratedVideoDecoder,AcceleratedVideoDecodeLinuxGL,PreferV4L2VideoAcceleration`
reaches the native stateless V4L2 backend (`S264`). Its initial H.264 SPS
`VIDIOC_S_EXT_CTRLS` fails with `EINVAL`; capture-format setup fails and Chromium
falls back to `FFmpegVideoDecoder`, with `kIsPlatformVideoDecoder=false`.
Disabling zero-copy GL does not resolve this. GPU status saying video decode is
“enabled” is insufficient evidence of hardware decoding.

A source-level compatibility hypothesis is that Chromium's
[`SetExtCtrlsInit()`](https://chromium.googlesource.com/chromium/src/+/153.0.8010.36/media/gpu/v4l2/v4l2_video_decoder.cc)
submits an initial SPS with zero flags, while the pinned kernel's
[`avd_h264_validate_sps()`](https://github.com/omacom/linux-aurora/blob/5ec1028c81526e1ed31db2b97e47edf8663e83cb/drivers/media/platform/apple/avd/avd-h264.c)
rejects SPS without `V4L2_H264_SPS_FLAG_FRAME_MBS_ONLY`. This is not yet a
runtime-confirmed diagnosis. A temporary process-local preload probe intended
to amend only the placeholder SPS still produced the same failure; interception
was not verified. No kernel validation was relaxed and no fix is qualified.

Normal software playback decoded all 240 frames with zero drops. Forced V4L2
runs also fell back to software; their colour samples matched the normal browser
baseline. This does not validate hardware colour output. Selected observations:
[browser decode report](../reports/2026-10-16-browser-decode.json).
