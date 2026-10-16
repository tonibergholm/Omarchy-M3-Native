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
