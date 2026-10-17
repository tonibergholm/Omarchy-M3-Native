# Omarchy M3 Native

Findings and local tuning from running Omarchy on a **13-inch MacBook Air M3
(2024), J613 / T8122**. Tested on one machine on **2026-10-16–17**.

This is a research and setup log, not an installer or a new driver distribution.
It uses the published Aurora Linux stack. It is independent of Omarchy, Aurora,
Asahi Linux and Apple; their work and support policies remain their own.

## What works on the test machine

| Feature | Observed result | Limits |
| --- | --- | --- |
| Speakers | Clear protected playback after restarting the audio stack | Protected playback passed after reboot and sleep; headphones and acoustic calibration unqualified |
| Keyboard illumination | Brightness control and persistence across reboot | Super+F5/F6 added as local shortcuts |
| Touch ID | Enrollment, matching, an unenrolled-finger rejection, sudo and lock-screen unlock | Reboot, repeated sleep and one macOS round trip passed; enrollment changes unqualified |
| GPU | OpenGL pixel readback and Vulkan compute readback passed | Experimental legacy/current14 profile; capped at performance state 2, 618 MHz |
| Native panel | eDP-1, 2560×1664, running Hyprland | Local brightness test passed visible changes, keys/OSD and DPMS checks; scanout remains SDR/8-bit |
| Die temperatures | 13 channels exposed; GPU reads `macsmc_soc_die` | Sensor selection is a local experiment, not a qualified policy for higher clocks |
| Microphone/camera | Clear microphone capture; local ISP14.7 candidate delivers 1080p30 camera frames | Grain in dark room; reboot, post-sleep capture and local browser tests passed |
| Video | H.264 hardware-decoded frames matched software; 1080p30 playback had no drops | Short 1080p60 fast-profile test had no drops; default 60 fps playback dropped frames |
| CPU frequency and idle | `apple-cpufreq`, schedutil, WFI and CPU PD present | Observed counters and configured frequency limits, not battery-life or sustained-performance qualification |

## Start here

- [Exact stack and test record](docs/tested-stack.md)
- [Touch ID setup and evidence](docs/touch-id.md)
- [GPU setup and recovery](docs/graphics.md)
- [Brightness and HDR investigation](docs/display.md)
- [Suspend/resume results](docs/sleep.md)
- [Battery observations](docs/power.md)
- [Temperature sensing](docs/thermal.md)
- [ALS suspend/resume candidate and energy comparison](docs/als-pm.md)
- [Video decoding and playback](docs/video.md)
- [Microphone and camera tests](docs/capture.md)
- [Local WebRTC call test](docs/webrtc.md)
- [Audio and keyboard illumination](docs/audio-keyboard.md)
- [What carries over from the M4 project](docs/m4-comparison.md)
- [Remaining work](docs/roadmap.md)

Read-only checks:

```sh
python3 tools/m3-status.py
python3 tools/thermal-watch.py --seconds 10
aurora-m3-gpu-check
```

The tools print selected platform facts, not raw device trees or full journals.
Review output before sharing. There are no automatic boot, partition, PAM or
clock changes in this repository.

The tested machine still has macOS installed. Keep working boot entries and a
recovery route before experimenting. SEP/xART writes affect shared security
state; a saved disk image does not guarantee rollback of SEP anti-replay state.

## Credits

The kernel, SEP driver, graphics implementation and firmware handoff are upstream
work, not implementations from this repository:

- [Asahi Linux](https://asahilinux.org/), Linux, m1n1 and Mesa contributors.
- [Aurora Linux / Omacom](https://github.com/omacom/linux-aurora), including its
  published kernel, matched Mesa and Touch ID stack.
- [Omarchy Mac](https://github.com/omacom/omarchy-mac), Omarchy, PipeWire,
  WirePlumber, ALSA and speakersafetyd contributors.
- [Scott Jones's J613 Touch ID work](https://github.com/omacom/linux-aurora/issues/79).
- [Kb2uka/Omarchy-M4-Native](https://github.com/Kb2uka/Omarchy-M4-Native), a useful
  reference for documenting per-board experiments and sensor validation.
- [iSMC](https://github.com/dkorunic/iSMC) for sensor-key reference information.

Toni Bergholm performed the physical tests with Codex assistance. The original
scripts and documentation here are MIT licensed. No Apple firmware, calibration,
keybags, biometric material or upstream driver sources are redistributed.
