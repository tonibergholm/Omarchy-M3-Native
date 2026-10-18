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

Protected content remains untested here. Short VP9/AV1 correctness results,
a short HEVC Main
correctness test and bounded three-minute 1080p60 tests are recorded below.
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


## Display-synchronized playback comparison

On the same J613 kernel and fixed 618 MHz GPU ceiling, a command-line
`--video-sync=display-resample` repeat used the same 180-second H.264 clip,
fast profile and 960×540 requested window. All 180 periodic samples reported
VA-API and active display synchronization; the timeline was continuous to EOF.
mpv reported **zero presentation drops, zero decoder drops, zero mistimed frames
and seven delayed frames**, versus 24 presentation drops and zero delayed frames
in the previous default-sync run. The thermal guard completed normally with a
66.734°C maximum and 53.812°C final sample. This is one sequential comparison;
changing synchronization also changes scheduling and counter behavior. Zero
drops does not establish perfect cadence or isolate the original root cause.

The first display-sync attempt looked smooth and correct to the operator, but
its sampled timeline jumped from 76.8 to 140.033 seconds and its delayed counter
reset. The operator explicitly reported no seeking. The cause is unexplained;
that attempt is excluded as uninterrupted three-minute evidence. The repeat
above disabled player keyboard/mouse bindings and the on-screen controller;
this precaution does not establish input as the cause of the earlier jump.

The command-line option is available for further experiments:

```sh
mpv --profile=m3-fast --video-sync=display-resample video.mp4
```

No normal player configuration changed. Both runs had **no audio**, so audio
resampling and A/V synchronization remain unqualified; this result is not a
recommendation to change ordinary playback defaults. Fullscreen, browsers, HDR,
other media and long-session reliability also remain unqualified. The audit
now records requested sync mode, active display-sync state and reported/estimated
display refresh rates. See the
[selected comparison](../reports/2026-10-17-video-display-sync.json).


## Unattended decoder correctness extension (2026-10-18)

Headless tests on the same pinned J613 stack used forced VA-API output and
hardware download into NV12 for frame checksums, compared against software
H.264/HEVC decoding converted to the same pixel format. Hardware logs identified
Apple AVD. All output frame rows (ordering, timestamps and pixel checksums)
matched exactly in these cases:

| Generated clip | Frames matched |
| --- | ---: |
| H.264 High, 1280×720/30, 3 seconds, B-frames and CABAC | 90/90 |
| H.264 High, 1920×1080/30, 2 seconds, B-frames | 60/60 |
| HEVC Main, 1280×720/30, 2 seconds, B-frames | 60/60 |

The 720p H.264 header's `entropy_coding_mode_flag=1` was checked explicitly.
This adds short **HEVC Main decoding correctness** evidence, not HEVC playback
or every HEVC profile. All clips were progressive 8-bit 4:2:0 generated patterns.
VA-API advertised H.264, HEVC Main/Main10, VP9 and AV1 profiles, but advertised
profiles alone do not qualify the untested codecs or 10-bit path.

Each process had a 90-second timeout and a 78°C die-temperature stop guard.
Encoders used one thread, with x265 worker pools disabled. All stages completed;
the largest sampled temperature was 77.703°C, so further encoding tests were
deferred. Half-second polling cannot exclude peaks between samples. No window,
audio, camera capture or operator action was required. GPU clocks and protection
settings were unchanged. See the
[selected report](../reports/2026-10-18-headless-decode.json).


## Small Main10 conformance check

The local x265 library reports an **8-bit build**. A requested Main10 generation
attempt silently produced Main/yuv420p instead; its subsequent P010 download
failure is excluded as Main10 evidence. The private generated-test harness now
checks actual profile and pixel format before attempting that comparison.

