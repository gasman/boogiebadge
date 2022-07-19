import display
import buttons
import machine
import system
import json

from .player import CHANNEL_COUNT, ROW_COUNT, Player, Track
from .ui import Button

WAVEFORM_SINE = 0
WAVEFORM_SQUARE = 1
WAVEFORM_TRIANGLE = 2
WAVEFORM_SAWTOOTH = 3
WAVEFORM_NOISE = 4


class Joystick:
    def __init__(self):
        self.timer = machine.Timer(1)
        self.current_button = None
        self.ticks_since_press = 0
        self.debounce_ticks = 5
        self.listener = None

        def tick(t):
            if self.current_button is not None:
                self.ticks_since_press += 1
                if self.ticks_since_press > self.debounce_ticks and self.listener:
                    self.listener(self.current_button)

        self.timer.init(period=100, callback=tick)

        for button in (buttons.BTN_UP, buttons.BTN_DOWN, buttons.BTN_LEFT, buttons.BTN_RIGHT):
            self.add_event_handler(button)

    def add_event_handler(self, button):
        def event_handler(pressed):
            if pressed:
                self.current_button = button
                self.ticks_since_press = 0
                self.listener(self.current_button)
            elif self.current_button == button:
                self.current_button = None

        buttons.attach(button, event_handler)


joystick = Joystick()


track_data = """{"pattern": [[[57, 1], [null, 0], [57, 1], [null, 0], [null, 0], [57, 1], [null, 0], [52, 1], [null, 0], [null, 0], [52, 1], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0]], [[33, 2], [null, 0], [null, 0], [null, 0], [33, 2], [null, 0], [null, 0], [null, 0], [33, 2], [null, 0], [null, 0], [null, 0], [33, 2], [null, 0], [null, 0], [null, 0]], [[null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0]], [[null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0]]], "samples": {"2": {"waveform": 3, "volumes": [15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}, "1": {"waveform": 1, "volumes": [15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}}, "tempo": 5}"""
track = Track.from_json(json.loads(track_data))


player = Player()
player.load_track(track)


class StepSequencer:
    def __init__(self, pattern):
        self.pattern = pattern
        self.active_column = None
        self.cursor_x = 0
        self.cursor_y = 0

    def activate(self):
        self.render_all()
        joystick.listener = lambda button: self.move(button)
        player.on_play_row(lambda row: self.highlight_column(row, flush=True))
        player.on_stop(lambda: self.unhighlight_column(flush=True))

    def deactivate(self):
        joystick.listener = None
        # TODO: detach event handlers from player

    def render_all(self):
        display.drawFill(display.WHITE)

        for y, channel in enumerate(self.pattern):
            for x, row in enumerate(channel):
                self.render_cell(y, x, 0x000000)
        self.render_cursor(0x0000cc)
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

    def move(self, button):
        if button == buttons.BTN_UP:
            self.set_cursor(self.cursor_x, (self.cursor_y - 1) % CHANNEL_COUNT)
        elif button == buttons.BTN_DOWN:
            self.set_cursor(self.cursor_x, (self.cursor_y + 1) % CHANNEL_COUNT)
        elif button == buttons.BTN_LEFT:
            self.set_cursor((self.cursor_x - 1) % ROW_COUNT, self.cursor_y)
        elif button == buttons.BTN_RIGHT:
            self.set_cursor((self.cursor_x + 1) % ROW_COUNT, self.cursor_y)


sequencer = StepSequencer(track.pattern)
sequencer.activate()

play_button = Button("Play", 10, 10)
play_button.draw()
display.flush()

timer = machine.Timer(0)
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
