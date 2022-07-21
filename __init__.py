import display
import buttons
import machine
import system
import json

from .player import CHANNEL_COUNT, ROW_COUNT, Player, Track
from .ui import Button, Controller, Focusable, View, Widget

WAVEFORM_SINE = 0
WAVEFORM_SQUARE = 1
WAVEFORM_TRIANGLE = 2
WAVEFORM_SAWTOOTH = 3
WAVEFORM_NOISE = 4


controller = Controller()


track_data = """{"pattern": [[[57, 1], [null, 0], [57, 1], [null, 0], [null, 0], [57, 1], [null, 0], [52, 1], [null, 0], [null, 0], [52, 1], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0]], [[33, 2], [null, 0], [null, 0], [null, 0], [33, 2], [null, 0], [null, 0], [null, 0], [33, 2], [null, 0], [null, 0], [null, 0], [33, 2], [null, 0], [null, 0], [null, 0]], [[null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0]], [[null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0]]], "samples": {"2": {"waveform": 3, "volumes": [15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}, "1": {"waveform": 1, "volumes": [15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}}, "tempo": 5}"""
track = Track.from_json(json.loads(track_data))


player = Player()
player.load_track(track)


class StepSequencerView(View):
    def __init__(self, track):
        self.step_sequencer_widget = StepSequencerWidget(track.pattern)
        self.play_button = Button("Play", 10, 10)

        self.widgets = [
            self.play_button,
            self.step_sequencer_widget,
        ]
        super().__init__()

    def activate(self):
        player.on_play_row(lambda row: self.step_sequencer_widget.highlight_column(row, flush=True))
        player.on_stop(lambda: self.step_sequencer_widget.unhighlight_column(flush=True))

    def deactivate(self):
        pass
        # TODO: detach event handlers from player


class StepSequencerWidget(Focusable, Widget):
    def __init__(self, pattern):
        self.pattern = pattern
        self.active_column = None
        self.cursor_x = 0
        self.cursor_y = 0
        super().__init__()

    def draw(self):
        for y, channel in enumerate(self.pattern):
            for x, row in enumerate(channel):
                self.render_cell(y, x, 0x000000)

        if self.focused:
            self.render_cursor(0x0000cc)

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

    def render_cursor(self, colour):
        display.drawRect(31 + self.cursor_x * 16, 87 + self.cursor_y * 16, 16, 16, False, colour)

    def set_cursor(self, x, y):
        if x == self.cursor_x and y == self.cursor_y:
            return

        # clear old cursor
        self.render_cursor(0xffffff)
        self.cursor_x = x
        self.cursor_y = y
        # draw new cursor
        self.render_cursor(0x0000cc)

        display.flush()

    def on_move(self, button):
        if button == buttons.BTN_UP:
            if self.cursor_y == 0:
                return False
            else:
                self.set_cursor(self.cursor_x, self.cursor_y - 1)
        elif button == buttons.BTN_DOWN:
            if self.cursor_y == CHANNEL_COUNT - 1:
                return False
            else:
                self.set_cursor(self.cursor_x, (self.cursor_y + 1) % CHANNEL_COUNT)
        elif button == buttons.BTN_LEFT:
            self.set_cursor((self.cursor_x - 1) % ROW_COUNT, self.cursor_y)
        elif button == buttons.BTN_RIGHT:
            self.set_cursor((self.cursor_x + 1) % ROW_COUNT, self.cursor_y)

        return True

    def on_focus(self, button):
        if button in (buttons.BTN_LEFT, buttons.BTN_UP):
            self.cursor_y = CHANNEL_COUNT - 1
        else:
            self.cursor_y = 0
        super().on_focus(button)

    def on_blur(self, button):
        self.render_cursor(0xffffff)
        super().on_blur(button)


sequencer_view = StepSequencerView(track)
controller.set_view(sequencer_view)


timer = machine.Timer(1)
timer.init(period=20, callback=lambda t: player.tick())


def on_btn_a(pressed):
    if pressed:
        player.start()

def on_btn_b(pressed):
    if pressed:
        player.stop()


buttons.attach(buttons.BTN_A, on_btn_a)
buttons.attach(buttons.BTN_B, on_btn_b)
buttons.attach(buttons.BTN_HOME, lambda pressed: system.launcher())
