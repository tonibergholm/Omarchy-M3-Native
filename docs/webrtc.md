# Local WebRTC loopback — J613, 2026-10-16

On the [tested stack](tested-stack.md), Chromium 153.0.8010.36 captured the real
camera and microphone, sent them between two local RTCPeerConnections and
displayed the received video. An isolated browser profile and a localhost-only
test page were used. No STUN/TURN server or external peer was configured. No
speech, video, SDP, ICE candidates, IP addresses or device identifiers are in
the reports. Audio playback was muted to avoid feedback; decoded-audio counters
and microphone activity were checked, not audible remote voice quality.

## Default negotiation

The first 30-second call worked according to the operator, but a 20-second
statistics sample showed the sender downscaled to **320×180** and reported a
bandwidth quality limitation. VP8 encode/decode used `libvpx`; audio was Opus.
A late collector update overwrote the final counters, so the
[retained default observation](../reports/2026-10-16-webrtc-default-sample.json)
is explicitly a mid-run sample, not complete totals. The collector was fixed
to retain final results before the next pass.

## 720p-focused pass

The test page requested exact 1280×720 capture and used the sender's
`maintain-resolution` degradation preference, a 4 Mbps bitrate cap and a 30 fps
cap. These were local test-page settings; no normal browser or system defaults
were changed. The 4 Mbps value is a cap, not a measured rate or a target guarantee.

Over **30 seconds**:

- The sender reported 1280×720 at 30 fps; 895 frames were encoded and 888 decoded.
- The receiving video element produced 815 frame callbacks, about **27.17 fps**.
- Inbound video `framesDropped` and video/audio packet-loss counters were zero.
- Opus reception counted 1500 packets and 1439520 decoded audio samples.
  There were 682 concealed audio samples; audible remote voice was not tested.
- VP8 encode/decode both reported `libvpx`, with power-efficient flags false.
  This is a **software-codec** result, not hardware video encode/decode proof.
- Average reported encoding time was 15.467 ms per frame; decoding 8.378 ms.
  The final quality-limitation reason was `none`, not a whole-run guarantee.
- The highest 1 Hz sampled CPU temperature was **59.125°C**. The 78°C test
  guard did not trigger; no power policy or clock limit was changed.
- Both capture tracks ended and both peers closed automatically. The operator
  confirmed both video views and microphone activity worked. OpenGL and Vulkan
  readback passed after the call.

The selected [720p report](../reports/2026-10-16-webrtc-loopback.json) uses fields
from the [WebRTC statistics specification](https://www.w3.org/TR/webrtc-stats/).
The test browser and local server were closed after collection. A short local
loopback does not qualify internet links, remote conferencing services,
long-running calls, echo cancellation quality or other codecs.
