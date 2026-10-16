# Microphone and camera — J613, 2026-10-16

Tested on the [same Aurora stack](tested-stack.md), after the longer sleep test.
Recordings stayed in a private local directory; no speech or camera frames are
included in this repository.

## Microphone: clear capture confirmed

The default `omarchy_asahi_mic` source was already installed and unmuted. It
maps Asahi's mono DSP microphone to a desktop-compatible stereo source. A
15-second, 48 kHz, stereo sample was recorded and played through the protected
speaker sink; the operator confirmed clear voice. No audio configuration or
gain change was needed. An initial shorter mono test was not heard as voice;
that observation alone did not establish a hardware fault. Browser conferencing
and microphone behavior after another reboot remain separate tests.

## Camera: stock 14.7 path stalled

`/dev/video1` is the IMX558 FaceTime camera, separate from `/dev/video0` (AVD).
The device tree reports ISP firmware/compatibility **14.7.0**. It advertises
1920×1080 NV12 at 30 fps, among other modes. On the packaged driver, buffer setup
and STREAMON succeeded but no frame dequeued before a 12-second timeout. The
process required the timeout's kill fallback. Stop/return/suspend firmware
commands timed out and the driver force-stopped the ISP.

This matches the no-frame stage discussed in
[Aurora issue 117](https://github.com/omacom/linux-aurora/issues/117).
[Scott Jones's 26.6.2 work](https://github.com/omacom/linux-aurora/issues/117#issuecomment-6159609193)
and [PR119](https://github.com/omacom/linux-aurora/pull/119) identified the
MBNR/temporal/motion stages as a blocker there and suggested checking the same
skip on 14.7. Their firmware-version/setfile changes are not applied here.

## Local J613/14.7 test: frames delivered

The [GPL-2.0-only source candidate](../patches/j613-isp14-no-temporal-candidate.patch)
adds `apple_isp.j613_no_temporal=1`, default off. It skips MBNR enable, temporal
filter start/enable and motion-history start only for `apple,j613` with ISP
compatibility 14.7. The firmware identity, boot loader, setfile selection and
calibration files are unchanged. This group test does not isolate which stage
is individually responsible or prove an ANE fault on 14.7.

The camera module was built against the exact installed headers/symbols with
clang 23.1.1 (release compiler: 22.1.8). Only the ISP module was unloaded/reloaded;
its dependencies were loaded before inserting the local candidate. The
packaged module file remains unchanged.

Two separate discard-only captures delivered **30 and 60 consecutive NV12
frames**, 3110400 bytes each, at approximately **30 fps** and 1920×1080. mpv live
previews then completed, including a 20-second repeat. The operator saw a live
picture but reported substantial grain/static in a dark room. Good-light image
quality and colour accuracy are not qualified. OpenGL and Vulkan checks still
passed after the camera tests.

Skipping temporal noise reduction may reduce image quality. An existing
`exposure_dynamic_framerate` control can allow auto exposure to reduce the rate
toward 15 fps instead of holding 30 fps and increasing gain. A brief additional
preview tested this control; visual improvement is unconfirmed, and its original
value 0 was restored. No low-light policy was made permanent.

Known limitations: the pre-existing firmware-stop warning remains; mpv reports
buffer-close/QBUF warnings during teardown. Camera-indicator behavior still
needs operator confirmation. Camera persistence across reboot, camera after
suspend, browser capture and sustained use remain untested. The camera workaround is now embedded alongside the tested brightness module
in the separate **M3 brightness experiment** UKI. Both embedded module hashes
were verified. Packaged modules and ordinary module lookup were restored after
packaging. The normal Omarchy and GPU-off boot entries were retained; a
root-only backup contains the earlier brightness-only test UKI and boot config.
The new camera-enabled UKI has not yet been reboot-tested.

See [selected capture results](../reports/2026-10-16-capture.json).
