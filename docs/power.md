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
