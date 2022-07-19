import sndmixer

CHANNEL_COUNT = 4
ROW_COUNT = 16


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


class Sample:
    def __init__(self, waveform, volumes):
        self.waveform = waveform
        self.volumes = volumes

    def to_json(self):
        return {
            'waveform': self.waveform,
            'volumes': self.volumes,
        }

    @classmethod
    def from_json(cls, data):
        return cls(
            waveform=data['waveform'],
            volumes=data['volumes'],
        )


class Track:
    def __init__(self, samples, pattern, tempo):
        self.samples = samples
        self.pattern = pattern
        self.tempo = tempo

    def to_json(self):
        return {
            'samples': {
                str(i): sample.to_json() for (i, sample) in self.samples.items()
            },
            'pattern': [
                [list(row) for row in channel]
                for channel in self.pattern
            ],
            'tempo': self.tempo
        }

    @classmethod
    def from_json(cls, data):
        return cls(
            samples={
                int(i): Sample.from_json(sample) for (i, sample) in data['samples'].items()
            },
            pattern=[
                [tuple(row) for row in channel]
                for channel in data['pattern']
            ],
            tempo=data['tempo']
        )


class Channel:
    def __init__(self, index):
        self.index = index
        self.track = None
        self.id = sndmixer.synth()
        self.current_sample = None
        self.current_pitch = None
        self.sample_tick = 0

    def start(self):
        sndmixer.play(self.id)

    def stop(self):
        sndmixer.pause(self.id)

    def load_row(self, row_index):
        pitch, sample_number = self.track.pattern[self.index][row_index]
        if pitch is None:
            return

        self.sample_tick = 0
        self.current_pitch = pitch
        if sample_number != 0:
            self.current_sample = self.track.samples[sample_number]

    def play_tick(self):
        if self.current_sample is None or self.sample_tick >= 32:
            sndmixer.volume(self.id, 0)
        else:
            sndmixer.waveform(self.id, self.current_sample.waveform)
            sndmixer.freq(self.id, TONES[self.current_pitch])
            sndmixer.volume(self.id, self.current_sample.volumes[self.sample_tick])

        self.sample_tick += 1


class Player:
    def __init__(self):
        sndmixer.begin(CHANNEL_COUNT)
        self.channels = [Channel(i) for i in range(0, CHANNEL_COUNT)]
        self.is_started = False
        self.is_playing = False
        self.row_callbacks = []
        self.stop_callbacks = []

    def load_track(self, track):
        self.track = track
        for chan in self.channels:
            chan.track = track

    def start(self):
        self.row_tick = 0
        self.row_index = 0

        if not self.is_started:
            for chan in self.channels:
                chan.start()
            self.is_started = True

        self.is_playing = True

    def stop(self):
        for chan in self.channels:
            chan.stop()
        self.is_started = False
        self.is_playing = False

        for callback in self.stop_callbacks:
            callback()

    def on_play_row(self, callback):
        self.row_callbacks.append(callback)

    def on_stop(self, callback):
        self.stop_callbacks.append(callback)

    def tick(self):
        if not self.is_playing:
            return

        if self.row_tick == 0:
            for chan in self.channels:
                chan.load_row(self.row_index)

            for callback in self.row_callbacks:
                callback(self.row_index)

        for chan in self.channels:
            chan.play_tick()

        self.row_tick += 1
        if self.row_tick >= self.track.tempo:
            self.row_tick = 0
            self.row_index = (self.row_index + 1) % 16
