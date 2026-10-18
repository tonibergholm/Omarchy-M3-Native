# Battery observations — J613, 2026-10-16

A 120.14-second desktop sample on the [tested stack](tested-stack.md), with
the local brightness-test UKI, recorded 25 battery samples five seconds apart.
All samples reported Discharging with external power absent. Screen brightness
was 265 and keyboard brightness 77. This was an active Codex desktop session,
not a controlled idle benchmark; CPU temperature ranged 51.2–66.0°C.

Battery `power_now` was negative during discharge. Positive draw magnitudes:
median **6.77 W**, mean **6.74 W**, range **5.96–7.49 W**. Energy-counter loss
was 0.1824 Wh, equivalent to 5.47 W over the interval. The disagreement means
these short telemetry windows should not be treated as precise runtime
measurements. No battery-life estimate is claimed.

See the [selected baseline report](../reports/2026-10-16-battery-baseline.json).
## Longer lid sleep: recovery passed, power measurement inconclusive

A temporary systemd sleep hook captured battery counters just before and after
an unplugged lid-close/lid-open test. The hook interval was 1053.819 seconds;
subtracting its CLOCK_MONOTONIC interval gives **1052.224 seconds suspended**
(about 17½ minutes). Kernel suspend success increased by one, with no failure.
The temporary hook was removed after collection; no power policy was changed.

| Counter | Before | After |
| --- | ---: | ---: |
| Remaining charge | 4365 mAh | 4366 mAh |
| Derived remaining energy | 49.7610 Wh | 49.7724 Wh |
| Reported full energy | 50.0232 Wh | 50.3994 Wh |
| Reported percentage | 100% | 100% |

All external-power inputs were offline at both hook observations. The slight
increase in remaining charge and changing full-capacity estimate do not provide
a credible discharge measurement. **No sleep watts or battery-life extrapolation
is reported.** The immediate post-resume power reading is not a sleep average.

