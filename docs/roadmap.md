# Remaining work

1. **Thermal policy:** sensor reporting and GPU consumption now work. Check
   CPU thermal cooling bindings, sensor coverage/freshness, and failure behavior.
   Keep the GPU state-2 ceiling until a separate higher-clock test is justified.
2. **Display brightness/HDR:** the [local J613 backlight candidate](display.md)
   passed visible steps, keys/OSD, bounds rejection and DPMS checks. Verify
   another reboot and suspend/resume before broader acceptance. Native HDR
   remains blocked; initial software PQ-to-SDR conversion ran successfully.
3. **Sleep/resume:** only s2idle is advertised. Preserve lock intent and verify
   display, GPU, input, sound and Touch ID after an attended sleep. Presence of
   CPU idle states does not prove whole-machine suspend works.
4. **macOS coexistence:** verify macOS Touch ID and Linux enrollment after a
   round trip, without deleting or replacing either system's authority.
5. **Audio startup:** reproduce the initial sample-rate failure across boots
   before changing service ordering. Test jack switching and microphone capture.
6. **Video/camera:** [initial H.264 checks](video.md) passed decoder equivalence
   and 1080p30 playback; short 1080p60 fast-profile playback improved presentation
   counts. Test browser playback, other codecs and sustained use. Camera device
   detection alone is not a working capture test.
7. **Power and external devices:** measure settled idle draw, battery runtime,
   shutdown and specific USB-C display/dock combinations. No whole-machine
   battery-life claim follows from cpuidle counters.

Publish evidence against exact releases and named hardware. Keep one upstream
thread for a known issue, and send reusable fixes to their owning project.
