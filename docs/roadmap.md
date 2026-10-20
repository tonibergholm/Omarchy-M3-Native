# Remaining work

1. **Thermal policy:** the [PR146 DT-only native trial](thermal.md) passed
   six CPU-zone/both-cluster cooling bindings, energy-model registration,
   simulated temperature-driven power allocation and frequency limiting,
   short sleep recovery and post-resume cooling controls. After the one-boot
   rollback passed, the owner chose to retain the same tested DT candidate.
   Its boot image is hash-verified and the original backup is preserved;
   package rebuilds may replace the local image.
   Sustained real-temperature regulation, sensor accuracy and failure behavior
   remain unqualified. Keep the GPU state-2 ceiling.
2. **Display brightness/HDR:** the [local J613 backlight candidate](display.md)
   passed visible steps, keys/OSD, bounds rejection and DPMS checks. Verify
   repeated/long suspend before broader acceptance; one normal reboot restored
   both brightness values exactly. Native HDR
   remains blocked; initial software PQ-to-SDR conversion ran successfully.
   A local bootloader reservation trial now drives the ARZOPA Z1FC on both
   USB-C ports at 1080p60, with short 1080p144, rear hotplug, DPMS and one
   approximately 10-second attached-display suspend passing. Both pictures,
   Touch ID and GPU checks recovered. The original boot image was restored
   automatically; repeated boots, longer sleep and sustained 144 Hz remain
   open. See the [external-display evidence](display.md#arzopa-z1fc-external-display-19-october).
3. **Sleep/resume:** [short power-button and lid-wake cycles](sleep.md) passed
   Touch ID unlock, brightness, GPU readback and audible protected playback.
   A further unplugged 17½-minute lid cycle and three consecutive attended lid
   cycles passed recovery; battery counters were inconclusive. A lid-open Enter-key
   wake and subsequent Touch ID unlock passed once; a separate lid-open trackpad
   wake also passed once. Test a larger cycle count. One 9h19m overnight recovery passed, but
   measured battery loss was 27 percentage points; investigate sleep draw.
4. **macOS coexistence:** one round trip passed macOS Touch ID and Linux matching
   with existing enrollments unchanged. Repeat coexistence remains unqualified;
   do not delete or replace either system's authority.
5. **Audio startup:** the .20 boot observer captured IV-sense frame progress
   while the speaker-rate control was zero, immediately before the startup
   panic. Root cause and a protective fix remain open; do not assume a rate
   or bypass speaker protection. Clear [microphone capture](capture.md)
   passed; test jack switching and remote-call capture. Earlier multi-rate
   process-exit and PCM-negotiation checks did not establish healthy playback:
   later rate transitions caused repeated speaker-protection negative-power
   panics. The local graph is now fixed at 48 kHz. On Aurora .20, continuous
   and separate short clips were audible, including after lid sleep, without
   additional protection-daemon restarts. One startup `Invalid sample rate`
   panic remains unresolved; evidence is on the
   [existing upstream issue](https://github.com/AsahiLinux/speakersafetyd/issues/16#issuecomment-6264611425).
   See the [rate-failure report](../reports/2026-10-19-audio-rate-transition-failure.json)
   and [.20 sleep result](../reports/2026-10-19-aurora20-sleep.json).
6. **Video/camera:** [initial H.264 checks](video.md) passed decoder equivalence
   and 1080p30 playback; short 1080p60 fast-profile playback improved presentation
   counts. A three-minute 1080p60 fast-profile run completed with zero decoder
   drops and 25 presentation drops; the operator reported smooth, correct output.
   Headless High-profile H.264/B-frame and short HEVC Main pixel-equivalence
   checks passed. Small HEVC Main10, VP9, AV1 8-bit and grain-free AV1 10-bit
   checks also passed; one AV1 grain-bearing sample produced all-zero hardware
   output. Investigate that failure, test sustained codec playback and browser
   support. The local
   [ISP14.7 camera candidate](capture.md) delivers 1080p30 frames after reboot and sleep. Local Chromium
   camera/mic capture and [software-codec WebRTC loopback](webrtc.md) passed
   at 720p. Qualify remote calls, indicator behavior,
   sustained use and good-light picture quality.
7. **Power and external devices:** [initial battery observations](power.md)
   need longer, steadier measurements. Measure settled idle draw, battery runtime,
   shutdown and specific USB-C display/dock combinations. Bluetooth failed a
   local HCI read after overnight resume and normal power-off failed; a
   default-off J613/BCM4388 recovery candidate initially passed a temporary load
   and a cycle without a timeout. On .20, awake JBL Flip 5 SBC/A2DP playback
   passed, but a connected lid cycle lost Bluetooth. The recovery admission
   candidate exercised its callback and failed HCI reset; a setup-ordering
   variant failed calibration transfer. One later diagnostic cycle recovered
   JBL audio automatically without a timeout, so recovery remains unqualified.
   Original driver reload restored connection; every candidate was removed.
   See [selected Bluetooth evidence](sleep.md#jbl-flip-5-audio-19-october). No whole-machine
   battery-life claim follows from cpuidle counters.

Publish evidence against exact releases and named hardware. Keep one upstream
thread for a known issue, and send reusable fixes to their owning project.


## Current validation gates after unattended checks

The Bluetooth recovery candidate passed a temporary native load, awake HCI
reply and one approximately 70-second sleep cycle. Wi-Fi remained connected,
and the original driver was restored with a successful HCI reply afterward.
That earlier cycle did not exercise recovery or peripherals. The subsequent
19 October JBL tests exercised timeout recovery and failed both candidate
variants, as described above. Awake and one no-timeout resume playback passed;
reliable Bluetooth sleep recovery remains open. See the
[earlier native report](../reports/2026-10-18-bluetooth-native-short-cycle.json)
and [current failure evidence](../reports/2026-10-19-bluetooth-recovery-v2-failure.json).
A read-only check after four lid cycles verified all six CPU zones still had
both-cluster cooling bindings and original 58/95/110°C trips. Speaker protection
was active with only its known startup restart. All Bluetooth candidates and
rollback timers were inactive; see the [regression snapshot](../reports/2026-10-19-post-bluetooth-regression.json).

The passive observer completed its first real matched sleep/resume capture and
all three delayed samples at approximately 30, 60 and 120 seconds. Suspend success
increased by one with no failure; screen and keyboard brightness were stable.
The charger was connected throughout, so this gives no sleep-drain estimate.
See the [native observer report](../reports/2026-10-18-sleep-observer-native.json).

AV1 grain correction remains unfinished. The process-local rejection prototype
demonstrated correct software fallback; a [source safeguard](video.md) now passes
47 focused sanitizer cases in driver PR #107, now ready for review. Hosted validation on
19 October passed 243/243 sanitizer tests, both software checks and the full
11-job matrix after one recorded test-helper retry. This supersedes the local
thermal/CI-authorization blocker. A selected native candidate check subsequently
matched all ten grain-fallback frames and all 50 grain-free hardware frames.
Broader qualification and independent review remain pending. Installed drivers still have the original
failing sample behavior; hardware synthesis remains unresolved. Physical peripheral/quality checks and
thermal/HDR support are separate remaining gates. The
[earlier audit](../reports/2026-10-18-validation-gates.json) records the state
before the attended Bluetooth cycle.

## Desktop idle repair

The local ChatGPT-only inhibitor workaround passed normal 150-second
screensaver/300-second secure lock and DPMS, an operator-confirmed reboot
cycle with Touch ID unlock, and a live mpv inhibitor check beyond five minutes.
Other reported application inhibitors and Stay Awake remain respected.
[Quickshell PR1097](https://github.com/quickshell-mirror/quickshell/pull/1097)
is the existing upstream fix; the local service clone remains in use.
See [power/idle evidence](power.md).

## Newer repository kernel audit, 20 October

Edge already offers `linux-aurora 7.2.10.aurora1-2`, newer than the installed .19 and isolated .20 experiments. Checking only the experimental SEP release list had missed this package lineage. Dev mode would use the same edge repository. The signed package and pinned source explicitly refuse M3 GPU startup (`refuse_probe` returns `ENODEV`), and its J613 DTB has no thermal zones. It is not a replacement that preserves the working M3 acceleration and thermal setup. No package/channel change or boot was performed. See the [read-only preflight](../reports/2026-10-20-aurora72-preflight.json).
