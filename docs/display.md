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
prevent this swap-based control path. One short [s2idle/power-button wake cycle](sleep.md) preserved brightness.
A subsequent normal reboot restored screen brightness 265 and keyboard
backlight 77 exactly. The systemd-backlight load succeeded, and the firmware
logged 17367040 in 16.16 units (= 265). OpenGL and Vulkan readbacks passed
again. See the [reboot report](../reports/2026-10-16-brightness-reboot.json).
A separate 35-second lid-close/lid-open cycle also preserved brightness, with
Touch ID, GPU checks and audible protected sound passing. Repeated/long sleep
remains untested. The active test UKI is separate from the packaged
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

## Upstream report

The J613 patch and test evidence were [posted to Aurora issue 32](https://github.com/omacom/linux-aurora/issues/32#issuecomment-6217879992)
on 2026-10-16. This is a submitted hardware report and source candidate, not an
upstream merge or packaged release.

## ARZOPA Z1FC external display, 19 October

On Aurora .20, the packaged m1n1 left dcpext disabled because its firmware was not reserved. Direct rear-port USB-C detected a power-delivery partner but exposed no external connector. A [local m1n1 reservation candidate](../patches/j613-dcpext-reservation-local.patch), based on the approach reported in [Aurora #103](https://github.com/omacom/linux-aurora/issues/103), passed reference/candidate builds and seven helper controls. It admits J613/T8122 on 14.7 only after the internal handoff marker, reserves firmware and leaves dcpext disabled for the kernel gate. The exact existing DTB/U-Boot/config payload tail, including retained thermal controls, was preserved.

A cold-plug test boot enabled dcpext and its routes; PMP request `0x21800` was acknowledged as `0x218f0`. The internal panel and ARZOPA Z1FC at **1920×1080/60 Hz** both looked correct to the operator, with OpenGL red/blue and Vulkan compute readbacks passing. A 20-second runtime **1080p144** test also looked clear and stable, then returned to 60 Hz automatically. No display configuration file was edited. This establishes short mode operation, not physical refresh calibration or sustained reliability.

The original thermal-enabled stage2 was restored on disk by the 90-second next-boot rollback, without changing the running trial session. Root and ESP backups were verified. Stage1, firmware/calibration contents and package-owned binaries were unchanged. A subsequent reboot uses the original bootloader unless the candidate is staged again. Longer external-display sleep and sustained 144 Hz remain unqualified. See [selected native evidence](../reports/2026-10-19-arzopa-z1fc-dcpext.json).

The rear-port unplug/replug and a move to the front (trackpad-side) port both restored a clear 1080p60 picture. The front maps to sysfs `port2` / DRM `DP-2` here (an initial watcher assumed `port1`; direct inspection corrected that harness mapping). GPU readbacks passed after each transition. A three-second DPMS off/on cycle changed both reported DPMS states false→true and both pictures returned correctly; GPU checks passed afterward. Legacy dispatcher syntax was rejected before any blanking, then corrected to the installed typed Lua API.

**Short attached-display suspend passed:** a normal s2idle request with the Z1FC on the front port increased success 0→1 with failures remaining zero. Journal realtime minus monotonic deltas estimate **10.040 seconds asleep** (14.591 seconds entry-to-exit wall time, 4.552 seconds monotonic). Both pictures returned correctly, Touch ID unlocked, and OpenGL/Vulkan checks passed. Longer/repeated sleep and daily-use qualification remain open.

Correction to the earlier source-only prediction: the T6030 PM guard does not apply here. Probe sets `external` only for `apple,t6030-dcpext`; J613 uses `apple,t8122-dcpext` and `ext_failsafe`, so it never enters that guard. No kernel guard was removed or bypassed. Rebooting uses the restored original stage2 unless the candidate is staged again.
