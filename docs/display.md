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

The complete selected result set was [reported upstream on Aurora #103](https://github.com/omacom/linux-aurora/issues/103#issuecomment-6266857792), including the corrected PM interpretation and measured short suspend.

A subsequent read-only `modetest -M apple -c` query exposed DPMS, EDID, TILE, link-status, non-desktop and vrr_capable properties, but no `HDR_OUTPUT_METADATA` or `Colorspace`. No native HDR output was qualified; this does not establish the monitor’s hardware HDR capability. PipeWire also exposed no display-audio output, so display audio playback remains untested. Raw EDID bytes and identifiers were not saved in the public report.

### 20 October refreshed candidate and longer 144 Hz checks

Unplugged boot followed by rear-port hotplug passed with both pictures correct and GPU readbacks passing. The package-managed thermal boot image was restored on disk and boot verification passed. See [boot and hotplug evidence](../reports/2026-10-20-dcpext-unplugged-boot-hotplug.json).

The first longer 144 Hz attempt disconnected after 25.35 seconds with the cable untouched; its cause remains unresolved. Replug left the Hyprland output disabled, and explicitly setting `disabled=false` at 60 Hz restored the picture. A later retry remained visually clear and stable for **200.77 seconds**, confirmed by the operator, before the unchanged 75 °C test guard returned it to 60 Hz. The peak was the `macsmc_soc_die` aggregate at 77.750 °C; individual CPU zones peaked at 54.416 °C and battery at 29.100 °C during the named observation. The aggregate is the maximum of thirteen configured SMC channels; its peak source and calibration remain unqualified. A separate 15.33-second guard stop lacked sensor identity. This is not a five-minute stability pass and does not erase the earlier disconnect. See [selected retest evidence](../reports/2026-10-20-arzopa-144hz-retests.json).

A [rebuilt preflight candidate](../reports/2026-10-20-dcpext-ordered-thermal-preflight.json) now preserves the corrected thermal-package sensor order (`20261020-2`). Baseline and candidate each contain 115 DTBs with both J613-compatible variants passing the order-sensitive verifier, and their DTB/U-Boot/config tails are identical. The actual restore helper passes candidate, already-restored and foreign-image fixtures with systemctl mocked. At that preflight, staging and native boot tests had not run. The older display results do not qualify it.

The corrected-order candidate was subsequently [staged and independently read back](../reports/2026-10-20-dcpext-ordered-thermal-staged.json). Verified baseline backups and EFI kernel images are preserved; a new 90-second next-boot rollback restores baseline `2f4037b0…`. Native boot/hotplug results follow below.

The corrected-order candidate then [booted natively on .20](../reports/2026-10-20-dcpext-ordered-thermal-native.json) with ARZOPA unplugged. Firmware-ready/DCPEXT, all six exact sensor mappings, both-cluster bindings and 58/95/110 °C trips passed; brightness remained 265/77. Automatic restoration produced the verified package baseline and Omarchy update verification passed. Rear-port hotplug produced correct 1080p60 pictures on both screens, confirmed by the operator, with GPU readbacks passing before and after.

A subsequent planned three-cycle mode test reached 144 Hz for ten seconds and returned to 60 Hz. At 14.995 seconds, during the 60 Hz dwell, the unchanged guard stopped the trial on `macsmc_soc_die` 77.015 °C. Both outputs remained active, final pictures were correct and GPU checks passed. Remaining cycles were cancelled; neither three-cycle nor five-minute qualification passed. The earlier unexplained dropout remains unresolved.

A subsequent [DPMS cycle](../reports/2026-10-20-dcpext-ordered-dpms.json) on this exact candidate held both outputs off in twelve samples across the requested three-second interval, then restored both at their original modes. The operator confirmed clear pictures on both screens; OpenGL/Vulkan readbacks passed and the independent fallback timer stopped. This is display power recovery, not system suspend qualification.

One subsequent [normal attached-display s2idle cycle](../reports/2026-10-20-dcpext-ordered-attached-sleep.json) passed on the rear port with lid open: suspend success 0→1, failures unchanged at zero, approximately 20.657 seconds clock-suspended. The owner confirmed both pictures correct and Touch ID unlock. GPU readbacks passed; brightness stayed 265/77, all six CPU-zone trips and both-cluster bindings remained, and protection stayed active with NRestarts=1. No guard was bypassed. This adds one short cycle on the corrected-order candidate, not longer/repeated sleep or battery-drain qualification.

A following [five-minute passive 60 Hz observation](../reports/2026-10-20-dcpext-ordered-passive-60hz.json) completed in 300.404 seconds. All 60 five-second samples retained both outputs enabled/on at 60 Hz and an external DRM connection. No mode/configuration changes or workload were requested. This establishes sampled desktop continuity for that interval, not continuous visual/refresh validation, events between samples or 144 Hz reliability.

## ARZOPA advertised audio/HDR versus Linux interfaces

A [read-only capability/source audit](../reports/2026-10-20-arzopa-audio-hdr-capability-audit.json), cross-checked with `edid-decode`, found valid CTA advertisement of stereo LPCM (32/44.1/48 kHz, 16/20/24-bit), front-left/right speakers, PQ/ST2084, static metadata type 1 and BT.2020 RGB/YCC. This is advertised input capability, not measured HDR quality, luminance, bit depth or audible playback.

The running kernel has `CONFIG_DRM_APPLE_AUDIO=y`, but `appledrm.hdmi_audio=N`, no booted `apple,dpaudio` nodes, no display ALSA card/ELD, and no `HDR_OUTPUT_METADATA` or `Colorspace` connector properties. Pinned .20 `avep_init()` accepts only firmware 12.3/13.5 and rejects other profiles, including 14.7. The audio-card path also needs a DCP endpoint and tx DMA provider. A parameter change alone cannot supply these missing interfaces. No switch, firmware call, DT graph or HDR mode was changed.

### Newer AV source and a compile-checked prerequisite

A [comparison with pinned 7.2 source](../reports/2026-10-20-display-audio-template-backport-preflight.json) found that its AV initializer additionally admits `DCP_FIRMWARE_V_14_7_TEMPLATE` using the existing 13.5 command table. The .20 T8122 external processor selects that template profile. The corresponding one-case [backport prerequisite](../patches/aurora20-template-audio-gate-prerequisite.patch) compiled with a matching .20 SDK for both reference and candidate (`W=1`, ARM64 objects, no warnings). Nothing was linked, installed or loaded.

This refines the port plan: profile admission code already exists upstream, but a complete M3 audio path does not. The pinned newer T8122 DT still has no display-audio/SIO provider nodes. T8112 display audio uses **SIO**, rather than MCA ADMAC; its channel numbers must not be copied to T8122 without machine-specific evidence. The first compile had an isolated-header omission; another hit the unchanged 75 °C guard. The final build restricted the compiler process to an efficiency core and passed below 58 °C, without changing clock limits. These are build results, not firmware/audio qualification.

The SIO prerequisite also spans the bootloader. In pinned [m1n1 `d05ba17`](https://github.com/AsahiLinux/m1n1/blob/d05ba17dfb771871d608225be42968bbb1e75a18/src/kboot.c), `dt_setup_sio()` only visits existing `sio`/`sio1` FDT aliases, reserves the matching ASC firmware, builds ADT-derived firmware-data mappings and parameters, then enables the node. Its [data builder](https://github.com/AsahiLinux/m1n1/blob/d05ba17dfb771871d608225be42968bbb1e75a18/src/sio.c) requires `asio-ascwrap-tunables`, `map-range`, `dmashim` and `device-type` properties. The [.20 Linux SIO driver](https://github.com/omacom/linux-aurora/blob/c46d7dcdb8712ea9aeb0ce47b439ffae76371e55/drivers/dma/apple-sio.c) consumes `apple,sio-firmware-params` and errors if that property is missing. These source paths identify an additional handoff requirement; they do not establish T8122 compatibility. A Linux-only audio-node overlay cannot replace the missing firmware-data preparation. No ADT blobs, firmware contents or guessed mappings are included here.

### External SDR colour candidate: parser regression found offline

[Upstream PR157](https://github.com/omacom/linux-aurora/pull/157) proposes external SDR colour preferences and a 10-bit blend correction; it does not add HDR connector support. At pinned head `9d3aeb24`, extracted selection tests found that an invalid preferred-colour record can clear a valid RGB slot and advance its rank. In a synthetic three-record case, an invalid 7-bit sRGB entry makes the final slot fallback select BT.2020 instead of retaining valid BT.709. No such malformed record was observed on ARZOPA.

A [validate-before-commit fix](../patches/dcp-colorimetry-valid-replacement.patch) passes all nine host checks with ASan/UBSan; the unmodified PR fails seven. The checks use extracted source with pinned blob verification, not a full serialized parser or hardware execution. The [.20 backport's fixed parser object](../reports/2026-10-20-external-colorimetry-selection.json) compiles for ARM64. A broader reference build stopped at the unchanged 75 °C guard, so no complete module-build claim follows. Nothing was installed or loaded. The [reproducer](../tools/test-colorimetry-selection.py) requires the pinned .20 and PR source directories and writes generated files into a new output directory.
