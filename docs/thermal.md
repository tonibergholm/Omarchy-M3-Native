# J613 temperature sensing

## Why the GPU could not read temperature

The SMC already returned die-related temperature keys, but the tested Aurora
`macsmc-hwmon` driver had no default J613 die-key list. Linux exposed only battery,
NAND, charging and Wi-Fi temperatures. The GPU expected `macsmc_soc_die` and
remained at its safe cap without it.

The existing driver accepts `macsmc_hwmon.soc_die_keys=` as a boot parameter.
No replacement kernel module was needed.

## Local configuration

```text
macsmc_hwmon.soc_die_keys=TCMz,Tg0C,Tg0D,Tg0O,Tg0P,Tg0W,Tg0X,Tg0a,Tg0b,Tg0i,Tg0j,Tg0u,Tg0v
asahi.t8122_pstate_cap=2
```

`TCMz` is the CPU maximum aggregate; `Tg*` is the GPU temperature-key family.
Raw key names are retained rather than asserting individual core locations.
Each selected key existed as a readable float on this Air. The maximum across
these 13 channels feeds `macsmc_soc_die`.

The parameters were appended to the existing explicit
`KERNEL_CMDLINE[linux-aurora]` in `/etc/default/limine`, preserving root/encryption
arguments and `asahi.t8122_start=1`. The defaults and boot menu were backed up,
`limine-update` rebuilt the UKI, and the GPU-off fallback was checked before
reboot. This repository does not automate that change on another machine.

## Observed after reboot

- All 13 channels registered and appeared in `sensors`.
- The GPU logged a temperature from `macsmc_soc_die` instead of “no SoC die
  temperature zone”. Its ceiling stayed at 618 MHz.
- Startup CPU temperature briefly reached about 85°C during existing browser
  activity. Extra load was deferred until the machine settled.
- A bounded, single-process, five-second CPU workload started near 59°C.
  CPU readings rose to about 70°C during the pulse, briefly about 72°C afterwards,
  then returned toward 60–62°C. GPU-family maximum rose from about 47°C to 55°C.
- The validation sampler had a 78°C stop guard and guaranteed workload cleanup.
- OpenGL pixel and Vulkan compute readbacks passed again afterwards.

SMC values updated in roughly one-second steps in this short sample; faster
polling did not produce independent readings each time. Other desktop activity
was present, so this is a response check, not a controlled calibration study.

## What this does not prove

This tripless reporting zone is consumed by the GPU's existing temperature
limiter. It does **not** add CPU frequency cooling bindings or independently
establish CPU thermal protection. Higher GPU clocks, sensor failure handling,
shutdown thresholds and sustained-load safety remain unqualified.

A follow-up read-only check found no `/sys/class/thermal/cooling_device*`
devices and no `#cooling-cells` on the CPU device-tree nodes. The kernel has
CPU frequency thermal support and the cpufreq driver advertises cooling-device
support, but no Linux CPU cooling binding was exposed on this boot. This does
not establish what protection firmware provides. No CPU policy was changed.

The speaker amplifier `temp1` channels reported `FAULT` while speakers were
idle. They are not the SMC die zone; protected speaker playback was not bypassed.

