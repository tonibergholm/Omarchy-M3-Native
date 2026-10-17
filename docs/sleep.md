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
