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

Protected content, AV1, HEVC and VP9 remain untested here. A later bounded
three-minute 1080p60 test is recorded below.
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

Two compatibility failures are now identified:

1. Chromium's [`SetExtCtrlsInit()`](https://chromium.googlesource.com/chromium/src/+/153.0.8010.36/media/gpu/v4l2/v4l2_video_decoder.cc)
   submits an initial SPS with zero flags. The pinned kernel's
   [`avd_h264_validate_sps()`](https://github.com/omacom/linux-aurora/blob/5ec1028c81526e1ed31db2b97e47edf8663e83cb/drivers/media/platform/apple/avd/avd-h264.c)
   rejects SPS without `V4L2_H264_SPS_FLAG_FRAME_MBS_ONLY`.
   A verified process-local preload probe adds that flag only to the placeholder
   SPS: the control succeeds, NV12 is selected, and seven capture buffers are
   requested. This confirms the initial mismatch. The earlier probe missed the
   call because the signed ioctl request was compared against an unsigned-long
   constant; matching its low 32 bits fixed interception.
2. Chromium's [`SubmitDecode()`](https://chromium.googlesource.com/chromium/src/+/153.0.8010.36/media/gpu/v4l2/v4l2_video_decoder_delegate_h264.cc)
   then submits `V4L2_STATELESS_H264_DECODE_MODE_FRAME_BASED`. The pinned
   [driver control configuration](https://github.com/omacom/linux-aurora/blob/5ec1028c81526e1ed31db2b97e47edf8663e83cb/drivers/media/platform/apple/avd/avd-v4l2.c)
   accepts only `V4L2_STATELESS_H264_DECODE_MODE_SLICE_BASED` and start-code mode
   `NONE`. The request fails with `ERANGE` (34), followed by software fallback.
   Changing the mode integer alone would not implement the required slice
   controls and compressed-data handling, so that was not attempted.

The temporary probe retained Chromium's sandbox and changed no installed
browser configuration, kernel or firmware. No hardware-decoding fix is qualified.
A compatible slice-based browser backend or a properly implemented and tested
frame-based driver path is needed to progress beyond these boundaries.

Normal software playback decoded all 240 frames with zero drops. Forced V4L2
runs also fell back to software; their colour samples matched the normal browser
baseline. This does not validate hardware colour output. Selected observations:
[browser decode report](../reports/2026-10-16-browser-decode.json).


## Three-minute 1080p60 extension (2026-10-17)

A generated H.264 1920×1080/60 clip containing **10,800 frames over 180 seconds**
played to EOF with the optional fast profile, requested 960×540 window geometry,
`gpu-next` and VA-API. The decoder log identified Apple AVD and hardware decoding;
mpv still reported `vaapi` at EOF. No audio was played. The operator reported
“Looks smooth and correct”. The GPU ceiling remained 618 MHz.

mpv reported **25 presentation drops** (about 0.23% of the clip's frame count),
**zero decoder drops**, zero mistimed frames and zero delayed frames. We did not
collect per-second drop timing, so cannot attribute drops to startup or a
particular section. This extends the earlier eight-second result; it is not a
zero-drop pass, and different geometry and desktop activity prevent a controlled
comparison with those short runs.

A one-second die-temperature sampler guarded playback at 78°C and a 240-second
timeout. It completed normally with 180 samples, maximum **75.140°C** and final
**54.828°C**. No clock, thermal policy or ordinary player configuration changed.
The pattern repeats four seconds of generated content; this does not qualify
arbitrary H.264 streams, fullscreen rendering, browsers, HDR, other codecs,
audio synchronization or long-session reliability. See the
[selected report](../reports/2026-10-17-video-180s.json).


## Presentation-drop timing repeat

A second 180-second run reused the exact clip, fast profile and requested
960×540 window, with one-second audit logging added. All 180 periodic samples
reported VA-API. It reached EOF with **24 presentation drops** (about 0.22% of
10,800 frames), **zero decoder drops**, zero mistimed and zero delayed frames.
The first increase was observed near 10.93 seconds, with 11 cumulative drops by
30.93 seconds and another 13 distributed through the remainder, including near
179.93 seconds. **Startup alone therefore does not explain this run's drops.**
The largest sampled increase was six drops near 25.93 seconds. Sampling marks
when cumulative changes became visible, not exact dropped-frame timestamps.

The thermal guard completed normally: 180 samples, maximum 70.453°C, final
55.312°C. The cap remained 618 MHz. The similar final drop totals (25 then 24)
are observations from two sequential runs, not a controlled rendering benchmark:
cache/shader history, audit overhead and other desktop activity differ. These
results do not isolate rendering cost, compositor timing or scheduling as the
cause. No persistent playback setting was changed. See the
[selected timing report](../reports/2026-10-17-video-drop-timing.json).

The audit tool's default end-of-file behavior is unchanged. To additionally log
selected counters every second:

```sh
mpv --profile=m3-fast --script=tools/mpv-audit.lua \
  --script-opts=m3-audit-interval=1 --term-status-msg='' video.mp4
```

The optional interval accepts 1–60 seconds; zero disables periodic output.
