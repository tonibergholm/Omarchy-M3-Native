# Brightness and HDR — J613, 2026-10-16

## Current observations

The unmodified [tested stack](tested-stack.md) exposes no screen backlight.
After booting the local test UKI, `apple-panel-bl` is registered with max 500.
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

## Brightness candidate: initial J613 runtime checks passed

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

After the test boot:

- `appledrm.j613_backlight=1` is active; `apple-panel-bl` has max 500.
- Requests 100 → 300 → 150 were read back exactly; the starting 265 was restored.
- The operator confirmed visible brightness changes, brightness keys and OSD.
- Writing 501 failed with EINVAL and left the level unchanged.
- The driver reported `failed 0`, requested/sent 265, and no pending request.
- DPMS off/on changed the compositor status and preserved reported brightness 265.
- OpenGL red/blue and Vulkan compute readback still passed.

These are requested nits, not photometer measurements. Firmware startup logs
contained 16.16 values consistent with requests (for example 9175040 = 140).
The early missing-Backlight-service firmware message still appears; it does not
prevent this swap-based control path. Full suspend/resume and persistence across
another reboot remain untested. The active test UKI is separate from the packaged
driver, so a normal kernel update does not incorporate this local patch.

Selected observations are in the [backlight report](../reports/2026-10-16-backlight.json).

## HDR outcome

Native HDR is blocked by the current kernel display interface. Enabling an HDR
compositor preset or forcing a 10-bit format does not establish valid output;
no HDR preset was enabled. An external HDR display is also untested on this Mac.

A six-second generated neutral PQ ramp (640×360, 24 fps, H.264 High10)
was software decoded in mpv 0.41.0 with gpu-next/OpenGL and BT.2390 tone mapping.
Input properties confirmed 10-bit BT.2020/PQ; `video-target-params` reported
BT.709/gamma2.2 and nominal 203-nit SDR reference white. That nominal renderer
value is not a panel luminance measurement. Playback reached EOF with two
presentation drops. Visual confirmation is pending; this establishes execution
of the conversion path, not calibrated colour correctness. This was not an
HEVC Main10 hardware-decode test.

The local optional preset can be selected with:

```sh
mpv --profile=m3-hdr-to-sdr video.mp4
```

Its settings are `vo=gpu-next`, `gpu-api=opengl`,
`target-colorspace-hint=no`, `target-trc=srgb`, `target-prim=bt.709`,
`tone-mapping=bt.2390`, `hdr-compute-peak=no`. These are described in the
[mpv manual](https://mpv.io/manual/stable/). Ordinary playback defaults are
unchanged. See the [selected conversion report](../reports/2026-10-16-pq-to-sdr.json).

The earlier H.264 [video tests](video.md) used SDR patterns; their hardware
decoder result does not qualify HDR decoding or sustained tone-mapping speed.
