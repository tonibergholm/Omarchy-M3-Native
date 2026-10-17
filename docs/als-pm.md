# J613 ALS suspend/resume source candidate

Status on 2026-10-17: source-built, awake-load checked and one native
suspend/resume cycle passed. Battery benefit remains unproven. This is a local research candidate for
the exact [tested stack](tested-stack.md), not an installer or upstream support.

The [sensor trace](../reports/2026-10-17-aop-sensor-suspend.json) established that
ambient-light and lid-angle reports continue during sleep. The earlier temporary
interval-zero module experiment showed reversible ALS quiescing. This candidate
moves the interval changes into actual driver suspend/resume callbacks.

Two source patches apply to Aurora commit
`5ec1028c81526e1ed31db2b97e47edf8663e83cb`:

- [Rust platform PM callbacks](../patches/rust-platform-system-pm-candidate.patch)
  add typed ordinary system suspend/resume methods. Existing drivers default to
  `HAS_PM=false`; the generic adapter registers PM operations only when enabled.
- [J613 ALS candidate](../patches/j613-als-system-pm-candidate.patch) retains the
  AOP/service references and changes the report interval to zero at suspend and
  back to 200000 µs at resume. A failed suspend operation attempts to restore
  reporting before returning an error. Firmware error status is treated as EIO.

The behavior requires both `j613_suspend_quiesce=1` and an `apple,j613` root
compatible. The integer parameter defaults to zero. The pinned Rust parameter
macro exposes integer parameters with `perm=0`, so there is no sysfs parameter
file; the loader verified the opt-in using a probe-time kernel message.
Runtime PM, noirq and hibernation operations are outside this candidate's scope.
Lid-angle and audio drivers are unchanged.

## Build and compatibility checks

The release source archive matched SHA-256
`6cc841d18a55beb163faabb52e5a84d9fcf7bd8d6618c879ac88ac0d918cd630`.
The reconstructed configuration matches the installed kernel byte-for-byte.
The build used Rust 1.93.1, clang/LLVM 22.1.8 and bindgen 0.73.2, matching the
release recipe. Work ran in a private source/output tree with CPU quota and
thermal pause/resume guards. Packaged headers and kernel images were unchanged.

The headers package omits Rust artifacts. Reconstructing them also allowed the
local generic platform-adapter extension to compile into the module; no new
kernel image was installed. Both modules have the running kernel's vermagic.
All 47 reference-module and 52 candidate-module undefined symbols match the
installed export inventory, including the Rust crate symbol identities.

An unchanged source-built reference module loaded, exposed normal light readings
and preserved the lid-angle device; the packaged original was then restored.
The candidate subsequently loaded with its J613 opt-in confirmed. Light readings
work and awake AOP traffic was 12 interrupts over two seconds. The packaged ALS
module remains unchanged. See the [selected build/runtime report](../reports/2026-10-17-als-source-pm-build.json).

## First native PM result

The source-built candidate spent **364.836 seconds (6 minutes 5 seconds)**
suspended. Kernel success increased 11→12 and failures stayed zero. Its own
callbacks logged `J613 ALS reports paused for suspend` and
`J613 ALS reports restored after resume`. The observer recorded **370 AOP
interrupts**, approximately **1.014 per suspended second**, across the pre/post
hook window including entry/exit overhead.

Before any post-wake module reload, the native driver delivered normal readable
light data and AOP traffic returned to **12 interrupts over two seconds**.
Brightness 265/77, OpenGL/Vulkan readbacks, Wi-Fi and speaker protection passed.
The user confirmed lid-open wake, Touch ID unlock and clear protected audio.
The observer then restored the packaged original, and the temporary hook was
removed. See the [native sleep report](../reports/2026-10-17-als-source-pm-sleep.json).

Charge increased 1227→1268 mAh while reported capacity stayed 29%, leaving energy
use inconclusive. This is one native-cycle pass; repeated-cycle reliability and
error/rollback paths remain unqualified. A longer matched battery comparison is
required before claiming an energy benefit. The candidate is not installed as
the default module or in a boot image. Source patches preserve the Rust platform
code's GPL-2.0-only license and the Asahi sensor driver's GPL-2.0-only OR MIT license.


## Longer energy comparison: packaged baseline

The new packaged-driver baseline lasted **13,118.196 seconds (3h38m38s)**, rather
than the initially planned hour. Charge fell **1088→686 mAh**, reported capacity
**26%→16%**, and immediate derived energy fell **4.5828 Wh**, approximately
**1.258 W** over the suspended interval. AOP IRQ count increased by 47,491,
approximately **3.620 per suspended second** across the hook window. Success
increased 12→13 and failures remained zero. AC stayed absent, Wi-Fi/Bluetooth
remained unblocked, and brightness restored to 265/77.

The new delayed sampler completed at 30, 60 and 120 seconds after wake. Charge
readings were **632, 623 and 612 mAh** respectively. The first 30 seconds account
for a **54 mAh** decrease and a full-energy estimate change from 50.2284 to
49.6698 Wh. This is much larger movement than the sampled awake power readings
alone would suggest. Later full-energy readings settled near 49.6356 Wh.
Delayed charge loss includes both awake use and gauge settling; it is not
reported as sleep-only consumption, nor used as a fixed correction offset.

The candidate comparison is pending recharge and must match the observed
baseline duration as closely as practical. No ALS energy-saving claim follows
from this baseline. See the [selected observations](../reports/2026-10-17-als-energy-baseline.json).
