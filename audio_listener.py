import sounddevice as sd
import numpy as np
import queue
import sys

class AudioListener:
    def __init__(self, sample_rate=16000, block_size=16000):
        self.sample_rate = sample_rate
        self.block_size = block_size
        self.audio_queue = queue.Queue()
        self.stream = None

    def _audio_callback(self, indata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        self.audio_queue.put(indata.copy())

    def start(self):
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            callback=self._audio_callback,
            blocksize=self.block_size
        )
        self.stream.start()
        print("Listening...")

    def stop(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()

    def get_audio_block(self):
        return self.audio_queue.get()

if __name__ == "__main__":
    listener = AudioListener()
    listener.start()
    try:
        while True:
            block = listener.get_audio_block()
            print(f"Captured block of shape {block.shape}")
    except KeyboardInterrupt:
        listener.stop()
