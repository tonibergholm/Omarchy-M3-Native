# Tested stack — 2026-10-16

| Component | Version / setting |
| --- | --- |
| Machine | MacBook Air 13-inch M3, 2024, `apple,j613`, `apple,t8122` |
| Distribution | Arch Linux ARM |
| Omarchy | `omarchy-dev 4.0.0.r7026.g51bfd1d-1`, `omarchy-mac 0.1.4-1` |
| Aurora release | `aurora-2026.10.15.19` |
| Kernel | `7.1.12-2-20261015.19-sep-ARCH` |
| Kernel/headers packages | `7.1.12.aurora2-20261015.19` |
| Release kernel source | `5ec1028c81526e1ed31db2b97e47edf8663e83cb` |
| Boot chain | Existing stage1 → m1n1 stage2 → U-Boot → Limine → UKI |
| Existing stage1 | Reports `v1.6.1-dirty`; retained, source provenance not established here |
| m1n1 package | `m1n1-aurora 1.6.1.aurora17-5` |
| Stage2 | Reports `v1.6.1-omarchy.aurora17` |
| OS firmware label | `14.7` |
| System firmware | `27.0` |
| GPU firmware compatibility | `14.8.3`, identified by the GPU driver |
| Experimental Mesa | `mesa-m3 26.1.4.m3.2-5`, active under `/opt/mesa-m3` |
| libfprint / fprintd | `1.94.100-1.1` / `1.94.5-2` |
| Touch ID integration | `aurora-touchid 20261003-2` |

These firmware fields are different facts. The OS firmware label does not prove
which GPU firmware ABI is active. Do not choose a 26.6.2 GPU profile solely from
the system firmware version.

Published packages were used for the initial bring-up. A later separate UKI
contains the local [J613 backlight patch](display.md); a further test UKI now
also embeds the [ISP14.7 camera candidate](capture.md), now reboot-tested
with 1080p30 camera capture and GPU readback passing.
Packaged modules and the normal Omarchy UKI are retained. First the read-only
SEP stack was installed, then SEP provisioning was enabled and tested. GPU
activation came afterwards, followed by the explicit thermal sensor list.

Observed CPU policy maxima are 4056 MHz and 2748 MHz, with schedutil and
apple-cpufreq. These are configured limits, not measured sustained clocks.

See [the structured result](../reports/2026-10-16-j613.json). Linux reboots after enrollment passed. Later [short power-button and lid-wake
suspend tests](sleep.md) also passed Touch ID unlock. macOS coexistence remains
untested.

The existing Touch ID report was published as a comment on
[Aurora issue #79](https://github.com/omacom/linux-aurora/issues/79#issuecomment-6216574514).
