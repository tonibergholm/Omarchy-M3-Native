# Remaining work

1. **Thermal policy:** sensor reporting and GPU consumption now work. Check
   CPU thermal cooling bindings, sensor coverage/freshness, and failure behavior.
   Keep the GPU state-2 ceiling until a separate higher-clock test is justified.
2. **Display brightness:** native display works, but no backlight device exists
   on this current14 firmware path. Follow [Aurora #32](https://github.com/omacom/linux-aurora/issues/32).
3. **Sleep/resume:** only s2idle is advertised. Preserve lock intent and verify
   display, GPU, input, sound and Touch ID after an attended sleep. Presence of
   CPU idle states does not prove whole-machine suspend works.
4. **macOS coexistence:** verify macOS Touch ID and Linux enrollment after a
   round trip, without deleting or replacing either system's authority.
5. **Audio startup:** reproduce the initial sample-rate failure across boots
   before changing service ordering. Test jack switching and microphone capture.
6. **Video/camera:** measure actual hardware decoder use and windowed/fullscreen
   behavior. Camera device detection alone is not a working capture test.
7. **Power and external devices:** measure settled idle draw, battery runtime,
   shutdown and specific USB-C display/dock combinations. No whole-machine
   battery-life claim follows from cpuidle counters.

Publish evidence against exact releases and named hardware. Keep one upstream
thread for a known issue, and send reusable fixes to their owning project.
