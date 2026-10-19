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

The candidate comparison is recorded below. No ALS energy-saving claim follows
from this baseline. See the [selected observations](../reports/2026-10-17-als-energy-baseline.json).


## Longer candidate comparison

On the same J613 and pinned kernel, the opted-in source PM candidate completed
**14,714.913 seconds (4h05m15s)** suspended. Both native callbacks logged success;
suspend success increased 13→14 and failures stayed zero. AOP IRQ count increased
by 14,755, approximately **1.003 per suspended second**, versus the packaged
baseline's 3.620. After wake, traffic returned to about six interrupts per second
before the packaged original was restored automatically after the 120-second
sample. Light readings worked after restoration.

Charge fell **2973→2548 mAh**, reported capacity **70%→61%**. Immediate derived
energy loss was **4.845 Wh**, approximately **1.185 W**, versus the baseline's
1.258 W. This roughly 0.072 W difference does **not** establish an energy benefit:
this is one sequential pair, durations differ, starting state of charge differs
(70% versus 26%), and energy is derived from charge at nominal voltage rather
than measured independently. The candidate's delayed charge readings were
**2475, 2462 and 2427 mAh** at 30, 60 and 120 seconds. The first 30-second drop of
73 mAh and changing full-energy estimate again show substantial gauge movement.
Delayed readings include awake use and are not a corrected sleep-energy result.

AC was absent and radio block states and brightness matched the baseline at
both endpoints. The temporary observation hook and sampler unit have been removed. The packaged
driver remains the default and no boot image was changed. This
second native cycle supports the PM behavior, but repeated-cycle reliability,
error paths and energy savings remain unqualified. See the
[selected comparison](../reports/2026-10-17-als-energy-comparison.json).


## Aurora .20 rebuild and awake-load checks, 19 October

The .20 release at `c46d7dcdb8712ea9aeb0ce47b439ffae76371e55` has unchanged
ALS and platform-adapter source. Both PM patches apply cleanly. A matching
isolated SDK retained the packaged configuration byte-for-byte. Reference and
candidate modules built without warnings/errors, with exact .20 vermagic and
all 47/52 required symbols found in the release export inventory.

Both modules passed separate temporary awake-load tests: light readings worked,
the lid-angle sensor remained present, and the candidate opt-in diagnostic was
observed. Each test restored the original; the packaged module file was unchanged.
The candidate subsequently passed one 135.784-second native .20 lid cycle:
both callbacks logged success, readings resumed before restoration, and Touch ID,
GPU rendering and brightness restoration passed. AOP interrupt count increased
152 across the hook window, including entry/exit activity. Charge increased in
this short test, so it provides no usable power-saving estimate. The original
module was restored automatically. Repeated-cycle/error-path qualification
remains open. See the [.20 sleep evidence](../reports/2026-10-19-aurora20-als-pm-sleep.json)
and [.20 build evidence](../reports/2026-10-19-aurora20-als-pm-preflight.json).
