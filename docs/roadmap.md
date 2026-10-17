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
4. **macOS coexistence:** verify macOS Touch ID and Linux enrollment after a
   round trip, without deleting or replacing either system's authority.
5. **Audio startup:** reproduce the initial sample-rate failure across boots
   before changing service ordering. Clear [microphone capture](capture.md) passed; test jack switching and
   remote-call capture.
6. **Video/camera:** [initial H.264 checks](video.md) passed decoder equivalence
   and 1080p30 playback; short 1080p60 fast-profile playback improved presentation
   counts. A three-minute 1080p60 fast-profile run completed with zero decoder
   drops and 25 presentation drops; the operator reported smooth, correct output.
   Test browser playback, other codecs and longer use. The local
   [ISP14.7 camera candidate](capture.md) delivers 1080p30 frames after reboot and sleep. Local Chromium
   camera/mic capture and [software-codec WebRTC loopback](webrtc.md) passed
   at 720p. Qualify remote calls, indicator behavior,
   sustained use and good-light picture quality.
7. **Power and external devices:** [initial battery observations](power.md)
   need longer, steadier measurements. Measure settled idle draw, battery runtime,
   shutdown and specific USB-C display/dock combinations. No whole-machine
   battery-life claim follows from cpuidle counters.

Publish evidence against exact releases and named hardware. Keep one upstream
thread for a known issue, and send reusable fixes to their owning project.
