import display
import buttons
import machine
import system
import json

from .player import Player, Track

WAVEFORM_SINE = 0
WAVEFORM_SQUARE = 1
WAVEFORM_TRIANGLE = 2
WAVEFORM_SAWTOOTH = 3
WAVEFORM_NOISE = 4


track_data = """{"pattern": [[[57, 1], [null, 0], [57, 1], [null, 0], [null, 0], [57, 1], [null, 0], [52, 1], [null, 0], [null, 0], [52, 1], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0]], [[33, 2], [null, 0], [null, 0], [null, 0], [33, 2], [null, 0], [null, 0], [null, 0], [33, 2], [null, 0], [null, 0], [null, 0], [33, 2], [null, 0], [null, 0], [null, 0]], [[null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0]], [[null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0]]], "samples": {"2": {"waveform": 3, "volumes": [15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}, "1": {"waveform": 1, "volumes": [15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}}, "tempo": 5}"""
track = Track.from_json(json.loads(track_data))


player = Player()
player.load_track(track)


def render_step_sequencer(pattern):
    display.drawFill(display.WHITE)

    for y, channel in enumerate(pattern):
        for x, row in enumerate(channel):
            if row[0]:
                display.drawRect(32 + x * 16, 88 + y * 16, 15, 15, True, 0x000000)
            else:
                display.drawRect(32 + x * 16, 88 + y * 16, 14, 14, False, 0x000000)
    display.flush()


render_step_sequencer(track.pattern)


def tick(t):
    player.tick()


timer = machine.Timer(0)
timer.init(period=20, callback=tick)


def on_action_btn(pressed):
    if pressed:
        player.start()

buttons.attach(buttons.BTN_A, on_action_btn)
buttons.attach(buttons.BTN_B, lambda pressed: system.launcher())
