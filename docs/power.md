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
