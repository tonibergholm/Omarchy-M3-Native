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
