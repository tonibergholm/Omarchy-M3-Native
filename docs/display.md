# Brightness and HDR — J613, 2026-10-16

## Current observations

On the [tested stack](tested-stack.md), `/sys/class/backlight` is empty.
The keyboard LED is separate and works. The internal panel runs at 2560×1664,
60 Hz, XRGB8888, with Hyprland's sRGB preset. DRM exposes only XRGB8888 and
ARGB8888 scanout formats, with no HDR_OUTPUT_METADATA or Colorspace property.
The selected [14.x atomic-check code](https://github.com/omacom/linux-aurora/blob/5ec1028c81526e1ed31db2b97e47edf8663e83cb/drivers/gpu/drm/apple/iomfb_v14_7.c)
explicitly rejects other pixel formats.

The device tree's panel `apple,max-brightness` is 525. Apple's
[13-inch M3 Air specifications](https://support.apple.com/en-ca/118551) rate
the Liquid Retina IPS display at 500 nits. It is not the MacBook Pro's XDR
panel. Video-format support, wide P3 colour and native HDR output are separate
properties; none establishes that this Linux display path supports HDR.

## Brightness candidate: built and staged, not yet runtime tested

Aurora [issue 32](https://github.com/omacom/linux-aurora/issues/32) tracks this
missing backlight. [aronvandepol's J516S report and patch](https://github.com/omacom/linux-aurora/issues/32#issuecomment-6113974721)
identified 14.x swap brightness fields: update byte `0x354`, with an IEEE754
double in nits at `0x35c`. That report tested an M3 Pro, not this M3 Air.

The [local source adaptation](../patches/j613-v14-backlight-candidate.patch)
adds an opt-in `appledrm.j613_backlight=1` for the existing J613 board record.
The driver's existing exact firmware-image admission is retained. Other Air
boards are not admitted by this new option. The candidate caps the backlight
at min(device-tree maximum, 500), and initially reports 140 nits until a
brightness request is made. The reported initial value is not a measurement
of the boot firmware's current level.

The module compiled against this boot's exact Aurora headers and symbols.
The local compiler is clang 23.1.1; the distributed kernel was built with
clang 22.1.8. Modpost reported two init-to-exit section references in unchanged
DCP unregister/error-cleanup code. A successful build is not runtime acceptance.

A separate UKI was built and its embedded module hash verified. The packaged
module file and ordinary module lookup were restored after packaging. The
existing Omarchy UKI and GPU-off fallback were retained. No live driver reload
was attempted. The test entry is **M3 brightness experiment**, selected first
with an eight-second boot menu; **Omarchy → linux-aurora** uses the existing
working image. Root-only recovery/config backups are kept locally.

Next checks after boot: backlight registration, moderate brightness steps with
visible confirmation, bounds rejection, driver error counters, brightness-key
and OSD integration, DPMS restoration, then separate reboot and suspend tests.
Do not call the candidate working until those observations are recorded.

## HDR outcome

Native HDR is blocked by the current kernel display interface. Enabling an HDR
compositor preset or forcing a 10-bit format does not establish valid output;
no HDR preset was enabled. An external HDR display is also untested on this Mac.

HDR-to-SDR tone mapping in a video player is a useful separate test, still
pending. Existing H.264 [video tests](video.md) used SDR patterns and establish
nothing about HDR decoding, colour correctness or tone mapping.
