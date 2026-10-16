# Experimental M3 GPU

The tested release is
[aurora-2026.10.15.19](https://github.com/omacom/linux-aurora/releases/tag/aurora-2026.10.15.19).
Its inspected installer was run with `--m3-gpu`. It selected the legacy/current14
profile after checking the machine's firmware and bootloader. This is not the
separate native25/26.6.2 profile.

The matched `mesa-m3` package installs under `/opt/mesa-m3`; it does not replace
every system Mesa library. Its UWSM environment hook selects the prefix at login.
The desktop account needed membership in `render` and a fresh login.

## Verification after reboot

```text
PASS Apple GPU OpenGL (red/blue readback).
PASS Apple GPU Vulkan (compute readback).
```

The session state reported `decision=active`, `/opt/mesa-m3`, the T8122 render
node and native display. Hyprland's mapped libraries included the prefix's EGL,
GBM and Gallium. The native panel was eDP-1 at 2560×1664.

Run `aurora-m3-gpu-check` in the actual desktop session. Merely installing Mesa,
seeing a panel, or finding a render node is not the same test. These readbacks
also do not establish conformance, every application's stability or sustained
performance.

The tested ceiling is performance state 2, **618 MHz**. The thermal experiment
keeps `asahi.t8122_pstate_cap=2` explicit. No higher GPU clocks are qualified.

## Recovery

The installer retained **Aurora previous (GPU off)** in Limine, with
`asahi.t8122_start=0 mesa_m3=off`. Use that entry if GPU boot or desktop login
fails. Retain copies of the known-working stage2 and boot files before changes;
recovering a failure before Limine requires restoring stage2 from macOS/Recovery.

The current14 panel has no Linux backlight device. This is tracked separately
in [Aurora #32](https://github.com/omacom/linux-aurora/issues/32).
