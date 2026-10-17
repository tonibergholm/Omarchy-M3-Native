-- Read-only mpv playback counters. No media names or account identifiers.
-- mpv --script=tools/mpv-audit.lua video.mp4
local mp = require 'mp'
local utils = require 'mp.utils'
local options = require 'mp.options'
local opts = { interval = 0 }
options.read_options(opts, 'm3-audit')
if opts.interval ~= 0 and (opts.interval ~= opts.interval or opts.interval < 1 or opts.interval > 60) then
    mp.msg.error('m3-audit interval must be 0 (disabled) or 1..60 seconds')
    opts.interval = 0
end
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
        fullscreen = mp.get_property_native('fullscreen'),
        video_sync = mp.get_property('video-sync'),
        display_sync_active = mp.get_property_native('display-sync-active'),
        display_fps = mp.get_property_number('display-fps'),
        estimated_display_fps = mp.get_property_number('estimated-display-fps')
    }
end
mp.add_periodic_timer(0.1, sample)
if opts.interval > 0 then
    mp.add_periodic_timer(opts.interval, function()
        sample()
        if next(last) then
            mp.msg.info('M3_PLAYBACK_SAMPLE ' .. utils.format_json(last))
        end
    end)
end
mp.register_event('end-file', function(event)
    sample()
    last.reason = event.reason
    mp.msg.info('M3_PLAYBACK_RESULT ' .. utils.format_json(last))
end)
