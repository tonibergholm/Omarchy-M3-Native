# Remaining work

1. **Thermal policy:** sensor reporting and GPU consumption now work. Check
   CPU thermal cooling bindings, sensor coverage/freshness, and failure behavior.
   Keep the GPU state-2 ceiling until a separate higher-clock test is justified.
2. **Display brightness/HDR:** the [local J613 backlight candidate](display.md)
   passed visible steps, keys/OSD, bounds rejection and DPMS checks. Verify
   repeated/long suspend before broader acceptance; one normal reboot restored
   both brightness values exactly. Native HDR
   remains blocked; initial software PQ-to-SDR conversion ran successfully.
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
5. **Audio startup:** reproduce the initial sample-rate failure across boots
   before changing service ordering. Clear [microphone capture](capture.md) passed; test jack switching and
   remote-call capture.
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
   default-off J613/BCM4388 recovery candidate passed a temporary load and one
   70-second sleep cycle. The packaged driver was restored; no timeout recovery
   callback was exercised.
   Native recovery and peripheral checks remain pending. No whole-machine
   battery-life claim follows from cpuidle counters.

Publish evidence against exact releases and named hardware. Keep one upstream
thread for a known issue, and send reusable fixes to their owning project.


## Current validation gates after unattended checks

The Bluetooth recovery candidate passed a temporary native load, awake HCI
reply and one approximately 70-second sleep cycle. Wi-Fi remained connected,
and the original driver was restored with a successful HCI reply afterward.
No timeout occurred during the candidate cycle, so recovery, calibration reload
and peripheral connectivity remain unqualified. See the
[native Bluetooth report](../reports/2026-10-18-bluetooth-native-short-cycle.json).

The passive observer completed its first real matched sleep/resume capture and
all three delayed samples at approximately 30, 60 and 120 seconds. Suspend success
increased by one with no failure; screen and keyboard brightness were stable.
The charger was connected throughout, so this gives no sleep-drain estimate.
See the [native observer report](../reports/2026-10-18-sleep-observer-native.json).

AV1 grain correction remains unfinished. The process-local rejection prototype
demonstrated correct software fallback; a [source safeguard](video.md) now passes
47 focused sanitizer cases in draft driver PR #107. Hosted validation on
19 October passed 243/243 sanitizer tests, both software checks and the full
11-job matrix after one recorded test-helper retry. This supersedes the local
thermal/CI-authorization blocker. Native candidate checks and independent review remain pending. Installed drivers still have the original
failing sample behavior; hardware synthesis remains unresolved. Physical peripheral/quality checks and
thermal/HDR support are separate remaining gates. The
[earlier audit](../reports/2026-10-18-validation-gates.json) records the state
before the attended Bluetooth cycle.
