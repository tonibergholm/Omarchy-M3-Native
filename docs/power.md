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
A longer lid-sleep measurement is prepared with a temporary pre/post systemd
sleep hook that reads battery counters without changing power policy. Its
results are pending; the hook will be removed after collection.
