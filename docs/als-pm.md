# J613 ALS suspend/resume source candidate

Status on 2026-10-17: source-built and awake-load checked. Native suspend/resume
and battery benefit are still pending. This is a local research candidate for
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

## First native PM test

A temporary one-shot observer is armed. It records counters before sleep and
following native driver resume, checks awake mailbox activity briefly, then
reloads the preserved packaged original. It does not perform the suspend-time
interval change: that belongs to the source-built driver's PM callback.

The next attended lid cycle must check successful suspend, callback logs,
interrupt activity, restored light reporting and normal lid-open/Touch ID/audio
recovery. A longer matched battery comparison is still required before claiming
an energy benefit. The candidate is not installed as the default module or in
a boot image. Source patches preserve the Rust platform code's GPL-2.0-only
license and the Asahi sensor driver's GPL-2.0-only OR MIT license.