References: the exact release's
[hwmon driver](https://github.com/omacom/linux-aurora/blob/5ec1028c81526e1ed31db2b97e47edf8663e83cb/drivers/hwmon/macsmc-hwmon.c),
[GPU thermal policy](https://github.com/omacom/linux-aurora/blob/5ec1028c81526e1ed31db2b97e47edf8663e83cb/drivers/gpu/drm/asahi/m3_thermal.rs),
[iSMC sensor map](https://github.com/dkorunic/iSMC/blob/master/smc/sensors.go), and
[M4 sensor research](https://github.com/Kb2uka/Omarchy-M4-Native/blob/develop/docs/j713-cpu-temperature.md).

## Follow-up: updates and policy failure behavior

On the same pinned kernel, 65 read-only samples over 64.31 seconds found all
13 die channels readable and changing, with 51–64 changes per channel. The
aggregate zone ranged from 50.187 to 63.906°C during ordinary desktop and
research activity; no deliberate stress load was applied. This demonstrates
updates, not calibrated accuracy or independent hardware freshness timestamps.
Sequential channel and zone reads are not simultaneous.

Ten host tests against the unchanged release's `m3_thermal_policy.rs` passed:
three existing board/required-zone tests and seven local checks for missing,
failed, stale, implausible and stuck readings, critical-temperature fallback
with its grace period, and a fixed state-2 ceiling. The hwmon aggregate's source
returns an error if any selected die sensor fails or is out of its accepted
range. These are source and host-policy checks, not injected hardware faults.

Live kernel summaries still show safe state 2 and ceiling 2, both 618 MHz, with
no cap raises or lowers. Consequently the thermal fallback cannot reduce the
current GPU cap below state 2; it must not be described as a GPU shutdown or a
qualified whole-machine thermal policy. No Linux cooling devices or SMC thermal
pressure attribute were exposed. CPU firmware protection and sustained-load
safety remain unqualified. Clocks and protection settings were unchanged.
See the [selected report](../reports/2026-10-17-thermal-policy-check.json).

## PR146 one-boot native trial (19 October)

[Upstream PR146](https://github.com/omacom/linux-aurora/pull/146), head
`8fd1bf481afe6fcadaa04001b2bcd435616b705b`, supplied the J613 CPU thermal
device-tree changes for a one-boot trial on the same pinned kernel. All six
CPU sensors were readable on this firmware. Six `power_allocator` zones at
6 W, both cluster energy models, and both CPU cooling devices registered.
Manual conservative cooling requests lowered and restored both cluster QoS
ceilings. This supersedes the earlier absence of CPU cooling bindings only
for the running trial session.

A bounded temperature-emulation check demonstrated the automatic path without
heating the machine to the emulated temperature. At a simulated 108 C, a short
single-thread workload exceeded the allocator budget and the P-cluster ceiling
dropped from 4056 MHz to 3636/3288 MHz. Real TCMz stayed below 73 C. Simulation
and tracing were cleared, workers stopped, and the original ceiling recovered.
These are QoS limits and energy-model power estimates, not independent physical
frequency/power measurements or sustained real-temperature qualification.

The baseline stage2 image was reproduced byte for byte. The one-boot candidate
changed only the J613 DTB in its bundle. Its rollback service restored the
original boot image and disabled its timer; the candidate DT remains in memory
for the trial session. After successful checks, the owner explicitly chose to
retain the tested controls: the same candidate image was installed again and
hash-verified, with the original backup preserved and the rollback timer stopped
and disabled. Future kernel/boot package rebuilds may replace this local image;
retention is not a general update integration. The built-in hwmon driver and existing aggregate sensor
override were retained; the PR default-key C change is not installed.

See the [native report](../reports/2026-10-19-pr146-native-bindings.json) and
[preflight record](../reports/2026-10-19-pr146-preflight.json).


## Bounded lower-target native response on Aurora .20

A temporary test lowered only `cpu-e1-thermal` alert/control trips to 45/50 C,
retaining the 110 C critical trip, 6 W budget, PID parameters and GPU cap.
Native sensor inputs were used; no emulated temperature was written. During
a single-worker test, observed QoS limits reached 2808 MHz on the P cluster
and 2004 MHz on the E cluster, with maximum cooling states 11 and 3.
These were limits, not independently measured physical frequencies.

The independent 75 C guard stopped the run after 8.099 seconds when the hottest
reported zone reached 75.890 C; CPU sensor peak was 62.410 C. Original 58/95 C
trips and 4056/2748 MHz ceilings were restored, both cooling states returned to
zero, and the worker and rollback timer stopped. This demonstrates a short
native-input governor response under a changed target, not stable regulation.
The target did not settle; normal 95 C control, sustained loading and critical
shutdown behavior remain unqualified. See the
[selected report](../reports/2026-10-19-thermal-native-low-target.json).

## Package-managed retention and update verification, 20 October

An Omarchy update rejected the retained thermal stage2 because it differed from the image reconstructed from installed package inputs. Its SHA-256 exactly matched the known retained image; no unknown image change was found. The owner chose to retain thermal controls and integrate them with package-managed verification.

A local `omarchy-m3-thermal-local 20261020-1` package now owns an opt-in J613 thermal overlay. Applying it to the installed .19 base DTB reproduces the complete retained candidate semantically, resolving phandle references; the package-owned kernel DTBs remain unchanged. A local `omarchy-mac-boot 20261020-2.1` adapts overlay application and verification to an explicit list of installed package-owned DTBs, avoiding selection of the newer isolated .20 module tree. Explicit DTBS retain their old behavior unless the new option is selected. See the [source integration patch](../patches/explicit-dtb-overlay-integration.patch).

The boot-package suite passed 227 checks and integration passed 55 against its pinned Omarchy runtime. An initial integration run against latest runtime failed an unrelated factory-reset fixture; that run is not counted as passing. Native installation rebuilt m1n1 and initramfs through package hooks. Both the boot-chain check and Omarchy's actual update-verification entrypoint passed. The exact retained thermal DTB is in the on-disk bundle, package integrity checks pass, and experimental/fallback EFI images stayed byte-identical. No owner-managed boot-check exception was created and no reboot was triggered. This verifies on-disk integration, not a new native boot.

The thermal package pins the qualified .19 kernel and local boot package. Future kernel/boot-package upgrades need an updated integration and requalification; normal application updates remain available. Original EFI/configuration backups remain root-private. The bootloader reservation candidate for external displays remains a separate experiment. See the [selected repair report](../reports/2026-10-20-boot-update-thermal-integration.json).

The subsequent [native reboot](../reports/2026-10-20-thermal-package-reboot.json) loaded the isolated .20 entry with all six thermal zones, both cooling bindings, 6 W budgets and 58/95/110°C trips retained. Brightness restored to 265/77 and OpenGL/Vulkan readbacks passed. The known speaker startup panic recurred once, followed by recovery. DCPEXT remained disabled, consistent with the separate temporary display-bootloader trial. This does not qualify the default installed .19 entry or sustained regulation.

## 20 October display-test cutoff attribution

A guarded 144 Hz repeat logged all thirteen configured SMC channels and stopped after 101.79 seconds. At the stop, both `TCMz` and `macsmc_soc_die` read **77.281 °C**, following 55.546 °C in the previous one-second sample. GPU-family channels remained below 45 °C throughout this run. The final individual CPU-zone readings were below 50 °C. The external display remained connected at 144 Hz until automatic restoration to 60 Hz. This attributes this cutoff to TCMz; it does not prove a sensor fault, calibrate a hotspot, or retrospectively identify the earlier peaks. Reads are sequential, not atomic. No limits were changed. See [selected channel evidence](../reports/2026-10-20-smc-144hz-cutoff-source.json).

A subsequent passive 60 Hz comparison captured 120 samples over about 123 seconds, with both display modes remaining at 60 Hz. TCMz peaked at **77.046 °C** without an added test workload. These spikes therefore also occur outside 144 Hz operation; this does not establish their cause or accuracy.

## Local overlay sensor-order correction

The first package-managed overlay (`omarchy-m3-thermal-local 20261020-1`) reversed the six new hwmon temperature nodes: separate overlay fragments prepend new siblings. Thermal sensor indices therefore pointed to the reversed channel set. All six channels, common trips and both-cluster cooling bindings remained present, but zone names were incorrectly attributed. The earlier sorted semantic comparison missed this order-dependent ABI; it did not prove per-zone sensor identity. This affects observations after the first package integration, not the original correctly ordered compiled PR146 candidate, and does not explain TCMz spikes.

Local package `20261020-2` reverses insertion order, restoring indices 0–5 to `Te05`, `Te0P`, `Tp05`, `Tp0L`, `Tp0b`, `Tp0r`. Order-sensitive tests reject the old overlay and pass the original candidate plus corrected overlays on .19 and .20. The actual installed stage2 contains 115 DTBs; both J613-compatible variants have the corrected mapping. Boot-chain and Omarchy update verification pass; EFI kernel images are unchanged. **Runtime confirmation requires a reboot.** Thresholds and power budgets were not changed. See [selected correction evidence](../reports/2026-10-20-thermal-overlay-sensor-order.json).
