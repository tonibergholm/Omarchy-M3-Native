# Initial suspend/resume — J613, 2026-10-16

## Power-button wake

One short, attended **s2idle** cycle passed on the [tested Aurora stack](tested-stack.md)
with the local [J613 brightness-test UKI](display.md). No external display was
attached. The normal Omarchy sleep-lock inhibitor and packaged fprintd sleep
hooks were retained; no suspend-related setting was changed for this test.

The kernel logged suspend entry and exit, about six seconds apart. Its suspend
success counter increased from 0 to 1, failure stayed 0, and the boot identity
was unchanged. The operator confirmed **power-button wake** and **Touch ID unlock**.
The post-wake fingerprint PAM session logged successful authentication.

The 2560×1664/60 Hz SDR display returned with brightness 265; keyboard backlight
stayed 77. OpenGL red/blue pixel readback and Vulkan compute readback passed
after wake. These are requested brightness values, not measured luminance.

Speaker protection stayed active and logged its suspend detection and PCM
reinitialization. A one-second quiet tone was not heard. A six-second repeat
through `audio_effect.j613-convolver`, with the sink at 35%, was audible and
confirmed by the operator. No audio restart or configuration change was made.
A playback process exiting successfully alone was not counted as audible sound.

This single power-button cycle does not qualify repeated or overnight sleep,
battery drain, external displays, or every peripheral. A separate subsequent normal reboot also restored both brightness values;
see the [display results](display.md).

See [selected observations](../reports/2026-10-16-suspend.json).

## Lid-close sleep and lid-open wake

After the normal reboot, a separate attended lid test passed on the same stack.
Logind recorded lid closed, the kernel entered s2idle, then lid opened and the
kernel exited s2idle approximately 35 seconds later. Suspend success increased
0 → 1 and failure remained 0 within this boot. The operator confirmed that
opening the lid alone woke the display and Touch ID unlocked it, with no
power-button press. The lock PAM log also recorded successful authentication.

Screen brightness remained 265 and keyboard backlight 77. The native
2560×1664/60 Hz SDR display returned; OpenGL and Vulkan readback checks passed.
Speaker protection stayed active, and the operator heard a six-second quiet
tone clearly through the protected convolver path at 35% sink volume.

See the [lid-test report](../reports/2026-10-16-lid-suspend.json). This adds one
short lid cycle, not repeated-cycle or overnight qualification. Keyboard wake,
external-display sleep and battery drain remain untested.

## Longer unplugged lid sleep

A later unplugged lid cycle spent about 17½ minutes in s2idle. Opening the lid
alone woke the display; Touch ID unlocked and the protected tone was clear,
all confirmed by the operator. Brightness stayed 265/77, OpenGL and Vulkan
readback passed, and suspend success increased with no failure. This extends
recovery evidence beyond the short tests, but does not qualify overnight or
many-cycle reliability. [Battery-counter results](power.md) were inconclusive;
no sleep-power claim follows from the successful resume.


## Repeat unplugged lid cycle after fixed-brightness baseline

The first cycle in a new recorded series spent **121.170 seconds** suspended.
Kernel suspend success increased 1→2; failures remained zero. External power
was absent before and after. Screen brightness restored to 265 and keyboard
lighting to 77. OpenGL and Vulkan readbacks passed; the camera delivered 30
1080p NV12 frames to a discard sink. Speaker protection remained active and the
DSP sink remained the default. The user confirmed Touch ID unlock, normal
display and clear audible tone.

Remaining charge increased 4161→4199 mAh near full, so sleep power remains
inconclusive. This is one additional successful cycle, not repeated-cycle or
overnight qualification. A temporary system-sleep recorder retains separate
pre/post observations for the next cycles without changing sleep policy.
See the [selected report](../reports/2026-10-16-power-cycle-1.json).


A second consecutive unplugged lid cycle spent **118.066 seconds** suspended.
Success increased 2→3 with failures still zero. The same OpenGL, Vulkan,
30-frame camera, brightness and protected-audio-path checks passed. The user
again confirmed Touch ID, display and clear sound. Charge increased
4162→4181 mAh, so this cycle also gives no credible sleep-power estimate.
These are two consecutive short-cycle passes; overnight and larger cycle-count
reliability remain unqualified. See the
[second-cycle report](../reports/2026-10-16-power-cycle-2.json).


