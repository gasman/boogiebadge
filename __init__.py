import display
import buttons
import machine
import sndmixer
import system

WAVEFORM_SINE = 0
WAVEFORM_SQUARE = 1
WAVEFORM_TRIANGLE = 2
WAVEFORM_SAWTOOTH = 3
WAVEFORM_NOISE = 4

# A-4 = 440Hz
# if C-0 has note value 0, note value = (octave * 12) + note
# C  C# D  D# E  F  F# G  G# A  A# B
# 0  1  2  3  4  5  6  7  8  9  10 11
# A4 = 48 + 9 = 57
# freq = 440 * 2**((n-57)/12)

TONES = [
    round(440 * 2**((n - 57) / 12))
    for n in range(0, 107)
]

SAMPLES = {
    1: {
        'waveform': WAVEFORM_SQUARE,
        'volumes': [15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    },
    2: {
        'waveform': WAVEFORM_SAWTOOTH,
        'volumes': [15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    }
}

PATTERN = [
    [
        (57, 1), (None, 0), (57, 1), (None, 0), (None, 0), (57, 1), (None, 0), (52, 1),
        (None, 0), (None, 0), (52, 1), (None, 0), (None, 0), (None, 0), (None, 0), (None, 0),
    ],
    [
        (33, 2), (None, 0), (None, 0), (None, 0), (33, 2), (None, 0), (None, 0), (None, 0),
        (33, 2), (None, 0), (None, 0), (None, 0), (33, 2), (None, 0), (None, 0), (None, 0),
    ],
    [
        (None, 0), (None, 0), (None, 0), (None, 0), (None, 0), (None, 0), (None, 0), (None, 0),
        (None, 0), (None, 0), (None, 0), (None, 0), (None, 0), (None, 0), (None, 0), (None, 0),
    ],
    [
        (None, 0), (None, 0), (None, 0), (None, 0), (None, 0), (None, 0), (None, 0), (None, 0),
        (None, 0), (None, 0), (None, 0), (None, 0), (None, 0), (None, 0), (None, 0), (None, 0),
    ],
]

TEMPO = 5


class Channel:
    def __init__(self, index):
        self.index = index
        self.id = sndmixer.synth()
        self.current_sample = None
        self.current_pitch = None
        self.sample_tick = 0

    def start(self):
        sndmixer.play(self.id)

    def load_row(self, row_index):
        pitch, sample_number = PATTERN[self.index][row_index]
        if pitch is None:
            return

        self.sample_tick = 0
        self.current_pitch = pitch
        if sample_number != 0:
            self.current_sample = SAMPLES[sample_number]

    def play_tick(self):
        if self.current_sample is None or self.sample_tick >= 32:
            sndmixer.volume(self.id, 0)
        else:
            sndmixer.waveform(self.id, self.current_sample['waveform'])
            sndmixer.freq(self.id, TONES[self.current_pitch])
            sndmixer.volume(self.id, self.current_sample['volumes'][self.sample_tick])

        self.sample_tick += 1


print("Hello, MCH2022 Badge!")

display.drawFill(display.WHITE)
display.drawText(10, 10, "Hello, MCH2022 badgePython!", display.BLUE, "roboto_regular18")
display.flush()

CHANNEL_COUNT = 4
sndmixer.begin(CHANNEL_COUNT)
channels = [Channel(i) for i in range(0, CHANNEL_COUNT)]
audio_started = False

row_tick = 0
row_index = 0


def tick(t):
    global audio_started
    if not audio_started:
        return

    global channels
    global row_tick
    global row_index

    if row_tick == 0:
        for chan in channels:
            chan.load_row(row_index)

    for chan in channels:
        chan.play_tick()

    row_tick += 1
    if row_tick == TEMPO:
        row_tick = 0
        row_index = (row_index + 1) % 16


timer = machine.Timer(0)
timer.init(period=20, callback=tick)


def on_action_btn(pressed):
    if pressed:
        display.drawText(20, 20, "beep", display.BLUE, "roboto_regular18")
        display.flush()

        global audio_started
        global channels
        if not audio_started:
            for chan in channels:
                chan.start()
            audio_started = True

buttons.attach(buttons.BTN_A, on_action_btn)
buttons.attach(buttons.BTN_B, lambda pressed: system.launcher())
