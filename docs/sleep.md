# Initial suspend/resume — J613, 2026-10-16

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

This single short cycle does not qualify lid/keyboard wake, repeated or overnight
sleep, battery drain, external displays, or every peripheral. Normal shutdown
and next-boot brightness restoration remain a separate test.

See [selected observations](../reports/2026-10-16-suspend.json).