Instead, the [FFmpeg FATE conformance sample
DBLK_A_MAIN10_VIXS_3.bit](https://fate-suite.ffmpeg.org/hevc-conformance/DBLK_A_MAIN10_VIXS_3.bit)
was downloaded and probed as HEVC **Main 10, 176×144, yuv420p10le**. Forced VA-API
through Apple AVD and software decoding each produced **eight P010 frames**;
all frame rows and pixel checksums matched. P010 preserved 10-bit samples.
The reference's SHA-256 and selected results are in the
[Main10 report](../reports/2026-10-18-hevc-main10.json); the bitstream is not
redistributed here. The test used a 25% CPU quota and the existing 78°C guard,
with maximum sampled temperature 55.750°C. This tiny conformance case does not
qualify HD/UHD playback, HDR output, tone mapping, audio or arbitrary Main10.


## Unattended VP9/AV1 checks and a film-grain failure

On the same J613 kernel with `libva-v4l2_request-avd
1.3.r11.r169.gc653eaa-1`, the following forced VA-API/Apple AVD outputs matched
software decoding exactly (frame order, timestamps and pixel checksums):

| Clip | Comparison format | Frames matched |
| --- | --- | ---: |
| Generated VP9 Profile 0, 1280×720, 8-bit | NV12 | 30/30 |
| [FATE AV1 frames_refs_short_signaling.ivf](https://fate-suite.ffmpeg.org/av1/frames_refs_short_signaling.ivf), 640×360, 8-bit | NV12 | 50/50 |
| [Chromium bear-av1-320x180-10bit.webm](https://chromium.googlesource.com/chromium/src/+/refs/tags/120.0.6099.129/media/test/data/bear-av1-320x180-10bit.webm), 320×180, 10-bit | P010 | 82/82 |

The Chromium sample's sequence header has `film_grain_params_present=0`.
These are short correctness checks, not sustained playback qualification.

**Failing case:** the [FATE film_grain.ivf sample](https://fate-suite.ffmpeg.org/av1/film_grain.ivf)
is AV1 Main 10-bit, 320×240, with grain parameters present and `apply_grain=1`.
The hardware path returned ten P010 frames and successful exit, but **every
output word was zero**: 0/10 frames matched software. Software output with grain
disabled also did not match hardware. Normal software output contained nonzero
image data both with and without grain, excluding a mere difference in grain
noise as the explanation for the zero output. The expected frame timing and
sizes matched. The initial harness rejected the sample's unexpected 10-bit
format before a separate P010 run; no 8-bit truncation was used.

This isolates a failing grain-bearing sample while a different grain-free
10-bit sample passed; it does not prove whether the defect is in grain handling,
surface selection, the VA bridge or the kernel. The pinned kernel AV1 source
reads the film-grain control but further source/runtime work is needed before
assigning a root cause. The installed library was not patched or replaced.
For this affected sample, explicit software decoding (`mpv --hwdec=no ...`)
avoids relying on the failed hardware result; audible/visual playback was not
tested in this unattended run. Ordinary player defaults remain unchanged.

All jobs used a 25% CPU quota, finite deadlines and the 78°C guard. GPU pixel and
compute readbacks passed afterwards. Provenance, reference hashes and selected
results are in the [report](../reports/2026-10-18-vp9-av1.json); reference media,
raw output and the pinned library checkout remain private. No upstream issue
or comment was posted.


### AV1 grain/display-surface trace

A process-local VA-API observation probe reproduced the exact uninstrumented
failure. For all ten pictures, FFmpeg supplied `apply_grain=1` and a grain-display
surface different from the current decode surface. The client synchronized and
read display surfaces with successful VA status, yet received the zero output.
The installed VA AV1 header defines that display surface as the grain-applied
picture. The pinned bridge source (`c653eaa`) never uses
`current_display_picture`; it retains the decode/current surface and begin-picture
target instead. The pinned kernel reads a grain-control pointer, with no further
uses of that pointer found. These are evidence of an incomplete grain/display
path; they do not constitute a completed root-cause fix.

A separate **diagnostic-only** preload redirected display-surface sync/download
to the associated decode surfaces. This recovered exact software-without-grain
pixels for **6/10 frames**, while four still differed. All timing and frame sizes
matched. It neither synthesizes grain nor preserves all expected frames and
**must not be installed or described as a playback workaround**. Proper grain
synthesis, display-surface ownership and completion need to be addressed together;
explicit failure would also be preferable to silent blank output while that
support is unavailable. No source candidate was installed or upstream message
posted. See the [surface evidence](../reports/2026-10-18-av1-grain-surfaces.json).