The third consecutive unplugged lid cycle spent **515.823 seconds** suspended
(8 minutes 36 seconds). Success increased 3→4 and failures remained zero.
Brightness 265/77, OpenGL/Vulkan readbacks and 30-frame 1080p NV12 camera capture
passed again. Speaker protection stayed active. The user confirmed normal
Touch ID unlock, display and audible tone for the third time.

This completes three consecutive successful attended lid cycles in this series.
It does not qualify overnight sleep or large-cycle-count reliability. Charge
increased 4056→4080 mAh while reported capacity stayed 98%, leaving sleep draw
inconclusive. The temporary recorder remains installed for a longer test after
normal battery use. See the [third-cycle report](../reports/2026-10-16-power-cycle-3.json).


## Overnight resume (2026-10-17)

An unplugged **9 hour 19 minute** lid sleep resumed successfully: suspend success
4→5, failures zero, screen brightness 265 and keyboard lighting 77 restored.
OpenGL and Vulkan checks and 30-frame 1080p NV12 camera capture passed. The user
confirmed Touch ID unlock, normal display and clear protected audio. This is
one overnight recovery pass, not broad reliability qualification.

Battery fell 84%→57%, approximately 1.29 W by the charge-derived energy counter.
See [power observations and limits](power.md#overnight-unplugged-sleep-measurable-battery-loss)
and the [selected report](../reports/2026-10-17-overnight-sleep.json).

The temporary sleep-cycle recorder was removed after collecting the overnight
result. No sleep policy or device wake settings were changed.


## Built-in keyboard wake

An attended lid-open s2idle cycle on the same pinned J613 stack spent
**5.528 seconds** suspended. The operator confirmed that **Enter alone woke the
screen**, with no lid movement or power-button press, then Touch ID unlocked
the session. Suspend success increased 14→15 and failures stayed zero.
Brightness remained 265/77; OpenGL pixel and Vulkan compute readbacks passed.
Speaker protection stayed active; audible playback was not tested this cycle.

The MTP keyboard's input-device ancestor already had wakeup enabled; no wake
setting or sleep policy was changed. Its post-test wake counter was zero, and
no before/after counter delta was collected, so wake attribution rests on the
operator's observation rather than independent kernel-source identification.
The recorder's initial direct sysfs wakeup path was absent; subsequent ancestor
discovery confirmed the actual enabled setting. This is one short Enter-key
pass, not qualification of all keys, trackpad wake or repeated keyboard cycles.
The one-shot user timer finished; no persistent sleep hook was installed.
See the [selected report](../reports/2026-10-17-keyboard-wake.json).


## Built-in trackpad wake

The following lid-open s2idle cycle lasted **30.316 seconds**. In the instructed
trackpad-click test, the operator identified the trackpad as the wake action.
Suspend success increased 15→16, failures remained zero, brightness stayed
265/77, and both OpenGL and Vulkan readbacks passed. Speaker protection remained
active; audible playback and Touch ID were not separately confirmed this cycle.

The shared MTP input ancestor already had wakeup enabled. Its event, wakeup and
active counters were all zero before and after, while the SMC input counters
also remained unchanged. These counters therefore do not independently identify
the wake source. This is one operator-confirmed trackpad wake, not repeated-cycle
or closed-lid qualification. No wake policy was changed or persistent sleep hook
installed. See the [selected report](../reports/2026-10-17-trackpad-wake.json).


## Second overnight recovery (2026-10-18)

Following the macOS round trip and return to Linux, the journal records s2idle
entry at 21:58:47 on October 17 and exit at 08:37:48 on October 18, a
**10h39m01s journal interval**. This boot's success counter was one and failure
counter zero after wake. OpenGL and Vulkan readbacks passed; brightness was
265/77 and speaker protection was active. Audible playback was not tested.
The operator confirmed lid-open wake and Touch ID unlock both worked normally.

No dedicated recorder was armed at bedtime. The first inspection several
minutes after resume found **9% battery**, but no corresponding bedtime battery
sample exists and the UPower charge-history query returned no samples. This is
therefore a recovery result with **no quantified overnight battery-loss or
sleep-wattage claim**. See the
[selected report](../reports/2026-10-18-overnight-resume.json).


An unattended follow-up found no failed system or user units and connected
Wi-Fi. Bluetooth was powered and radios were unblocked, but the kernel recorded
an HCI `0x0c01` command timeout (`-110`) during the overnight resume. No paired
peripheral connection was tested, so powered status does not qualify Bluetooth
recovery or dismiss this error. No radio reset or service restart was performed.
EFI checksum reinspection was deferred because files require root and the user
requested checks without attendance. See the
[selected health report](../reports/2026-10-18-unattended-health.json).


### Bluetooth timeout source follow-up

The running controller's PCI ID is `14e4:5f72`, mapped by the pinned driver to
BCM4388. The timed-out opcode `0x0c01` is `HCI_OP_SET_EVENT_MASK`. The release
source's `bcm4377_resume_recovery_supported()` permits its resume-timeout reset
path only for BCM4378 on `apple,j493`; it therefore does not apply to this
J613/BCM4388. Current-boot logs show one Set Event Mask timeout, zero instances
of that recovery message, and ten boot-time codec-capability `-22` messages.
The controller remains powered and Wi-Fi connected. These state queries do not
prove live command transport or peripheral connectivity.

This identifies the scope of the existing recovery implementation, not the
cause of the J613 timeout or evidence that extending its gate is safe. No reset,
scan, connection, suspend, driver or firmware change was performed. The new
read-only `python3 tools/radio-status.py` prints selected controller state,
network states, rfkill values and timeout counts without addresses, names,
SSIDs or full journals. See the
[selected source/state report](../reports/2026-10-18-bluetooth-resume-source.json).


### Live transport check and default-off recovery candidate

An unprivileged raw-HCI **Read Local Version Information** (`0x1001`) command
was accepted by the kernel but produced no matching completion within three
seconds. A later eight-second receive-only window also saw none. An initial
filter-layout mistake was rejected before sending and is excluded. This is
stronger failure evidence than the powered cache flag, but does not identify
which transport stage failed.

With no connected devices or discovery active, a bounded normal BlueZ
power-off request was attempted with interactive authorization disabled. It
failed, and the adapter stayed powered. The reply said “Authentication Failed”;
the pinned kernel maps `-ETIMEDOUT` to `MGMT_STATUS_AUTH_FAILED`, and a `0x2039`
HCI timeout accompanied this attempt. That message is not treated as evidence
that a password or fingerprint was required. No successful power cycle, pairing
change, module reload or PCI reset occurred. Wi-Fi remained connected.

A [source candidate](../patches/j613-bt-resume-recovery-candidate.patch) adds
**default-off** `j613_resume_recovery` admission only for **J613 + BCM4388**, while
preserving the existing J493/BCM4378 gate. It reuses the release's recovery path;
that path is upstream work, not a new implementation here. Its module compiled
against the matching release configuration and symbols with the running kernel's
vermagic. All **32 host admission cases** passed across four chips, four board
identities and both option values. The packaged module hash remains unchanged.
The build used one worker, 10% CPU quota, thermal pause/resume and a 78°C stop
guard; maximum sampled temperature was 72.843°C.

**At this preparation stage the candidate had not been loaded or installed.** Compilation and admission
checks do not qualify hardware reset, calibration reload, callback races,
peripheral recovery or repeated suspend behavior. A recoverable native test is
still required before any deployment decision. The patch retains the Asahi
source's GPL-2.0-only OR MIT licence and attribution; no firmware, calibration
or module binary is published. See the
[selected report](../reports/2026-10-18-bluetooth-recovery-candidate.json).


### Temporary native Bluetooth test, 18 October

With the operator present, charger attached, no connected Bluetooth devices and
a macOS DFU recovery machine available, the matching candidate was loaded from
a private root-owned staging directory with `j613_resume_recovery=1`. The packaged
module and boot configuration were left unchanged; a 30-minute automatic rollback
was armed. The previously unresponsive controller then answered `0x1001` with
status zero in about 1 ms. A fresh module load restored command transport; this
is separate from validating the candidate's resume-timeout recovery.

A lid-close cycle recorded approximately **69.87 seconds suspended**, with
suspend success increasing from one to two and failure remaining zero. After
resume, the controller again answered in about 1 ms and Wi-Fi was connected.
No additional Set Event Mask timeout or recovery attempt appeared. Thus this
short cycle passed, but **the recovery callback was not exercised**. Peripheral
connections, calibration reload after recovery, repeated and overnight recovery
remain unqualified.

The original packaged driver was subsequently reloaded, the experimental
parameter disappeared, a fresh HCI read succeeded, and the rollback timer was
stopped. Nothing was installed persistently. The passive sleep observer also
recorded its first real matched pre/resume pair. See the
[selected native report](../reports/2026-10-18-bluetooth-native-short-cycle.json).
