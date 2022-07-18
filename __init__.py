import display
import buttons
import machine
import system

from .player import Player, Sample, Track

WAVEFORM_SINE = 0
WAVEFORM_SQUARE = 1
WAVEFORM_TRIANGLE = 2
WAVEFORM_SAWTOOTH = 3
WAVEFORM_NOISE = 4


track = Track(
    samples={
        1: Sample(
            waveform=WAVEFORM_SQUARE,
            volumes=[15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ),
        2: Sample(
            waveform=WAVEFORM_SAWTOOTH,
            volumes=[15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ),
    },
    pattern=[
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
    ],
    tempo=5
)

player = Player()
player.load_track(track)


print("Hello, MCH2022 Badge!")

display.drawFill(display.WHITE)
display.drawText(10, 10, "Hello, MCH2022 badgePython!", display.BLUE, "roboto_regular18")
display.flush()


def tick(t):
    player.tick()


timer = machine.Timer(0)
timer.init(period=20, callback=tick)


def on_action_btn(pressed):
    if pressed:
        display.drawText(20, 20, "beep", display.BLUE, "roboto_regular18")
        display.flush()
        player.start()

buttons.attach(buttons.BTN_A, on_action_btn)
buttons.attach(buttons.BTN_B, lambda pressed: system.launcher())
