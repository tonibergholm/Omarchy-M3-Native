# Audio and keyboard illumination

## Audio

Both J613 audio cards and Asahi DSP profiles were already installed. Speaker
protection logged an initial “Invalid sample rate” failure and restarted.
Restarting PipeWire, pipewire-pulse and WirePlumber, then selecting the protected
`audio_effect.j613-convolver` sink at 20%, produced a clear physical test tone.
The daemon reported 48 kHz and the kernel confirmed speaker volumes unlocked.
This establishes recovery, not the cause of the original startup failure.

The sink/volume survived service restart; later boots retained the setting and
an active protection daemon. Audible playback was not repeated after every boot.
Do not bypass speaker protection or send test signals to raw speaker devices.

## Startup investigation on Aurora .20

One startup `Invalid sample rate` panic occurred on .20; automatic restart
recovered. Audible continuous and separate short clips passed before and after
lid sleep with no additional daemon restart. Earlier multi-rate graph changes
on .19 caused negative-power protection panics. The local graph is now fixed at
48 kHz; this is a workaround, not a startup fix. See the
[source audit](../reports/2026-10-19-audio-startup-source-audit.json) and
[upstream evidence](https://github.com/AsahiLinux/speakersafetyd/issues/16#issuecomment-6264611425).

The [read-only startup recorder](../tools/audio-startup-observer.py) samples the
speaker-rate control and selected speaker/sense PCM state and frame counters at
100 ms intervals, for at most 60 seconds. It opens only the ALSA control device;
it neither opens a PCM stream nor changes controls. An explicit new output path
is required; existing files and symlinks are refused. Output is created mode
0600. It requires J613, Python 3, libasound and permission to read the sound card.
The two-second awake check captured 20 samples without read errors on .20.

Keep recordings private and publish selected findings only. Sampling can miss
short transitions, reads are not atomic across control/PCM fields, and observer
activity can alter timing. A missing event does not prove the race is absent.
The sense PCM can display `rate: 0 (48000/1)` during healthy 48 kHz operation;
interpret the control value and stream progression together, not just that
leading zero. The optional `--notify-ready` sends systemd readiness only after the first
sample is saved; it requires `NOTIFY_SOCKET`. A private Unix-socket test and
a short native systemd notify-service test passed. A first boot recorder
using plain exec readiness started sampling 0.529 seconds after the panic;
its successful 600-sample recording therefore did not capture the failing
transition. See the [selected boot observation](../reports/2026-10-19-audio-startup-boot-observation.json).
The recorder does not install a boot service.

## Keyboard backlight

`kbd_backlight` was present with range 0–255 and initially zero. Setting it to
30% worked and survived reboot through the system's existing save/restore path.

```sh
brightnessctl -d kbd_backlight set 30%
```

These previously unbound local shortcuts were added to
`~/.config/hypr/bindings.lua`:

```lua
o.bind("SUPER + F5", "Keyboard brightness down", "omarchy-brightness-keyboard down", { repeating = true })
o.bind("SUPER + F6", "Keyboard brightness up", "omarchy-brightness-keyboard up", { repeating = true })
```

Hyprland reload and configuration-error checks passed. Back up personal bindings
and check for conflicts before applying the same shortcuts elsewhere.

## Event trace of the startup panic, 20 October

A one-boot trace captured the panic with both userspace and kernel probes armed before daemon startup, 49 selected events, zero buffer losses and no fetch faults. The daemon read rate zero at 11.968814 s. Other ALSA reads saw 48000 at 12.816313/12.816314 s during playback configuration; playback `hw_free` entries followed, including device 3 at 12.902241 s. At 12.911171 s the daemon's sense read returned 4096 frames; at 12.911198 s it read rate zero again; the panic journal timestamp was 12.911462 s. The initial and post-read zero values therefore missed a valid 48 kHz control interval. This strengthens the missed-transient-rate explanation that 100 ms polling could not establish.

No playback trigger was observed in the covered interval, so this does not establish audible playback or unknown-energy output. Kernel lifecycle probes capture entry arguments, not return success. The trace records no audio samples. It does not justify substituting the negotiated sense rate or retaining an assumed rate as a fix. Protection restarted normally once; no restart was requested by the test.

The one-boot unit adds a notify ordering delay, so the trace is instrumented evidence rather than unchanged boot timing. It stopped after 60 seconds, removed its probes/instance, consumed its arm marker and disabled itself; cleanup was independently checked. See the [selected event trace](../reports/2026-10-20-audio-startup-event-trace.json).
