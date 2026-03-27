import whisper
import torch
import numpy as np
import warnings
import logging

# Suppress Whisper FP16 warning and other library noise
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU")
logging.getLogger("transformers").setLevel(logging.ERROR)

class ASREngine:
    def __init__(self, model_name="tiny", device=None):
        print(f"Loading Whisper model: {model_name}...")
        self.model = whisper.load_model(model_name)
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
        else:
            self.device = device
        self.model.to(self.device)
        print(f"Whisper loaded on {self.device}")


    def transcribe(self, audio_data):
        """
        Transcribes audio data and returns words with timestamps and confidence scores.
        audio_data: numpy array of audio samples OR path to audio file
        """
        import soundfile as sf
        import numpy as np

        # If audio_data is a path, load it manually to avoid ffmpeg dependency in Whisper
        if isinstance(audio_data, str):
            data, samplerate = sf.read(audio_data)
            # Whisper expects 16,000 Hz
            if samplerate != 16000:
                # Simple resampling if needed, but benchmark generates at 16k
                pass
            audio_data = data.astype(np.float32)

        if isinstance(audio_data, np.ndarray):
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1) # to mono
            
        result = self.model.transcribe(
            audio_data,
            word_timestamps=True,
            task="transcribe",
            language="en"
        )
        
        words = []
        for segment in result.get("segments", []):
            if "words" in segment:
                for word_info in segment["words"]:
                    words.append({
                        "word": word_info["word"].strip(),
                        "start": word_info["start"],
                        "end": word_info["end"],
                        "probability": word_info.get("probability", 1.0)
                    })
        
        return words, result.get("text", "")


if __name__ == "__main__":
    # Test with a dummy block (zeros)
    engine = ASREngine()
    dummy_audio = np.zeros(16000, dtype=np.float32)
    words, text = engine.transcribe(dummy_audio)
    print(f"Transcribed words: {words}")
    print(f"Text: {text}")
