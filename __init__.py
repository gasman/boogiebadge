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


class StepSequencer:
    def __init__(self, pattern):
        self.pattern = pattern
        self.active_column = None

    def render_all(self):
        display.drawFill(display.WHITE)

        for y, channel in enumerate(self.pattern):
            for x, row in enumerate(channel):
                self.render_cell(y, x, 0x000000)
        display.flush()

    def render_cell(self, y, x, colour):
        if self.pattern[y][x][0]:
            display.drawRect(32 + x * 16, 88 + y * 16, 15, 15, True, colour)
        else:
            display.drawRect(32 + x * 16, 88 + y * 16, 14, 14, False, colour)

    def render_column(self, x, colour):
        for y, channel in enumerate(self.pattern):
            self.render_cell(y, x, colour)

    def unhighlight_column(self, flush=False):
        if self.active_column is not None:
            self.render_column(self.active_column, 0x000000)
        if flush:
            display.flush()

    def highlight_column(self, column, flush=False):
        if column != self.active_column:
            self.unhighlight_column()
            self.active_column = column
            if column is not None:
                self.render_column(column, 0x00cc00)
        if flush:
            display.flush()


sequencer = StepSequencer(track.pattern)
sequencer.render_all()
player.on_play_row(lambda row: sequencer.highlight_column(row, flush=True))
player.on_stop(lambda: sequencer.unhighlight_column(flush=True))

def tick(t):
    player.tick()


timer = machine.Timer(0)
timer.init(period=20, callback=tick)


def on_btn_a(pressed):
    if pressed:
        player.start()

def on_btn_b(pressed):
    if pressed:
        player.stop()


buttons.attach(buttons.BTN_A, on_btn_a)
buttons.attach(buttons.BTN_B, on_btn_b)
buttons.attach(buttons.BTN_HOME, lambda pressed: system.launcher())