In the pinned [macsmc-power driver](https://github.com/omacom/linux-aurora/blob/5ec1028c81526e1ed31db2b97e47edf8663e83cb/drivers/power/supply/macsmc-power.c),
ENERGY_NOW is B0RM remaining charge multiplied by nominal pack voltage; it is not
an independent energy accumulator. Here a 1 mAh step corresponds to 0.0114 Wh.
Gauge settling or estimation could contribute, but this test does not isolate
the cause. A longer repeat after the battery has discharged further is needed.

Lid-open wake, Touch ID unlock, brightness 265/77, OpenGL/Vulkan readback and
clearly audible protected playback all passed. See the
[selected longer-sleep report](../reports/2026-10-16-longer-sleep.json).


## Fixed-brightness desktop baseline

A second run allowed 60 seconds to settle, then sampled for 300.408 seconds
(61 readings). Screen brightness was fixed at 150/500 (30% of the control range,
not a measured luminance); keyboard lighting was off. AC remained absent and
all readings were Discharging. Background desktop applications remained open,
so this is a quiet desktop baseline, not a minimum-power laboratory result.

Reported discharge power averaged **4.98 W**, median **4.985 W**, range
**4.616–5.156 W**. CPU temperature ranged **49.281–51.484°C**. Remaining charge
fell 33 mAh; derived energy fell 0.3762 Wh, equivalent to **4.51 W** over the
window. Battery started near full, and the telemetry disagreement remains a
limit. No runtime extrapolation or causal improvement over the earlier active
session is claimed: workload and brightness both differed.

The original screen brightness 265 and keyboard brightness 77 were restored
automatically. No power policy changed. See the
[selected report](../reports/2026-10-16-settled-desktop-power.json).


## Overnight unplugged sleep: measurable battery loss

The overnight J613 run spent **33,557.628 seconds (9.322 hours)** suspended.
Recorded capacity fell **84%→57%**, charge **3462→2409 mAh**, and charge-derived
energy **39.4668→27.4626 Wh**. All external-power inputs were offline at both
observations. The 12.0042 Wh difference corresponds to approximately **1.29 W**
over the suspended interval. Unlike the near-full short tests, this run provides
clear evidence of substantial overnight battery loss.

This remains a single charge-gauge-derived estimate using nominal pack voltage,
not an independent energy measurement. Reported full energy also changed
49.8408→50.2398 Wh. Do not extrapolate exact sleep runtime from it.

Kernel suspend success increased 4→5 with failures zero. The log contains one
PM suspend entry/exit pair across the interval; this does not measure internal
s2idle wake activity. A Bluetooth opcode 0x0c01 timeout appeared at resume,
which does not establish the cause of the drain. The wake IRQ mapped to
apple-dockchannel-rx, which likewise is not a drain attribution.

Touch ID, display, protected audible sound, GPU readbacks and 30-frame camera
capture all passed after wake. See the
[overnight report](../reports/2026-10-17-overnight-sleep.json). A future controlled
comparison can isolate device contributions; no radio or wake-source policy was
changed in this run.


## Bluetooth sleep comparison

A subsequent Bluetooth-on baseline at lower charge spent **2323.019 seconds
(38 minutes 43 seconds)** suspended. Charge fell **2334→2298 mAh**, reported
capacity **56%→55%**, and derived energy **26.6076→26.1972 Wh**: approximately
**0.636 W** over the interval. Bluetooth was unblocked and powered on; no
connected Bluetooth devices were observed at setup/readback. Wi-Fi remained
enabled. AC was absent at both hook observations. Suspend success increased
5→6, failures stayed zero, and brightness restored to 265/77.

This shorter, lower-charge baseline is already below the overnight estimate.
Duration, gauge estimation and run-to-run variation prevent attributing that
difference to any device. The completed comparison below does not establish a
Bluetooth power saving. No camera capture or GPU stress checks were run between
conditions, to limit changes in device activity.
See the [baseline report](../reports/2026-10-17-bluetooth-on-sleep.json).


The Bluetooth-off repeat spent **2305.784 seconds (38 minutes 26 seconds)**
suspended. Charge fell **2189→2155 mAh**, derived energy fell **0.3876 Wh**, and
mean derived draw was **0.605 W**, versus **0.636 W** with Bluetooth on. Bluetooth
was soft-blocked at both off-condition hook observations, while Wi-Fi stayed
unblocked. AC remained absent. Suspend success increased 6→7, failures stayed
zero, and brightness restored to 265/77.

The **0.031 W difference** is too small to establish a useful Bluetooth effect
from one sequential pair with gauge variation and changing full-capacity
estimates. No automatic Bluetooth sleep policy was installed. Bluetooth was
restored to powered-on/unblocked afterward. These shorter runs also do not
explain why the overnight estimate was higher. See the
[comparison report](../reports/2026-10-17-bluetooth-sleep-comparison.json).


## Wi-Fi soft-block comparison

A one-shot system-sleep hook blocked only WLAN immediately before sleep and
unblocked it immediately afterward. Bluetooth remained unblocked. The run spent
**2710.920 seconds (45 minutes 11 seconds)** suspended. Charge fell
**1976→1926 mAh**, reported capacity **47%→46%**, and derived energy fell
**0.5700 Wh**: approximately **0.757 W**. AC was absent at both observations.
Suspend success increased 7→8 with failures still zero; brightness restored to
265/77. The hook confirmed Wi-Fi soft-blocked at both observations, then
unblocked it; NetworkManager subsequently reported wlan0 connected.

This did **not** improve on the earlier Wi-Fi-on/Bluetooth-on baseline of
0.636 W. One sequential comparison at different charge levels and durations
cannot establish that blocking Wi-Fi increases consumption, or exclude Wi-Fi
and PCIe contributions. Soft-blocking is not a whole-chip power-off test. PCIe
D0 readings before and after system suspend do not reveal its state during
sleep. No persistent Wi-Fi power-saving or wake setting was changed.

See the [selected comparison report](../reports/2026-10-17-wifi-sleep-comparison.json).
The ordinary NetworkManager Wi-Fi power-save setting remains off; the pinned
brcmfmac driver separately implements a system-suspend firmware D3 handshake.
Runtime control and system sleep are separate interfaces, as described in the
[kernel power-management documentation](https://docs.kernel.org/driver-api/pm/devices.html).


## Short suspend trace: AOP mailbox activity

A diagnostic-only lid cycle spent **64.802 seconds** suspended, with success
8→9 and failures zero. An isolated trace instance recorded suspend phases,
device PM callbacks, IRQ entries and IPIs. All **2229 device-callback completion
events** reported zero error; trace buffers reported no overruns or lost events.
The temporary hook and isolated instance were removed afterward. No radio,
wake-source, CPU idle or device power policy changed.

Between `machine_suspend` begin/end markers, IRQ counts were: **236 AOP mailbox**,
**66 architectural timer**, **13 SMC mailbox**, and **259 IPI IRQ entries**.
The live device-tree phandle links mailbox `2f4408000` (IRQ 57) to the AOP at
`2f4c00000`; mailbox `2ec408000` (IRQ 55) links to the SMC. These are counts over
the marker window, including its entry/exit boundary activity, not proof of a
particular service's power cost.

Each CPU recorded 250–263 suspend `CPU PD` entries and no suspend WFI entries.
The [pinned CPUIdle core](https://github.com/omacom/linux-aurora/blob/5ec1028c81526e1ed31db2b97e47edf8663e83cb/drivers/cpuidle/cpuidle.c)
accounts suspend-to-idle separately from ordinary idle. These invocations do not
independently verify physical core or cluster power gating. Suspend counter time
and trace timestamps barely advanced across 64.8 seconds of wall-clock sleep;
neither is interpreted as an absolute residency percentage.

The pinned [ambient-light driver](https://github.com/omacom/linux-aurora/blob/5ec1028c81526e1ed31db2b97e47edf8663e83cb/drivers/iio/common/aop_sensors/aop_als.rs)
enables a **200000 µs reporting interval**, with no suspend callback in that
file. This is a concrete candidate for recurring AOP traffic, but the mailbox is
shared with other AOP services. IRQ tracing alone does not identify endpoints,
and no causal battery-drain claim follows. Next: identify endpoint traffic and
validate report quiescing/restoration before testing any energy benefit.

See the [selected diagnostic report](../reports/2026-10-17-suspend-diagnostic.json).
Raw trace, interrupt snapshots and device-tree data remain private.


## AOP endpoint attribution and reversible ALS control

A second diagnostic sleep lasted **62.984 seconds**, success 9→10, failures zero.
Temporary argument-free probes on the ALS and LAS report handlers, plus an
RTKit receive probe filtered to AOP IRQ 57, recorded **164 ambient-light reports**
and **63 lid-angle reports** between `machine_suspend` markers. Endpoint
**0x27** delivered 164 messages; **0x26** delivered 63. An eight-second awake
control gave 40 ALS/0x27 and eight LAS/0x26 reports. No trace events were lost.
This establishes sensor processing during sleep, without attributing battery
cost. Probes, their isolated instance and the diagnostic hook were then removed.
See the [sensor report](../reports/2026-10-17-aop-sensor-suspend.json).

The installed headers omit the Rust build artifacts needed to rebuild this
module directly. A private, temporary **instruction-checked module copy** was
therefore used only to validate control of ALS reporting. Four checked AArch64
instructions in the two probe branches change the single source constant
`ALS_INTERVAL_US` from 200000 to zero. No relocation targets those instructions;
no packaged module, firmware or calibration was modified. Original upstream
code remains the Asahi contributors' dual GPL-2.0-only/MIT sensor driver.
This is a diagnostic binary experiment, not a source-built PM fix or an installer.

An awake original/stopped/restored sequence measured **48 / 8 / 48 AOP mailbox
interrupts** in three eight-second windows: approximately **6 / 1 / 6 per second**.
The ALS device remained present but returned ENODATA while reporting was stopped;
normal light readings returned after reloading the original module. The lid-angle
device stayed present. Packaged module SHA-256 remained unchanged. An earlier
collector treated expected ENODATA as an error; its `finally` path also restored
the original successfully before the corrected repeat.
See the [control report](../reports/2026-10-17-als-interval-control.json).

A J613-only one-shot sleep test is now prepared to substitute the interval-zero
copy before sleep and reload the preserved original after wake. This leaves LAS,
Wi-Fi, Bluetooth, audio drivers and speaker protection alone. No sleep power
saving or production-ready suspend fix has yet been established.


## ALS quiesced sleep: recovery and reduced interrupt traffic

The one-shot J613 experiment spent **788.295 seconds (13 minutes 8 seconds)**
suspended. It loaded the private interval-zero ALS module before sleep and
reloaded the preserved original after wake. ALS readings returned ENODATA at
both measurement boundaries and became readable again after restoration. The
lid-angle device remained bound throughout. The packaged module stayed unchanged.

AOP IRQ 57 increased by **790** across the hook observations, approximately
**1.002 interrupts per suspended second**. That window includes entry/exit
activity, and no endpoint trace was active in this run. The result is consistent
with the previously identified ~1 Hz lid-angle stream remaining while ALS
reports are quiesced. It does not directly attribute every remaining interrupt.
CPU suspend `CPU PD` entries increased by 793–1564 per CPU; entry counts are not
physical residency measurements.

Suspend success increased 10→11, failures stayed zero, brightness restored to
265/77, and OpenGL/Vulkan checks and Wi-Fi recovery passed. Speaker protection
remained active. The user confirmed opening the lid woke the display, Touch ID
unlocked and the protected tone was clear. No audio or lid-sensor driver was
modified. See the [sleep report](../reports/2026-10-17-als-quiesced-sleep.json).

This validates reversible report quiescing and recovery, **not an energy saving**:
battery counters were not recorded in this run. A maintainable implementation
needs source-built ALS suspend/resume callbacks and a matched energy comparison.
The temporary module substitution is not installed as a permanent sleep policy.

The one-shot ALS sleep hook was removed after collection. Normal ALS reporting
is restored; private observations and module copies are retained for research.


A [source-built ALS PM candidate](als-pm.md) is compiled, awake-load checked
and passed one native suspend/resume cycle. It replaces the diagnostic
instruction edit with source callbacks; no battery benefit is claimed. The
packaged original is restored and the one-shot observer is removed.


## Passive boundary observer (2026-10-18)

The second overnight sleep had no bedtime sample. A temporary **user-level**
observer now subscribes to logind's typed `PrepareForSleep` signals, without
triggering, delaying or inhibiting sleep. It records selected battery fields,
external-power state, brightness, suspend counters and monotonic/boottime clocks.
Resume schedules target samples at +30/+60/+120 seconds and records their actual
elapsed time; a new sleep cancels unfinished delayed samples. No media capture,
network identifiers, full journal or private firmware data is recorded.

The transient `m3-passive-sleep.service` is running with a seven-day runtime
limit, 5% CPU quota and 128 MiB memory limit. It does not start after reboot.
The local JSONL file is mode 0600 inside a private 0700 research directory;
exclusive creation prevents an existing recording from being overwritten.
Stop it with `systemctl --user stop m3-passive-sleep.service`.

Three offline tests passed for two-cycle clock/pairing behavior, unmatched
resume handling and preservation of existing/symlink output. The startup record
and live service are verified, but **native sleep/resume signal delivery and
post-wake sampling remain pending the next natural cycle**. No sleep was
triggered for qualification. Logind notifications surround the sleep workflow;
they are not exact kernel boundary measurements. Activation establishes neither
a battery-use estimate nor a saving. See the
[selected activation report](../reports/2026-10-18-passive-sleep-observer.json).

`python3 tools/sleep-observer.py` defaults to one read-only snapshot on stdout.
Explicit `--watch --output /private/new-file.jsonl` enables recording and requires
an existing output directory and a new file. It needs Python GObject/Gio bindings.
Run offline checks with `python3 -m unittest discover -s tests`.
