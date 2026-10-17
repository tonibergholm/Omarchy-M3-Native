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
