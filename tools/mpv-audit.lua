-- Read-only mpv playback counters. No media names or account identifiers.
-- mpv --script=tools/mpv-audit.lua video.mp4
local mp = require 'mp'
local utils = require 'mp.utils'
local last = {}
local function sample()
    if not mp.get_property_native('video-params') then return end
    last = {
        hwdec = mp.get_property('hwdec-current'),
        vo = mp.get_property('current-vo'),
        dropped = mp.get_property_number('frame-drop-count', 0),
        decoder_dropped = mp.get_property_number('decoder-frame-drop-count', 0),
        mistimed = mp.get_property_number('mistimed-frame-count', 0),
        delayed = mp.get_property_number('vo-delayed-frame-count', 0),
        time_pos = mp.get_property_number('time-pos', 0),
        fullscreen = mp.get_property_native('fullscreen')
    }
end
mp.add_periodic_timer(0.1, sample)
mp.register_event('end-file', function(event)
    sample()
    last.reason = event.reason
    mp.msg.info('M3_PLAYBACK_RESULT ' .. utils.format_json(last))
end)
