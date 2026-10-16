# Touch ID on J613

The successful path is Aurora's Apple Silicon SEP driver and its libfprint
integration. Intel T2's PCI/bridgeOS transport is not this machine's transport.
[T2Touch](https://github.com/tonibergholm/t2touch) informed the investigation but
was not installed on the M3.

## Tested sequence

1. Inspected the pinned release installer and verified package checksums.
2. Retained the previous boot files, kernel packages and an iBoot container image
   privately. A second Apple Silicon Mac was available for DFU recovery.
3. Installed the release with `--read-only --m3-handoff --no-m3-mesa`, then rebooted.
4. Confirmed all 12 SEP endpoints, the sensor and `/dev/sep-bio`.
5. Changed the SEP options to `xart_writes=1 provision_keybag=1`, then rebooted.
   The prior `xart_writes=0 provision_keybag=0` boot had correctly refused to
   activate without a Linux identity keybag.
6. Enrolled a finger through fprintd. An unenrolled-finger control returned
   `verify-no-match`. The enrolled finger returned no-match once, then matched.
7. Enabled fingerprint PAM only after successful matching. Existing sudo password
   includes were retained; Omarchy's `omarchy-apply-lock` configured its separate
   password and fingerprint lock services.
8. Verified sudo, fingerprint lock-screen unlock and return to a responsive
   desktop. A graphical `pkexec /usr/bin/true` prompt completed as well.
9. Rebooted. SEP restored master/owner/user Catacombs and one live identity;
   fprintd verification and sudo authentication passed again.

Do not reload or unbind an attached SEP driver to retry provisioning. Its DMA
handoff is once per boot. Use the matched release's instructions and a reboot.

An earlier sudo test timed out before a later successful test. Neither one match
nor this small test sequence establishes accuracy or reliability statistics.

## Limits

macOS Touch ID after Linux enrollment, Linux/macOS round trips, sleep/resume,
additional fingers, deletion and physical password-fallback authentication have
not been tested here. No claim is made for J615 or other M3 boards.

Read the release's
[xART storage notes](https://github.com/omacom/linux-aurora/blob/5ec1028c81526e1ed31db2b97e47edf8663e83cb/tools/aurora-sep/XART-SAFETY.md).
An iBoot image cannot promise recovery of SEP anti-replay state. No identity,
calibration or biometric files belong in this repository.
