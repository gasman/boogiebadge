import display
import buttons
import machine
import system
import json

from .player import CHANNEL_COUNT, ROW_COUNT, Player, Track
from .ui import Button, Controller, Focusable, NumberInput, View, Widget

WAVEFORM_SINE = 0
WAVEFORM_SQUARE = 1
WAVEFORM_TRIANGLE = 2
WAVEFORM_SAWTOOTH = 3
WAVEFORM_NOISE = 4


controller = Controller()


track_data = """{
    "patterns": [
        {
            "rows": [[40, 1], [null, 0], [40, 1], [null, 0], [null, 0], [null, 0], [40, 1], [null, 0], [null, 0], [null, 0], [40, 1], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0]],
            "default_sample": 1,
            "default_pitch": 40,
            "label": "kick"
        },
        {
            "rows": [[null, 0], [null, 0], [null, 0], [null, 0], [20, 2], [null, 0], [null, 0], [20, 2], [null, 0], [20, 2], [null, 0], [null, 0], [20, 2], [null, 0], [null, 0], [null, 0]],
            "default_sample": 2,
            "default_pitch": 20,
            "label": "snare"
        },
        {
            "rows": [[25, 3], [25, 3], [25, 3], [25, 3], [null, 0], [null, 0], [25, 3], [25, 3], [25, 3], [25, 3], [25, 3], [25, 3], [null, 0], [null, 0], [25, 3], [25, 3]],
            "default_sample": 3,
            "default_pitch": 25,
            "label": "hh closed"
        },
        {
            "rows": [[null, 0], [null, 0], [null, 0], [null, 0], [30, 4], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [null, 0], [30, 4], [null, 0], [null, 0], [null, 0]],
            "default_sample": 4,
            "default_pitch": 30,
            "label": "hh open"
        }
    ],
    "samples": {
        "1": {
            "waveform": 1,
            "volumes": [15, 12, 9, 6, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "frequencies": [0, -20, -40, -60, -80, -100, -120, -140, -160, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        },
        "2": {
            "waveform": 4,
            "volumes": [8, 7, 6, 5, 4, 4, 3, 3, 2, 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "frequencies": [0, -10, -20, -30, -40, -50, -60, -70, -80, -90, -100, -110, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        },
        "3": {
            "waveform": 4,
            "volumes": [8, 6, 4, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "frequencies": [0, -10, -20, -30, -40, -50, -60, -70, -80, -90, -100, -110, -120, -130, -140, -150, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        }
        "4": {
            "waveform": 4,
            "volumes": [8, 7, 6, 5, 4, 3, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "frequencies": [0, -10, -20, -30, -40, -50, -60, -70, -80, -90, -100, -110, -120, -130, -140, -150, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        }
    },
    "tempo": 5
}"""
track = Track.from_json(json.loads(track_data))
print(json.dumps(track.to_json()))

player = Player()
player.load_track(track)


class PlayButton(Button):
    help_text = "press A or START to play / stop"

    def on_press_a(self):
        if player.is_playing:
            player.stop()
        else:
            player.start()


class StepSequencerView(View):
    def __init__(self, track):
        self.step_sequencer_widget = StepSequencerWidget(track.patterns)
        self.play_button = PlayButton("Play", 10, 10)

        def change_tempo(new_tempo):
            track.tempo = new_tempo

        self.tempo_input = NumberInput(
            "Tempo", track.tempo, 60, 10,
            min_value=1,
            max_value=15,
            on_change=change_tempo,
        )

        self.widgets = [
            self.play_button,
            self.tempo_input,
            self.step_sequencer_widget,
        ]
        super().__init__()

    def activate(self):
        player.on_play_row(lambda row: self.step_sequencer_widget.highlight_column(row, flush=True))

        def on_start():
            self.play_button.set_label("Stop")
            display.flush()
        player.on_start(on_start)

        def on_stop():
            self.step_sequencer_widget.unhighlight_column(flush=True)
            self.play_button.set_label("Play")
            display.flush()
        player.on_stop(on_stop)

        self.play_button.on_focus()

    def on_press_start(self):
        if player.is_playing:
            player.stop()
        else:
            player.start()

    def deactivate(self):
        pass
        # TODO: detach event handlers from player


class StepSequencerWidget(Focusable, Widget):
    help_text = "press A to toggle drum on / off"

    def __init__(self, patterns):
        self.patterns = patterns
        self.active_column = None
        self.cursor_x = 0
        self.cursor_y = 0
        super().__init__()

    def draw(self):
        for y, pattern in enumerate(self.patterns):
            display.drawText(
                0,
                87 + y*16,
                pattern.label,
                0x000000,
            )

            for x, row in enumerate(pattern.rows):
                self.render_cell(y, x, 0x000000)

        if self.focused:
            self.render_cursor(0x0000cc)

        super().draw()

    def render_cell(self, y, x, colour):
        if self.patterns[y].rows[x][0]:
            display.drawRect(64 + x * 16, 88 + y * 16, 15, 15, True, colour)
        else:
            display.drawRect(64 + x * 16, 88 + y * 16, 15, 15, True, 0xffffff)
            display.drawRect(64 + x * 16, 88 + y * 16, 14, 14, False, colour)

    def render_column(self, x, colour):
        for y, pattern in enumerate(self.patterns):
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
        display.drawRect(63 + self.cursor_x * 16, 87 + self.cursor_y * 16, 16, 16, False, colour)

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

    def on_press_a(self):
        pattern = self.patterns[self.cursor_y]
        if pattern.rows[self.cursor_x][0]:
            pattern.rows[self.cursor_x] = None, 0
        else:
            pattern.rows[self.cursor_x] = (pattern.default_pitch, pattern.default_sample)

        self.render_cell(self.cursor_y, self.cursor_x, 0x000000)

sequencer_view = StepSequencerView(track)
controller.set_view(sequencer_view)


timer = machine.Timer(1)
timer.init(period=20, callback=lambda t: player.tick())


buttons.attach(buttons.BTN_HOME, lambda pressed: system.launcher())
